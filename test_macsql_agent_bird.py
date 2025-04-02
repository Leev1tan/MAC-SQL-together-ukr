#!/usr/bin/env python
"""
Test script for MAC-SQL with Together AI using the agent-based architecture on the BIRD dataset.
"""

import os
import sys
import json
import argparse
import logging
import sqlite3
from pathlib import Path
import random
from pprint import pprint
from dotenv import load_dotenv
from core.enhanced_chat_manager import EnhancedChatManager
from core.macsql_together_adapter import TogetherAIAdapter, patch_api_func, configure_together_rate_limits
from core.bird_extensions import load_bird_subset
from core.const import ENGINE_TOGETHER
from typing import List, Dict, Any, Optional
import copy
import types
from datetime import datetime

# Add imports for agent flow tracking and visualization
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
        
    # Define a thorough fallback serialization function
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

# Try to import pretty debug utilities
try:
    from core.debug_pretty import Colors, print_agent_header, print_schema_preview, print_sql
    HAS_PRETTY_DEBUG = True
except ImportError:
    HAS_PRETTY_DEBUG = False
    # Define fallback color class
    class Colors:
        PURPLE = ''
        BLUE = ''
        CYAN = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        BOLD = ''
        UNDERLINE = ''
        END = ''

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", ENGINE_TOGETHER)

def find_bird_data():
    """Find the BIRD dataset directory."""
    # First check environment variable
    env_path = os.getenv("BIRD_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Found BIRD data directory from environment variable: {env_path}")
        return str(env_path)
    
    # If no environment variable, check standard locations
    possible_paths = [
        Path("data/bird"),
        Path("MAC-SQL/data/bird"),
        Path("../MAC-SQL/data/bird"),
        Path("./data/bird"),
        Path("./MAC-SQL/data/bird"),
        Path("data/minidev/MINIDEV"),  # Additional BIRD-specific path
        Path("MAC-SQL/data/minidev/MINIDEV"),  # Additional BIRD-specific path
    ]
    
    for path in possible_paths:
        if path.exists():
            # Verify dataset files and database directory
            dataset_files_exist = (
                (path / "dev.json").exists() or 
                (path / "mini_dev.json").exists() or
                (path / "mini_dev_sqlite.json").exists()  # For BIRD
            )
            db_dir_exists = (
                (path / "database").exists() or  # Spider format
                (path / "dev_databases").exists()  # BIRD format
            )
            
            if dataset_files_exist and db_dir_exists:
                logger.info(f"Found BIRD data directory at: {path}")
                return str(path)
    
    raise FileNotFoundError("BIRD dataset directory not found. Please place it in data/bird or MAC-SQL/data/bird or set the BIRD_PATH environment variable.")

def get_bird_db_path(bird_path: str) -> str:
    """Returns the path to the database directory within the BIRD dataset"""
    # BIRD uses "dev_databases" instead of "database"
    db_path = os.path.join(bird_path, "dev_databases")
    if os.path.exists(db_path):
        return db_path
    
    # Fall back to "database" if "dev_databases" doesn't exist
    db_path = os.path.join(bird_path, "database")
    if os.path.exists(db_path):
        return db_path
    
    # If neither exists, return the path that would be expected
    return os.path.join(bird_path, "dev_databases")

def get_bird_tables_path(bird_path):
    """Find the tables.json file for BIRD dataset."""
    # First check environment variable
    env_path = os.getenv("BIRD_TABLES_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Using tables.json from environment variable: {env_path}")
        return env_path
    
    # Check standard locations
    tables_paths = [
        os.path.join(bird_path, "tables.json"),
        os.path.join(bird_path, "dev_tables.json")
    ]
    
    for path in tables_paths:
        if os.path.exists(path):
            logger.info(f"Found tables.json at: {path}")
            return path
    
    # If not found, return the default path and let the EnhancedChatManager handle the error
    return os.path.join(bird_path, "tables.json")

