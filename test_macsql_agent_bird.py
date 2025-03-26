#!/usr/bin/env python
"""
Test script for MAC-SQL with Together AI using the agent-based architecture on the BIRD dataset.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv

# Add MAC-SQL to path for imports
sys.path.append(str(Path(__file__).parent / "MAC-SQL"))

# Import our enhanced chat manager
from core.enhanced_chat_manager import EnhancedChatManager, run_with_agents
from core.macsql_together_adapter import TogetherAIAdapter

# Load environment variables
load_dotenv()

# Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct")

def find_bird_data():
    """Find the BIRD dataset in the data directory"""
    data_dir = Path(__file__).parent / "MAC-SQL" / "data" / "bird"
    
    # Check if BIRD directory exists
    if not data_dir.exists():
        print(f"Error: BIRD data directory not found at {data_dir}")
        return None, None, None
    
    # Check for datasets (mini dev or regular dev)
    dataset_options = [
        data_dir / "MINIDEV" / "mini_dev_sqlite.json",  # Mini dev dataset
        data_dir / "dev.json",                          # Regular dev dataset
    ]
    
    dataset_path = None
    for path in dataset_options:
        if path.exists():
            dataset_path = path
            break
    
    if not dataset_path:
        print("Error: Could not find BIRD dataset file. Please ensure it's installed.")
        return None, None, None
    
    # Check for database directories
    db_dirs = [
        data_dir / "MINIDEV" / "dev_databases",  # Mini dev databases
        data_dir / "dev_databases",              # Regular dev databases
    ]
    
    db_path = None
    for path in db_dirs:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("Error: Could not find BIRD database directory. Please ensure it's installed.")
        return None, None, None
    
    # Look for tables.json
    tables_options = [
        data_dir / "tables.json",
        data_dir / "MINIDEV" / "tables.json"
    ]
    
    tables_path = None
    for path in tables_options:
        if path.exists():
            tables_path = path
            break
    
    return dataset_path, db_path, tables_path

def test_single_query(db_id, question, evidence="", ground_truth=""):
    """
    Test a single query using the agent-based architecture.
    
    Args:
        db_id: Database ID
        question: Natural language question
        evidence: Optional evidence text
        ground_truth: Optional ground truth SQL
        
    Returns:
        Generated SQL and execution results
    """
    # Find BIRD data paths
    dataset_path, db_path, tables_path = find_bird_data()
    if not dataset_path or not db_path or not tables_path:
        return None, None
    
    # Set up logging directory
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_path = str(logs_dir / "agent_test_single.log")
    
    # Configure Together AI integration
    TogetherAIAdapter.set_api_integration()
    
    # Initialize manager with our enhanced implementation
    manager = EnhancedChatManager(
        data_path=str(db_path),
        tables_json_path=str(tables_path),
        log_path=log_path,
        model_name=TOGETHER_MODEL,
        dataset_name="bird"
    )
    
    # Create message for chat manager
    message = {
        'db_id': db_id,
        'query': question,
        'evidence': evidence,
        'extracted_schema': {},
        'ground_truth': ground_truth,
        'difficulty': 'unknown',
        'send_to': "System"
    }
    
    # Process through agents
    manager.start(message)
    
    # Return generated SQL and execution status
    return message.get('pred', ''), message.get('execution_match', False)

def test_agent_subset(num_samples=5, output_file=None):
    """
    Test a subset of BIRD queries using agent-based architecture.
    
    Args:
        num_samples: Number of samples to test
        output_file: Optional file to save results
        
    Returns:
        Evaluation results
    """
    # Find BIRD data paths
    dataset_path, db_path, tables_path = find_bird_data()
    if not dataset_path or not db_path or not tables_path:
        return None
    
    print(f"Running agent-based test on {num_samples} samples...")
    
    # Run evaluation using enhanced agent-based approach
    try:
        # Import with corrected syntax
        from run_with_together import load_bird_subset
        
        # Load BIRD subset
        queries = load_bird_subset(dataset_path, num_samples=num_samples)
        
        # Set up logging
        logs_dir = Path(__file__).parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_path = str(logs_dir / "agent_test_batch.log")
        
        # Configure Together AI integration
        TogetherAIAdapter.set_api_integration()
        
        # Initialize manager with our enhanced implementation
        manager = EnhancedChatManager(
            data_path=str(db_path),
            tables_json_path=str(tables_path),
            log_path=log_path,
            model_name=TOGETHER_MODEL,
            dataset_name="bird"
        )
        
        # Process each query
        results = []
        for i, query in enumerate(queries):
            print(f"Processing query {i+1}/{len(queries)}: {query['db_id']}")
            
            # Create message for chat manager
            message = {
                'db_id': query['db_id'],
                'query': query['question'],
                'evidence': query.get('evidence', ''),
                'extracted_schema': {},
                'ground_truth': query.get('SQL', ''),
                'difficulty': query.get('difficulty', 'unknown'),
                'send_to': "System"
            }
            
            # Process through agents
            manager.start(message)
            
            # Store results
            result = {
                'db_id': query['db_id'],
                'question': query['question'],
                'gold_sql': query.get('SQL', ''),
                'predicted_sql': message.get('pred', ''),
                'execution_match': message.get('execution_match', False)
            }
            
            results.append(result)
            
            print(f"Result: {'✓' if result['execution_match'] else '✗'} Execution Match")
            print("-" * 50)
        
        # Calculate accuracy
        execution_matches = sum(1 for r in results if r['execution_match'])
        accuracy = execution_matches / len(results) if results else 0
        
        print(f"\nExecution Accuracy: {accuracy:.2%} ({execution_matches}/{len(results)})")
        
        # Save results if output file is specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump({
                    'results': results,
                    'accuracy': accuracy,
                    'total': len(results),
                    'matches': execution_matches
                }, f, indent=2)
            
            print(f"Results saved to {output_path}")
        
        return results
    
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure run_with_together.py is available and properly configured.")
        return None
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_with_pipeline(num_samples=5):
    """
    Compare agent-based approach with pipeline approach on the same queries.
    
    Args:
        num_samples: Number of samples to test
        
    Returns:
        Comparison results
    """
    # Run agent-based approach
    print("Running agent-based approach...")
    agent_results = test_agent_subset(num_samples, "output/agent_results.json")
    
    # Run pipeline approach
    print("\nRunning pipeline approach...")
    try:
        # Import with corrected syntax
        from run_with_together import run_bird_test
        
        pipeline_results = run_bird_test(num_samples)
        
        # Save pipeline results
        with open("output/pipeline_results.json", 'w') as f:
            json.dump(pipeline_results, f, indent=2)
        
        # Calculate pipeline accuracy
        pipeline_matches = sum(1 for r in pipeline_results['results'] if r['execution_match'])
        pipeline_accuracy = pipeline_matches / len(pipeline_results['results']) if pipeline_results['results'] else 0
        
        print(f"\nPipeline Execution Accuracy: {pipeline_accuracy:.2%} ({pipeline_matches}/{len(pipeline_results['results'])})")
        
        # Compare results
        agent_matches = sum(1 for r in agent_results if r['execution_match'])
        agent_accuracy = agent_matches / len(agent_results) if agent_results else 0
        
        print("\nComparison:")
        print(f"Agent-based Accuracy: {agent_accuracy:.2%}")
        print(f"Pipeline Accuracy: {pipeline_accuracy:.2%}")
        print(f"Difference: {agent_accuracy - pipeline_accuracy:.2%}")
        
        return {
            'agent_accuracy': agent_accuracy,
            'pipeline_accuracy': pipeline_accuracy,
            'difference': agent_accuracy - pipeline_accuracy
        }
    
    except ImportError:
        print("Error: Could not import run_bird_test from run_with_together.py")
        return None

def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(description="Test MAC-SQL with Together AI using agent-based architecture")
    parser.add_argument("--samples", type=int, default=5, help="Number of samples to test")
    parser.add_argument("--compare", action="store_true", help="Compare with pipeline approach")
    parser.add_argument("--single", action="store_true", help="Test a single query interactively")
    parser.add_argument("--output", type=str, default="output/agent_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    Path("output").mkdir(exist_ok=True)
    
    if args.single:
        # Interactive test mode
        db_id = input("Enter database ID: ")
        question = input("Enter question: ")
        evidence = input("Enter evidence (optional): ")
        
        print("\nProcessing query...")
        sql, matched = test_single_query(db_id, question, evidence)
        
        print("\nGenerated SQL:")
        print(sql)
        print(f"\nExecution match: {matched}")
    
    elif args.compare:
        # Compare with pipeline approach
        compare_with_pipeline(args.samples)
    
    else:
        # Run agent-based test
        test_agent_subset(args.samples, args.output)

if __name__ == "__main__":
    main() 