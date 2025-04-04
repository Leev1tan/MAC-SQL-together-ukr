#!/usr/bin/env python
"""
Test script for evaluating the MAC-SQL agent on the Ukrainian BIRD dataset.
This script handles:
1. Loading Ukrainian BIRD questions
2. Running the agent to generate SQL for each question
3. Executing the generated SQL against PostgreSQL databases
4. Evaluating execution accuracy and timing metrics
"""

import os
import sys
import time
import json
import logging
import argparse
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
import traceback

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.bird_ukr_loader import (
    find_bird_ukr_data, 
    load_questions, 
    load_random_subset, 
    normalize_ukr_query
)
from utils.pg_connection import (
    init_connection_pool, 
    get_pool_connection, 
    return_connection, 
    close_connection_pool,
    close_all_connection_pools,
    execute_query as pg_execute_query
)
from utils.bird_ukr_tables_adapter import convert_tables_format, generate_compatible_tables_json
from core.enhanced_chat_manager import EnhancedChatManager as HighLevelChatManager

# Try to import agent flow tracking
try:
    from core.tracking import install_tracker, get_tracker, clear_flow, MessageTracker
    from core.visualization import visualize_agent_flow, print_agent_flow
    # Try to import serialization utilities
    try:
        from core.utils.serialization import safe_serialize_message
    except ImportError:
        # Define a fallback serialization function
        def safe_serialize_message(message):
            """Create a safe copy of the message without circular references."""
            if message is None:
                return {}
            
            if isinstance(message, dict):
                # Make a copy so we don't modify the original
                result = {}
                for k, v in message.items():
                    if k not in ["agent_instance", "trace_history"]:
                        if v is None:
                            result[k] = None
                        elif isinstance(v, (str, int, float, bool)):
                            result[k] = v
                        elif isinstance(v, (list, dict)):
                            # Convert complex objects to strings
                            try:
                                import json
                                result[k] = json.dumps(v)
                            except:
                                result[k] = str(v)
                        else:
                            # Other objects just convert to string
                            result[k] = str(v)
                return result
            return str(message)
    
    # Make sure we have a tracker instance
    flow_tracker = get_tracker()
    HAS_AGENT_FLOW = True