def load_bird_queries(path, num_samples=5):
    """Load a subset of BIRD queries."""
    # Determine which file to load from
    # BIRD has different file names than Spider
    dev_paths = [
        os.path.join(path, "dev.json"),
        os.path.join(path, "mini_dev.json"),
        os.path.join(path, "mini_dev_sqlite.json")
    ]
    
    data_file = None
    for dev_path in dev_paths:
        if os.path.exists(dev_path):
            data_file = dev_path
            break
    
    if not data_file:
        logger.error(f"No BIRD dataset file found in {path}")
        raise FileNotFoundError(f"No BIRD dataset file found in {path}")
    
    logger.info(f"Loading BIRD queries from {data_file}")
    
    # Use the bird_extensions function to load the queries
    return load_bird_subset(data_file, num_samples)

def print_db_tables(db_id, db_path):
    """Print the actual database tables for a given database."""
    try:
        # Make sure db_path points to the database directory
        if not os.path.basename(db_path).startswith("database") and not os.path.basename(db_path).startswith("dev_databases"):
            # Check if it's a BIRD database path
            bird_db_path = os.path.join(db_path, "dev_databases")
            if os.path.exists(bird_db_path):
                db_path = bird_db_path
            else:
                db_path = os.path.join(db_path, "database")
        
        # Find database file
        db_file = os.path.join(db_path, db_id, f"{db_id}.sqlite")
        if not os.path.exists(db_file):
            logger.error(f"Database file not found: {db_file}")
            print(f"  Error: Database file '{db_file}' not found")
            return
        
        if HAS_PRETTY_DEBUG:
            print(f"\n{Colors.BOLD}{Colors.GREEN}DATABASE SCHEMA: {db_id}{Colors.END}")
        else:
            print(f"\nActual tables in {db_id}:")
        
        # Connect to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if HAS_PRETTY_DEBUG:
                print(f"\n{Colors.BLUE}Table: {table_name}{Colors.END}")
            else:
                print(f"\nTable: {table_name}")
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                
                if is_pk:
                    if HAS_PRETTY_DEBUG:
                        print(f"  {Colors.BOLD}{col_name}{Colors.END} ({col_type}) PRIMARY KEY")
                    else:
                        print(f"  {col_name} ({col_type}) PRIMARY KEY")
                else:
                    print(f"  {col_name} ({col_type})")
                    
        # Get foreign keys if supported
        try:
            has_foreign_keys = False
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA foreign_key_list({table_name});")
                foreign_keys = cursor.fetchall()
                
                if foreign_keys:
                    if not has_foreign_keys:
                        if HAS_PRETTY_DEBUG:
                            print(f"\n{Colors.PURPLE}Foreign Keys:{Colors.END}")
                        else:
                            print("\nForeign Keys:")
                        has_foreign_keys = True
                    
                    for fk in foreign_keys:
                        _, _, ref_table, from_col, to_col, _, _, _ = fk
                        if HAS_PRETTY_DEBUG:
                            print(f"  {table_name}.{from_col} → {ref_table}.{to_col}")
                        else:
                            print(f"  {table_name}.{from_col} → {ref_table}.{to_col}")
                            
        except Exception as e:
            pass  # Some SQLite versions don't support foreign_key_list
            
        conn.close()
    except Exception as e:
        logger.error(f"Error printing database tables: {e}")
        print(f"  Error: {str(e)}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test MAC-SQL agents on BIRD dataset.")
    parser.add_argument("--samples", type=int, default=5, help="Number of sample queries to test.")
    parser.add_argument("--visualize", action="store_true", help="Visualize agent flow.")
    parser.add_argument("--viz-format", type=str, default="html", choices=["html", "json", "mermaid"], help="Visualization format")
    parser.add_argument("--viz-output", type=str, default=None, help="Path to save visualization output")
    parser.add_argument("--output", type=str, default=None, help="Path to save test results as JSON")
    parser.add_argument("--full-trace", action="store_true", help="Include full message trace in output")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    return parser.parse_args()

def test_single_query(db_id, question, gold_sql=None, evidence=None, args=None):
    """Test a single query using the MAC-SQL agent pipeline."""
    bird_path = find_bird_data()
    db_path = get_bird_db_path(bird_path)
    tables_path = get_bird_tables_path(bird_path)
    
    # Create chat manager
    chat_manager = EnhancedChatManager(
        data_path=db_path,
        tables_json_path=tables_path,  # Use the found tables.json path
        log_path="logs/agent_test_bird.log",
        model_name=TOGETHER_MODEL,
        dataset_name="bird",  # Use the BIRD configuration
        lazy_loading=False,  # For testing, disable lazy loading
        use_enhanced_agents=True,  # Use enhanced agents
        debug_mode=True  # Enable debug mode for testing
    )
    
    # Setup agent flow tracking if available
    if args and args.visualize and HAS_AGENT_FLOW:
        # Reset the flow for this test
        clear_flow()
        
        # Install the flow tracker
        try:
            # First try to use the latest tracking code
            install_tracker(chat_manager)
        except:
            # Fall back to the older installation method
            install_flow_tracker(chat_manager)
        
        # Monkey patch chat_manager._chat_single_round to track messages
        original_chat_single_round = chat_manager._chat_single_round
        
        def tracked_chat_single_round(self, message):
            """Wrap the original method to track messages before and after."""
            # Safely copy the message to avoid tracking massive objects
            message_before = safe_serialize_message(copy.deepcopy(message))
            
            # Track the message before processing
            flow_tracker.track_message(
                from_agent=message_before.get("send_from", "System"),
                to_agent=message_before.get("send_to", "Unknown"),
                action="process_message",
                data={
                    "message_type": "before",
                    "query": message_before.get("query", ""),
                    "db_id": message_before.get("db_id", ""),
                    "step": message_before.get("step", "")
                },
                raw_message=message_before if args.full_trace else None
            )
            
            # Call the original method
            original_chat_single_round(message)
            
            # Track the message after processing
            message_after = safe_serialize_message(copy.deepcopy(message))
            
            # Determine what changed in the message
            changed_fields = []
            for k in message_after:
                if k in message_before:
                    if message_after[k] != message_before[k]:
                        changed_fields.append(k)
                else:
                    changed_fields.append(k)
            
            # Extract SQL if present
            sql = message_after.get("pred", "")
            
            # Helper to get field values
            def get_field(msg, field):
                if field in msg:
                    val = msg[field]
                    if isinstance(val, str) and len(val) > 100:
                        return val[:100] + "..."
                    return val
                return None
            
            flow_tracker.track_message(
                from_agent=message_after.get("send_from", "Unknown"),
                to_agent=message_after.get("send_to", "System"),
                action="process_result",
                data={
                    "message_type": "after",
                    "query": message_after.get("query", ""),
                    "db_id": message_after.get("db_id", ""),
                    "step": message_after.get("step", ""),
                    "changed_fields": changed_fields,
                    "sql": sql
                },
                raw_message=message_after if args.full_trace else None
            )
            
        # Replace the method
        chat_manager._chat_single_round = types.MethodType(tracked_chat_single_round, chat_manager)
    
    # Construct the message
    msg = {
        "db_id": db_id,
        "query": question,
        "evidence": evidence if evidence else "",
        "ground_truth": gold_sql if gold_sql else "",
        "send_to": "System"  # Initial routing to System
    }
    
    # Print the query information
    if HAS_PRETTY_DEBUG:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}TESTING QUERY ON {db_id}{Colors.END}")
        print(f"{Colors.BOLD}Question:{Colors.END} {question}")
        if evidence:
            print(f"{Colors.BOLD}Evidence:{Colors.END} {evidence}")
        if gold_sql:
            print(f"{Colors.BOLD}Gold SQL:{Colors.END}")
            print_sql(gold_sql)
    else:
        print(f"\nTesting query on database: {db_id}")
        print(f"Question: {question}")
        if evidence:
            print(f"Evidence: {evidence}")
        if gold_sql:
            print(f"Gold SQL: {gold_sql}")
    
    # Print database tables
    print_db_tables(db_id, db_path)
    
    # Process the query
    start_time = datetime.now()
    chat_manager.start(msg)
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    # Extract the predicted SQL
    pred_sql = msg.get("pred", "")
    
    # Print the results
    if HAS_PRETTY_DEBUG:
        print(f"\n{Colors.BOLD}{Colors.GREEN}RESULTS{Colors.END}")
        print(f"{Colors.BOLD}Execution time:{Colors.END} {execution_time:.2f} seconds")
        print(f"\n{Colors.BOLD}Predicted SQL:{Colors.END}")
        print_sql(pred_sql)
    else:
        print("\nResults:")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Predicted SQL: {pred_sql}")
        
    # Check execution match if gold SQL is provided
    execution_match = False
    exact_match = False
    gold_time = 0
    pred_time = 0
    if gold_sql:
        try:
            # Calculate exact match
            exact_match = calculate_exact_match(pred_sql, gold_sql)
            
            execution_results = execute_and_compare_bird_queries(pred_sql, gold_sql, db_id, db_path)
            execution_match = execution_results["execution_match"]
            gold_time = execution_results["gold_time"]
            pred_time = execution_results["pred_time"]
            
            if HAS_PRETTY_DEBUG:
                print(f"{Colors.BOLD}Gold SQL execution time:{Colors.END} {gold_time:.4f} seconds")
                print(f"{Colors.BOLD}Predicted SQL execution time:{Colors.END} {pred_time:.4f} seconds")
                
                if exact_match:
                    print(f"{Colors.BOLD}{Colors.GREEN}Exact match:{Colors.END} {exact_match}")
                else:
                    print(f"{Colors.BOLD}{Colors.YELLOW}Exact match:{Colors.END} {exact_match}")
                
                if execution_match:
                    print(f"{Colors.BOLD}{Colors.GREEN}Execution match:{Colors.END} {execution_match}")
                else:
                    print(f"{Colors.BOLD}{Colors.RED}Execution match:{Colors.END} {execution_match}")
                
                if execution_results["gold_error"]:
                    print(f"{Colors.BOLD}{Colors.RED}Gold SQL error:{Colors.END} {execution_results['gold_error']}")
                if execution_results["pred_error"]:
                    print(f"{Colors.BOLD}{Colors.RED}Predicted SQL error:{Colors.END} {execution_results['pred_error']}")
            else:
                print(f"Gold SQL execution time: {gold_time:.4f} seconds")
                print(f"Predicted SQL execution time: {pred_time:.4f} seconds")
                print(f"Exact match: {exact_match}")
                print(f"Execution match: {execution_match}")
                
                if execution_results["gold_error"]:
                    print(f"Gold SQL error: {execution_results['gold_error']}")
                if execution_results["pred_error"]:
                    print(f"Predicted SQL error: {execution_results['pred_error']}")
        except Exception as e:
            print(f"Error checking execution match: {e}")
    
    # Display agent flow if requested
    if args and args.visualize and HAS_AGENT_FLOW:
        print_agent_flow()
        
    # Return the results
    result = {
        "db_id": db_id,
        "question": question,
        "evidence": evidence if evidence else "",
        "gold_sql": gold_sql if gold_sql else "",
        "pred_sql": pred_sql,
        "execution_time": execution_time
    }
    
    if gold_sql:
        result["execution_match"] = execution_match
        result["exact_match"] = exact_match
        result["gold_time"] = gold_time
        result["pred_time"] = pred_time
    
    return result