except ImportError:
    HAS_AGENT_FLOW = False
    
    # Create a simple mock tracker for fallback
    class MockTracker:
        def __init__(self):
            self.messages = []
            self.current_session_id = None
            
        def get_messages(self):
            return self.messages
            
        def clear(self):
            self.messages = []
            
        def track_message(self, **kwargs):
            msg = kwargs
            self.messages.append(msg)
            return "mock-id"
            
    flow_tracker = MockTracker()
    
    def install_tracker(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    def install_flow_tracker(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    def print_agent_flow(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    def visualize_agent_flow(*args, **kwargs):
        print("Agent flow visualization not available.")
    
    def clear_flow(*args, **kwargs):
        print("Agent flow tracking not available.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load .env file first, force override, and check result
load_result = load_dotenv(override=True)
print(f"load_dotenv result (found file?): {load_result}")
print(f"TOGETHER_MODEL after load_dotenv: {os.environ.get('TOGETHER_MODEL')}")

# Early parse for --model argument ONLY
early_parser = argparse.ArgumentParser(add_help=False) # Prevent conflict with later full parse
early_parser.add_argument("--model", type=str, help="Override TOGETHER_MODEL env var")
early_args, _ = early_parser.parse_known_args()

# Set TOGETHER_MODEL env var if --model is provided, otherwise keep loaded value
if early_args.model:
    os.environ["TOGETHER_MODEL"] = early_args.model
    print(f"Overriding TOGETHER_MODEL with --model arg: {early_args.model}")
else:
    print(f"Using TOGETHER_MODEL from environment: {os.getenv('TOGETHER_MODEL')}")

class UkrainianBirdAdapter:
    """
    Adapter class to connect MAC-SQL with Ukrainian BIRD dataset.
    This provides a consistent interface matching other adapters.
    """
    
    def __init__(
        self, 
        data_path: str,
        tables_path: str,
        model_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the adapter with paths to data and configuration.
        
        Args:
            data_path: Path to the BIRD-UKR dataset
            tables_path: Path to the tables.json file
            model_name: Model name to use for the agent
        """
        from core.enhanced_chat_manager import EnhancedChatManager
        from core.const import ENGINE_TOGETHER
        from core.macsql_together_adapter import configure_together_rate_limits, patch_api_func, TogetherAIAdapter
        
        # Set Together API parameters
        together_api_key = os.environ.get("TOGETHER_API_KEY", "")
        together_model = os.environ.get("TOGETHER_MODEL", ENGINE_TOGETHER)
        
        # Configure rate limiting
        configure_together_rate_limits()
        
        # Initialize TogetherAI adapter
        try:
            adapter = TogetherAIAdapter()
            logger.info(f"Initialized TogetherAIAdapter")
            
            # Patch API functions to use Together
            patch_api_func()
            logger.info(f"Patched API functions to use Together")
        except Exception as e:
            logger.warning(f"Error initializing TogetherAIAdapter: {e}")
        
        # Get log path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join("logs", "bird_ukr", timestamp)
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "log.txt")
        
        # Initialize the chat manager with BIRD-UKR dataset - it will use our custom agents
        self.chat_manager = EnhancedChatManager(
            data_path=data_path,
            tables_json_path=tables_path,
            log_path=log_path,
            model_name=model_name or together_model,
            dataset_name="bird-ukr"  # This will trigger using our custom PostgreSQL agents
        )
        
        # Track initialization parameters
        self.data_path = data_path
        self.tables_path = tables_path
        
        # Debug settings
        self.debug_mode = kwargs.get("debug_mode", False)
        
        # Install agent flow tracker if available
        if HAS_AGENT_FLOW:
            install_tracker(self.chat_manager)
            logger.info("Agent flow tracking enabled")
    
    def run(self, db_id: str, query: str, evidence: str = "", ground_truth: str = ""):
        """
        Run the MAC-SQL agent on a single query.
        
        Args:
            db_id: Database ID 
            query: Question text
            evidence: Additional evidence or context
            ground_truth: Ground truth SQL (for evaluation)
            
        Returns:
            Dictionary with results
        """
        # Prepare message for the chat manager - IMPORTANT: Don't include ground_truth to avoid data leakage
        message = {
            "db_id": db_id,
            "query": query,
            "question": query,  # Add question key for compatibility with pg_selector.py
            "evidence": evidence,
            "send_to": "Selector"  # Start with the Selector agent
        }
        
        # Process through chat manager
        self.chat_manager.start(message)
        
        # Get the predicted SQL
        pred_sql = message.get("pred", "")
        
        # Execute both ground truth and predicted SQL (if available)
        gold_time = 0
        pred_time = 0
        execution_match = False
        
        if pred_sql and ground_truth:
            # Validate against ground truth
            conn = get_pool_connection(db_id)
            if conn:
                try:
                    # Execute ground truth
                    start_time = time.time()
                    cursor_gold = conn.cursor()
                    cursor_gold.execute(ground_truth)
                    gold_results = cursor_gold.fetchall()
                    gold_time = time.time() - start_time
                    cursor_gold.close()
                    
                    # Execute predicted SQL
                    start_time = time.time()
                    cursor_pred = conn.cursor()
                    cursor_pred.execute(pred_sql)
                    pred_results = cursor_pred.fetchall()
                    pred_time = time.time() - start_time
                    cursor_pred.close()
                    
                    # Compare results
                    execution_match = compare_results(gold_results, pred_results)
                    message["execution_match"] = execution_match
                    
                except Exception as e:
                    logger.error(f"Error executing SQL: {e}")
                    message["execution_error"] = str(e)
                    
                finally:
                    # Return connection to the pool
                    return_connection(db_id, conn)
        
        # Add timing information
        message["gold_time"] = gold_time
        message["pred_time"] = pred_time
        
        # Get exact match (if we have both predicted and ground truth)
        if pred_sql and ground_truth:
            normalized_pred = normalize_sql(pred_sql)
            normalized_gold = normalize_sql(ground_truth)
            message["exact_match"] = normalized_pred == normalized_gold
        else:
            message["exact_match"] = False
        
        # Store gold SQL in result for reference (but it wasn't used during prediction)
        message["gold_sql"] = ground_truth
        
        return message

def get_database_path(data_path, db_id):
    """
    For PostgreSQL databases, we just return the database ID as the "path".
    Since this is used for connection, not a physical path.
    
    Args:
        data_path: Path to the data directory
        db_id: The database identifier
    
    Returns:
        The database identifier itself
    """
    return db_id

def get_agent(data_path, model_name, tables_json_path, cache_dir=None, dataset_name="bird-ukr"):
    """
    Get a MAC-SQL agent instance for evaluation.
    
    Args:
        data_path: Path to the dataset
        model_name: Name of the model to use
        tables_json_path: Path to the tables.json file
        cache_dir: Cache directory for API responses
        dataset_name: Name of the dataset
        
    Returns:
        MAC-SQL agent instance
    """
    # Create UkrainianBirdAdapter
    agent = UkrainianBirdAdapter(
        data_path=data_path,
        tables_path=tables_json_path,
        model_name=model_name,
        debug_mode=True
    )
    
    return agent

def os_path_exists_or_pg_db(path):
    """
    Custom function to check if a path exists on the filesystem
    or if it's a PostgreSQL database ID (which doesn't need to exist as a path).
    
    Args:
        path: The path or database ID to check
        
    Returns:
        True if the path exists or it's likely a PostgreSQL database ID
    """
    # For PostgreSQL databases in this project, we assume they're valid
    # This is a workaround since we can't check PostgreSQL database existence the same way
    return True

def test_single_query(
    agent,
    args,
    query_id,
    question,
    db_id,
    tables_json_path,
    gold_query="",
    gold_result=None,
    logger=None,
) -> Dict[str, Any]:
    """
    Test a single query using the MAC-SQL agent.
    
    Args:
        agent: The MAC-SQL agent
        args: Command-line arguments
        query_id: The ID of the query
        question: The question to be answered
        db_id: The ID of the database
        tables_json_path: Path to the tables.json file
        gold_query: The gold SQL query, if available
        gold_result: The gold result, if available
        logger: The logger to use
        
    Returns:
        Results for the single query
    """
    # If logger is not provided, use the default logger
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Log information about the query
    logger.info(f"Testing query {query_id} on database {db_id}")
    
    # Get the database path
    db_path = get_database_path(args.data_path, db_id)
    
    # Initialize result dictionary
    result_info = {
        "question_id": question.get("question_id", "unknown"),
        "db_id": db_id,
        "question": question.get("question", ""),
        "gold_sql": gold_query,
        "difficulty": question.get("difficulty", ""),
        "execution_match": False,
        "gold_time": None,
        "pred_time": None,
        "gold_result": None,
        "pred_result": None,
        "agent_time": None,
        "agent_messages": None,
        "error": None
    }
    
    # Skip if no question text or database ID
    if not question.get("question") or not db_id:
        logger.warning(f"Skipping question {query_id}: Missing question text or database ID")
        result_info["error"] = "Missing question text or database ID"
        return result_info
    
    # For PostgreSQL databases, we don't need to check if the path exists as a file
    if not os_path_exists_or_pg_db(db_path):
        logger.warning(f"Skipping question {query_id}: Database path not found: {db_path}")
        result_info["error"] = f"Database path not found: {db_path}"
        return result_info
    
    try:
        # Ensure connection pool is initialized for this DB
        init_connection_pool(db_id)
        
        # Start the agent process
        agent.start(question)

        # Get final predicted SQL
        pred_sql = question.get('pred', '').strip()
        final_sql = question.get('final_sql', '').strip()
        if not pred_sql and final_sql:
            pred_sql = final_sql
            
        # --- Execute Gold SQL --- 
        gold_success, gold_db_result, gold_time = pg_execute_query(db_id, gold_query)
        result_info['gold_time'] = gold_time
        if not gold_success:
            result_info['gold_error'] = str(gold_db_result)
            logger.warning(f"Gold SQL failed for {query_id}: {gold_db_result}")
            # Even if gold fails, proceed to execute predicted SQL for debugging
            
        # --- Execute Predicted SQL --- 
        pred_success, pred_db_result, pred_time = False, None, 0
        if pred_sql:
            pred_success, pred_db_result, pred_time = pg_execute_query(db_id, pred_sql)
            result_info['pred_time'] = pred_time
            if not pred_success:
                result_info['pred_error'] = str(pred_db_result)
                logger.warning(f"Predicted SQL failed for {query_id}: {pred_db_result}")
        else:
            result_info['pred_error'] = "No SQL query generated."
            logger.warning(f"No SQL generated for {query_id}")
            
        # --- Compare Results --- 
        execution_match = False
        if gold_success and pred_success:
            # Use the local compare_results function
            execution_match = compare_results(gold_db_result, pred_db_result)
            result_info['execution_match'] = execution_match
            if execution_match:
                logger.info("Execution MATCH ✓")
            else:
                logger.info("Execution MISMATCH ✗")
                # Log mismatch details for debugging
                logger.debug(f"Gold Result ({len(gold_db_result)} rows): {gold_db_result[:5]}") # Show first 5 rows
                logger.debug(f"Pred Result ({len(pred_db_result)} rows): {pred_db_result[:5]}") # Show first 5 rows
        elif gold_success and not pred_success:
            logger.info("Execution MISMATCH ✗ (Prediction failed)")
            result_info['execution_match'] = False
        elif not gold_success and pred_success:
             logger.info("Execution MISMATCH ✗ (Gold failed)")
             result_info['execution_match'] = False
        else: # Both failed
             logger.info("Execution MISMATCH ✗ (Both failed)")
             result_info['execution_match'] = False # Treat as mismatch if both failed

        # --- Calculate Exact Match (if applicable) ---
        if gold_query and pred_sql:
            normalized_pred = normalize_sql(pred_sql)
            normalized_gold = normalize_sql(gold_query)
            result_info["exact_match"] = normalized_pred == normalized_gold
        else:
            result_info["exact_match"] = False
        
        # Save gold SQL in result for reference (but it wasn't used during prediction)
        result_info["gold_sql"] = gold_query
        
    except Exception as e:
        logger.exception(f"Error processing query {query_id}: {e}")
        result_info['error'] = str(e)
        
    finally:
        # Ensure connection pool is closed for this DB if it exists
        # Note: closing after every query might be inefficient, 
        # consider closing pools at the end of the script instead.
        # close_connection_pool(db_id) 
        pass
        
    # Update result info with final details
    result_info['pred_sql'] = pred_sql
    result_info['status'] = 'Success' if 'error' not in result_info else 'Failed'
    
    return result_info

def test_agent_subset(agent, args):
    """
    Test a subset of questions on the BIRD-UKR dataset using the provided agent.
    
    Args:
        agent: MAC-SQL agent adapter
        args: Command-line arguments
        
    Returns:
        Results of the evaluation
    """
    # Get data path
    data_path = args.data_path
    
    # Get tables.json path
    tables_json_path = get_tables_json_path(data_path)
    
    # Load questions based on arguments
    if args.random:
        # Load random questions
        questions = load_random_subset(
            data_path=data_path,
            num_samples=args.num_samples,
            random_seed=args.seed
        )
    else:
        # Load sequential questions
        questions_path = os.path.join(data_path, "questions.json")
        questions = load_questions(questions_path, limit=args.num_samples)
    
    # Test the questions
    return test_agent_subset_questions(questions, tables_json_path, args, agent)

def test_agent_subset_questions(
    questions: List[Dict[str, Any]],
    tables_json_path: str,
    args,
    agent
) -> List[Dict[str, Any]]:
    """
    Test a subset of questions using the MAC-SQL agent.
    
    Args:
        questions: List of questions to test
        tables_json_path: Path to the tables.json file
        args: Command line arguments
        agent: MAC-SQL agent instance
        
    Returns:
        List of test results
    """
    # Create logger
    logger = logging.getLogger(__name__)
    
    # Collect unique database IDs from questions
    db_ids = set(q.get("db_id") for q in questions if q.get("db_id"))
    logger.info(f"Initializing connection pools for {len(db_ids)} databases...")
    
    # Initialize PostgreSQL connection pools for each database
    for db_id in db_ids:
        try:
            # Initialize pool for the database
            init_connection_pool(db_id)
            logger.info(f"Initialized pool for database: {db_id}")
        except Exception as e:
            logger.error(f"Error initializing pool for database {db_id}: {e}")
    
    # Test all questions
    results = []
    try:
        # Process each question
        for i, question in enumerate(questions):
            # Get the database ID
            db_id = question.get("db_id")
            if not db_id:
                logger.warning(f"Skipping question {i+1}: No database ID")
                continue
                
            # Test the query
            result = test_single_query(
                agent=agent,
                args=args,
                query_id=question.get("question_id", f"q{i+1}"),
                question=question,
                db_id=db_id,
                tables_json_path=tables_json_path,
                gold_query=question.get("gold_sql", ""),
                gold_result=None,
                logger=logger
            )
            
            # Add result to list
            results.append(result)
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
    finally:
        # Close all connection pools
        for db_id in db_ids:
            try:
                close_connection_pool(db_id)
            except Exception as e:
                logger.error(f"Error closing pool for database {db_id}: {e}")
    
    return results

def save_results(results, args, execution_accuracy, avg_gold_time, avg_pred_time):
    """
    Save test results to a JSON file.
    
    Args:
        results: List of test results
        args: Command-line arguments
        execution_accuracy: Execution accuracy
        avg_gold_time: Average gold SQL execution time
        avg_pred_time: Average predicted SQL execution time
    """
    logger = logging.getLogger(__name__)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create results dictionary
    output_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": args.model,
        "dataset": "bird-ukr",
        "execution_accuracy": execution_accuracy,
        "num_samples": len(results),
        "random_seed": args.seed if args.random else None,
        "avg_gold_time": avg_gold_time,
        "avg_pred_time": avg_pred_time,
        "results": results
    }
    
    # Save results to file
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Results saved to {args.output}")

def parse_arguments():
    """
    Parse command-line arguments for the evaluation script.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Evaluate MAC-SQL on Ukrainian BIRD dataset")
    
    # Dataset parameters
    parser.add_argument("--data-path", type=str, default="./bird-ukr",
                        help="Path to the BIRD-UKR dataset")
    parser.add_argument("--random", action="store_true",
                        help="Randomly sample questions instead of selecting sequentially")
    parser.add_argument("--num-samples", type=int, default=10,
                        help="Number of samples to test")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for sampling")
    
    # Model parameters
    parser.add_argument("--model", type=str, default=os.environ.get("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
                        help="Model name to use")
    parser.add_argument("--cache-dir", type=str, default=None,
                        help="Directory to cache API responses")
    
    # Output parameters
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save results JSON")
    parser.add_argument("--verbose", "-v", action="count", default=0,
                        help="Verbosity level (add multiple times for more verbosity)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode")
    
    # Execution parameters
    parser.add_argument("--force-execution", action="store_true",
                        help="Force execution even if gold SQL is not available")
    parser.add_argument("--delay", type=float, default=0,
                        help="Delay between queries (in seconds)")
    
    # Visualization parameters
    parser.add_argument("--visualize", action="store_true",
                        help="Generate visualization of agent flow")
    parser.add_argument("--viz-format", type=str, default="png",
                        choices=["png", "svg", "pdf"],
                        help="Format for visualization output")
    parser.add_argument("--viz-output", type=str, default="agent_flow.png",
                        help="Path for visualization output")
    
    return parser.parse_args()

def main():
    """
    Main function for evaluating MAC-SQL Agents on BIRD-UKR dataset.
    """
    # Use the regular full parser here
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args)
    
    # Log start message and model being used
    logger.info("Starting BIRD-UKR evaluation...")
    logger.info(f"Using model (from env): {os.getenv('TOGETHER_MODEL', 'Not Set')}") 
    
    # Get tables.json path
    tables_json_path = get_tables_json_path(args.data_path)
    logger.info(f"Using converted tables.json: {tables_json_path}")
    
    # Load environment variables
    load_env()
    
    # Configure debugging if enabled
    configure_debug()
    
    # Initialize the MAC-SQL agent
    agent = get_agent(
        data_path=args.data_path,
        model_name=args.model,
        tables_json_path=tables_json_path,
        cache_dir=args.cache_dir,
        dataset_name="bird-ukr",
    )
    
    # Test the agent on a subset of questions
    try:
        results = test_agent_subset(agent, args)
        
        # Calculate and log summary
        num_matches = sum(1 for r in results if r.get("execution_match", False))
        execution_accuracy = num_matches / len(results) if results else 0
        
        # Calculate average execution times (only for successful executions)
        gold_times = [r.get("gold_time", 0) for r in results if r.get("gold_time") is not None]
        pred_times = [r.get("pred_time", 0) for r in results if r.get("pred_time") is not None]
        
        avg_gold_time = sum(gold_times) / len(gold_times) if gold_times else 0
        avg_pred_time = sum(pred_times) / len(pred_times) if pred_times else 0
        
        # Log summary
        logger.info("=" * 50)
        logger.info(f"Test summary:")
        logger.info(f"Total queries: {len(results)}")
        logger.info(f"Execution matches: {num_matches}")
        logger.info(f"Execution accuracy: {execution_accuracy:.4f}")
        logger.info(f"Average gold SQL time: {avg_gold_time:.4f}s")
        logger.info(f"Average pred SQL time: {avg_pred_time:.4f}s")
        logger.info("=" * 50)
        
        # Save results if specified
        if args.output:
            save_results(results, args, execution_accuracy, avg_gold_time, avg_pred_time)
            
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
    finally:
        # Clean up any remaining resources
        close_all_pools()

def compare_results(gold_results, pred_results):
    """
    Compare two sets of SQL execution results for equivalence.
    
    Args:
        gold_results: Results from the gold/ground truth SQL
        pred_results: Results from the predicted SQL
        
    Returns:
        True if the results are equivalent, False otherwise
    """
    # Special case: both empty
    if not gold_results and not pred_results:
        logger.info("Both result sets are empty - match!")
        return True
        
    # Special case: different length
    if len(gold_results) != len(pred_results):
        logger.warning(f"Result length mismatch: gold={len(gold_results)}, pred={len(pred_results)}")
        return False
    
    # For PostgreSQL results with RealDictRow objects
    if len(gold_results) > 0 and hasattr(gold_results[0], 'items'):
        logger.info("Comparing RealDictRow results")
        
        # Convert to comparable forms (ordered tuples of values)
        try:
            # Extract values and sort them for each row
            gold_values = [tuple(sorted(row.values())) for row in gold_results]
            pred_values = [tuple(sorted(row.values())) for row in pred_results]
            
            # Sort the value tuples to normalize order
            gold_values.sort()
            pred_values.sort()
            
            logger.info(f"Gold values: {gold_values}")
            logger.info(f"Pred values: {pred_values}")
            
            # Direct comparison
            return gold_values == pred_values
        except Exception as e:
            logger.error(f"Error comparing RealDictRow results: {e}")
            
            # Fallback - try direct comparison
            gold_str = str(gold_results)
            pred_str = str(pred_results)
            logger.info(f"Falling back to string comparison: {gold_str == pred_str}")
            return gold_str == pred_str
    
    # Convert all results to sets for comparison
    if len(gold_results) > 0:
        # Check if results are in tuple format
        if isinstance(gold_results[0], tuple) and isinstance(pred_results[0], tuple):
            gold_set = set(gold_results)
            pred_set = set(pred_results)
            return gold_set == pred_set
        
        # Handle RealDictCursor results (PostgreSQL)
        if isinstance(gold_results[0], dict) and isinstance(pred_results[0], dict):
            # Extract values only for comparison, ignore column names/order
            gold_values = [tuple(sorted(row.values())) for row in gold_results]
            pred_values = [tuple(sorted(row.values())) for row in pred_results]
            
            # Convert to sets for unordered comparison
            gold_set = set(gold_values)
            pred_set = set(pred_values)
            
            logger.info(f"Gold values: {gold_set}")
            logger.info(f"Pred values: {pred_set}")
            
            return gold_set == pred_set
        
        # Results might be dictionaries or complex objects
        # Try to convert to comparable types
        try:
            # Sort results by first column as a simple normalization
            # This works for most cases but might need refinement
            normalized_gold = sorted([tuple(row) for row in gold_results])
            normalized_pred = sorted([tuple(row) for row in pred_results])
            return normalized_gold == normalized_pred
        except Exception as e:
            logger.error(f"Error comparing results: {e}")
            
            # Fallback: serialize and compare
            # This is inefficient but should work as a last resort
            try:
                gold_json = json.dumps(gold_results, sort_keys=True)
                pred_json = json.dumps(pred_results, sort_keys=True)
                return gold_json == pred_json
            except Exception as e:
                logger.error(f"Error comparing serialized results: {e}")
                return False
    
    return False

def get_tables_json_path(data_path: str) -> str:
    """
    Get the path to the MAC-SQL compatible tables.json file.
    If the compatible file doesn't exist, create it.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        
    Returns:
        Path to the compatible tables.json file
    """
    # Check for original tables.json
    original_tables_path = os.path.join(data_path, "tables.json")
    if not os.path.exists(original_tables_path):
        raise FileNotFoundError(f"tables.json not found at {original_tables_path}")
    
    # Convert tables.json to MAC-SQL compatible format
    logger.info("Converting tables.json to MAC-SQL compatible format...")
    converted_path = generate_compatible_tables_json(data_path)
    logger.info(f"Using converted tables.json: {converted_path}")
    
    return converted_path

def close_all_pools():
    """
    Close all PostgreSQL connection pools
    """
    logger = logging.getLogger(__name__)
    logger.info("Closing all connection pools")
    
    close_all_connection_pools()
    
    logger.info("All connection pools closed")

def load_env():
    """
    Load environment variables from .env file
    """
    logger = logging.getLogger(__name__)
    logger.info("Loading .env file from current directory...")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API key is set
    api_key = os.environ.get("TOGETHER_API_KEY", "")
    api_key_exists = bool(api_key)
    api_key_length = len(api_key) if api_key_exists else 0
    
    logger.info(f"Loaded .env file successfully")
    logger.info(f"API Key (exists): {'Yes' if api_key_exists else 'No'}")
    logger.info(f"API Key (length): {api_key_length} characters")
    logger.info(f"Model: {os.environ.get('MODEL_NAME', 'Not set')}")
    
def configure_debug():
    """
    Configure debug mode from environment variables
    """
    logger = logging.getLogger(__name__)
    
    # Import debug module
    try:
        from core.debug_llm import is_debug_enabled
        # Check if it's a function or a variable
        if callable(is_debug_enabled):
            debug_enabled = is_debug_enabled()
        else:
            debug_enabled = is_debug_enabled
            
        if debug_enabled:
            logger.info("Debug mode enabled")
        else:
            logger.info("Debug mode disabled")
    except ImportError:
        logger.warning("Debug module not available")
    except Exception as e:
        logger.warning(f"Error configuring debug mode: {str(e)}")

def setup_logging(args):
    """
    Set up logging configuration.
    
    Args:
        args: Command-line arguments
    """
    # Set up logging format
    log_format = '%(levelname)s:%(name)s:%(message)s'
    
    # Set log level based on verbosity
    if args.verbose == 0:
        log_level = logging.INFO
    elif args.verbose == 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.DEBUG
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format
    )
    
    # Reduce verbosity of some libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

def normalize_sql(sql):
    """
    Normalize SQL query for comparison.
    Following scientific definition: treats clauses as sets and ignores literal values.
    
    Args:
        sql: SQL query string
        
    Returns:
        Normalized SQL string
    """
    # Remove comments
    sql = re.sub(r'--.*', ' ', sql)
    
    # Convert to lowercase
    sql = sql.lower()
    
    # Remove all string literals (replace with placeholder)
    sql = re.sub(r"'[^']*'", "'VALUE'", sql)
    
    # Remove all number literals
    sql = re.sub(r"\b\d+\b", "NUMBER", sql)
    
    # Remove extra whitespace
    sql = re.sub(r'\s+', ' ', sql)
    sql = sql.strip()
    
    # Remove trailing semicolon
    sql = sql.rstrip(';')
    
    # Remove backticks, quotes around identifiers
    sql = sql.replace("`", "").replace("\"", "")
    
    # Standardize aliases completely by removing numbers
    # Replace table aliases like t1, t2 with just "t"
    sql = re.sub(r'\b([a-z])(\d+)\b', r'\1', sql, flags=re.IGNORECASE)
    
    # Remove "AS" keyword in aliases
    sql = re.sub(r'\s+as\s+([a-z0-9_]+)', r' \1', sql, flags=re.IGNORECASE)
    
    # Normalize whitespace around operators
    sql = re.sub(r'\s*=\s*', '=', sql)
    sql = re.sub(r'\s*<>\s*', '!=', sql)
    sql = re.sub(r'\s*!=\s*', '!=', sql)
    
    # Normalize WHERE/AND/OR clauses
    sql = re.sub(r'where\s+and', 'where', sql)
    
    # Normalize commas
    sql = re.sub(r'\s*,\s*', ', ', sql)
    
    return sql

if __name__ == "__main__":
    main() 