def execute_and_compare_bird_queries(pred_sql, gold_sql, db_id, db_path):
    """Execute and compare the results of two SQL queries on a BIRD database."""
    result = {
        "execution_match": False,
        "gold_time": 0,
        "pred_time": 0,
        "gold_error": None,
        "pred_error": None
    }
    
    if not pred_sql or not gold_sql:
        result["pred_error"] = "Empty SQL query"
        return result
    
    # Find the database file
    db_file = os.path.join(db_path, db_id, f"{db_id}.sqlite")
    if not os.path.exists(db_file):
        result["gold_error"] = f"Database file not found: {db_file}"
        logger.error(result["gold_error"])
        return result
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Execute gold SQL with timing
        import time
        gold_start = time.time()
        try:
            cursor.execute(gold_sql)
            gold_result = cursor.fetchall()
            gold_cols = [desc[0] for desc in cursor.description] if cursor.description else []
            result["gold_time"] = time.time() - gold_start
        except Exception as e:
            result["gold_error"] = str(e)
            logger.error(f"Error executing gold SQL: {e}")
            conn.close()
            return result
        
        # Execute predicted SQL with timing
        pred_start = time.time()
        try:
            cursor.execute(pred_sql)
            pred_result = cursor.fetchall()
            pred_cols = [desc[0] for desc in cursor.description] if cursor.description else []
            result["pred_time"] = time.time() - pred_start
        except Exception as e:
            result["pred_error"] = str(e)
            logger.error(f"Error executing predicted SQL: {e}")
            conn.close()
            return result
        
        # Close connection
        conn.close()
        
        # BIRD has specific rules for execution match comparison
        # Check if column counts match
        if len(gold_cols) != len(pred_cols):
            return result
        
        # Check if results have the same row count
        if len(gold_result) != len(pred_result):
            return result
        
        # Convert results to sets for comparison (ignoring column order)
        gold_set = set(map(tuple, gold_result))
        pred_set = set(map(tuple, pred_result))
        
        # Check if results match - binary result (True or False)
        result["execution_match"] = gold_set == pred_set
        return result
    
    except Exception as e:
        result["pred_error"] = str(e)
        logger.error(f"Error comparing queries: {e}")
        return result

def log_agent_messages(message):
    """Log agent interactions for debugging."""
    if not message:
        return
    
    # Extract common fields
    query = message.get("query", "N/A")
    db_id = message.get("db_id", "N/A")
    send_from = message.get("send_from", "N/A")
    send_to = message.get("send_to", "N/A")
    
    logger.debug(f"Message from {send_from} to {send_to}")
    logger.debug(f"Database: {db_id}")
    logger.debug(f"Query: {query}")
    
    # Log specific fields based on agent
    if send_from == "Selector":
        desc_str = message.get("desc_str", "")
        logger.debug(f"Schema description: {desc_str[:100]}...")
    
    elif send_from == "Decomposer":
        final_sql = message.get("final_sql", "")
        qa_pairs = message.get("qa_pairs", [])
        logger.debug(f"SQL: {final_sql}")
        logger.debug(f"QA Pairs: {qa_pairs[:2]}...")
    
    elif send_from == "Refiner":
        pred = message.get("pred", "")
        logger.debug(f"Refined SQL: {pred}")
    
    logger.debug("-" * 50)

def normalize_sql(sql):
    """Normalize SQL for exact matching comparison."""
    if not sql:
        return ""
    
    # Convert to lowercase
    sql = sql.lower()
    
    # Remove extra whitespace
    sql = " ".join(sql.split())
    
    # Remove backticks, quotes around identifiers
    sql = sql.replace("`", "")
    
    # Normalize aliases (convert T1, T2 to t1, t2)
    sql = sql.replace(" as t1", " as t1").replace(" as t2", " as t2")
    
    # Normalize SQL keywords
    for keyword in ["select", "from", "where", "group by", "order by", "having", "limit", "join", "on", "and", "or"]:
        # Ensure keywords are separated by spaces
        sql = sql.replace(f" {keyword} ", f" {keyword} ")
    
    return sql

def calculate_exact_match(pred_sql, gold_sql):
    """Calculate if the predicted SQL exactly matches the gold SQL after normalization."""
    if not pred_sql or not gold_sql:
        return False
    
    # Normalize both SQL queries
    norm_pred = normalize_sql(pred_sql)
    norm_gold = normalize_sql(gold_sql)
    
    # Compare normalized versions
    return norm_pred == norm_gold

def test_agent_subset(
    bird_path: str,
    num_samples: int = 5,
    visualize: bool = False,
    log_level: str = "INFO",
    viz_format: str = "html",
    viz_output: str = None,
    result_output: str = None,
    full_trace: bool = False
):
    """Test the MAC-SQL agent on a subset of BIRD dataset."""
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Set up parameters
    args = types.SimpleNamespace(
        visualize=visualize,
        viz_format=viz_format,
        viz_output=viz_output,
        full_trace=full_trace
    )
    
    # Find the BIRD data
    db_path = get_bird_db_path(bird_path)
    tables_path = get_bird_tables_path(bird_path)
    
    # Load queries from the dataset
    queries = load_bird_queries(bird_path, num_samples=num_samples)
    
    logger.info(f"Testing {len(queries)} queries from BIRD dataset")
        
    # Process each query
    results = []
    for i, query in enumerate(queries):
        db_id = query.get("db_id", "")
        question = query.get("question", "")
        gold_sql = query.get("SQL", "")
        evidence = query.get("evidence", "")
        
        logger.info(f"Query {i+1}/{len(queries)}: {question} (DB: {db_id})")
        
        # Test this query
        result = test_single_query(db_id, question, gold_sql, evidence, args)
        results.append(result)
        
        print("\n" + "="*80 + "\n")
        
    # Calculate metrics
    num_matches = sum(1 for r in results if r.get("execution_match", False))
    execution_accuracy = num_matches / len(results) if results else 0
    
    # Calculate exact matches
    exact_matches = sum(1 for r in results if calculate_exact_match(r.get("pred_sql", ""), r.get("gold_sql", "")))
    exact_match_score = exact_matches / len(results) if results else 0
    
    # Calculate execution time statistics
    valid_gold_times = [r.get("gold_time", 0) for r in results if r.get("gold_time", 0) > 0]
    valid_pred_times = [r.get("pred_time", 0) for r in results if r.get("pred_time", 0) > 0]
    
    avg_gold_time = sum(valid_gold_times) / len(valid_gold_times) if valid_gold_times else 0
    avg_pred_time = sum(valid_pred_times) / len(valid_pred_times) if valid_pred_times else 0
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total queries: {len(results)}")
    print(f"Execution matches: {num_matches}/{len(results)} ({execution_accuracy:.2%})")
    print(f"Exact matches: {exact_matches}/{len(results)} ({exact_match_score:.2%})")
    print(f"Average gold SQL execution time: {avg_gold_time:.4f} seconds")
    print(f"Average predicted SQL execution time: {avg_pred_time:.4f} seconds")
    print("="*50)
    
    # Save results if output path is specified
    if result_output:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(result_output), exist_ok=True)
        
        # Create results dictionary with metadata
        output_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "num_samples": len(results),
                "execution_accuracy": execution_accuracy,
                "avg_gold_time": avg_gold_time,
                "avg_pred_time": avg_pred_time,
                "model": TOGETHER_MODEL,
                "dataset": "BIRD",
                "metrics": {
                    "exact_match": exact_match_score
                }
            },
            "results": results
        }
        
        # Save to file
        with open(result_output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Results saved to {result_output}")
    
    # Generate visualization if requested
    if visualize and HAS_AGENT_FLOW:
        visualize_agent_flow_wrapper(
            format_type=viz_format,
            output_path=viz_output
        )
    
    return results, execution_accuracy

def main():
    """Main function for testing the MAC-SQL agent on BIRD dataset."""
    args = parse_args()
    
    # Configure logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Find BIRD data
    bird_path = find_bird_data()
    logger.info(f"Using BIRD data in: {bird_path}")
    
    # Output path configuration
    output_path = args.output
    if output_path is None:
        # Create a default output path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"bird_agent_results_{timestamp}.json")
    
    # Visualization path configuration
    viz_output = args.viz_output
    if viz_output is None and args.visualize:
        # Create a default visualization path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        viz_dir = "output"
        os.makedirs(viz_dir, exist_ok=True)
        extension = ".html" if args.viz_format == "html" else ".json" if args.viz_format == "json" else ".md"
        viz_output = os.path.join(viz_dir, f"bird_agent_flow_{timestamp}{extension}")
    
    # Run test
    results, accuracy = test_agent_subset(
        bird_path,
        num_samples=args.samples,
        visualize=args.visualize,
        log_level=args.log_level,
        viz_format=args.viz_format,
        viz_output=viz_output,
        result_output=output_path,
        full_trace=args.full_trace
    )
    
    return results, accuracy

def visualize_agent_flow_wrapper(messages=None, format_type="html", output_path=None):
    """Wrapper for visualizing agent flow to handle exceptions."""
    if not HAS_AGENT_FLOW:
        print("Agent flow visualization not available.")
        return
    
    try:
        # Create directory if it doesn't exist
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Visualize agent flow
        visualize_agent_flow(
            messages=messages,
            format_type=format_type,
            output_path=output_path
        )
        
        if output_path:
            print(f"Agent flow visualization saved to {output_path}")
    except Exception as e:
        print(f"Error generating visualization: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 