#!/usr/bin/env python
"""
Run Spider benchmark evaluation for MAC-SQL with Together API.
This script sets up the correct database paths and performs the evaluation.
"""

import os
import sys
import argparse
import json
import logging
import subprocess
from pathlib import Path
import time
from datetime import datetime

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/spider_evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def find_dataset_paths():
    """Find the Spider dataset directory."""
    possible_paths = [
        "MAC-SQL/data/spider",
        "data/spider",
        "../MAC-SQL/data/spider",
        "../data/spider",
    ]
    
    # First check if environment variable is set
    env_path = os.environ.get("SPIDER_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Found Spider data directory from environment variable: {env_path}")
        return env_path
    
    # Otherwise search in possible paths
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found Spider data directory: {path}")
            return path
    
    logger.error("Spider dataset directory not found. Please set the SPIDER_PATH environment variable.")
    return None

def verify_database_structure(spider_path):
    """Verify that the database structure is correct."""
    # Check if the database directory exists
    db_dir = os.path.join(spider_path, "database")
    if not os.path.exists(db_dir):
        logger.error(f"Database directory not found: {db_dir}")
        return False
    
    # Check if tables.json exists
    tables_json = os.path.join(spider_path, "tables.json")
    if not os.path.exists(tables_json):
        logger.error(f"Tables schema not found: {tables_json}")
        return False
    
    # Check if dev.json exists
    dev_json = os.path.join(spider_path, "dev.json")
    if not os.path.exists(dev_json):
        logger.error(f"Dev queries not found: {dev_json}")
        return False
    
    # Check if at least one database exists
    sample_db_path = os.path.join(db_dir, "world_1", "world_1.sqlite")
    if not os.path.exists(sample_db_path):
        logger.error(f"Sample database not found: {sample_db_path}")
        logger.error("Database files may be missing. Please download the Spider dataset.")
        return False
    
    logger.info("Database structure verified successfully")
    return True

def run_evaluation(spider_path, num_samples=10, visualize=False, output_path=None):
    """Run the evaluation using test_macsql_agent_spider.py."""
    # Make sure paths are absolute
    abs_spider_path = os.path.abspath(spider_path)
    
    # Set environment variables
    env = os.environ.copy()
    env["SPIDER_PATH"] = abs_spider_path
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"

    # For Windows, use a different path separator
    if os.name == 'nt':
        env["PYTHONPATH"] = f"{os.getcwd()};{env.get('PYTHONPATH', '')}"
    
    # Determine output file path
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"output/spider_agent_results_{timestamp}.json"
    else:
        # Ensure output directory exists if a specific path is given
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Prepare the command
    cmd = [
        sys.executable,
        "test_macsql_agent_spider.py",
        "--samples", str(num_samples),
        "--output", output_path # Pass the determined output path
    ]
    
    if visualize:
        cmd.append("--visualize")
    
    # Run the evaluation
    logger.info(f"Running evaluation with command: {' '.join(cmd)}")
    logger.info(f"Results will be saved to: {output_path}")
    try:
        subprocess.run(cmd, env=env, check=True)
        logger.info("Evaluation completed successfully")
        return output_path # Return the actual path used
    except subprocess.CalledProcessError as e:
        logger.error(f"Evaluation failed: {e}")
        return None

def analyze_results(results_path: str):
    """Analyzes the results JSON file and prints metrics."""
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # --- Corrected access to the results list ---
        results_list = data.get("results", []) # Access the list within the 'results' key
        if not results_list:
             print(f"Warning: No results found in {results_path}")
             return
        # --- End of correction ---

        num_questions = len(results_list)
        if num_questions == 0:
            print("No results found to analyze.")
            return

        # Use metrics from overall_metrics if available, otherwise calculate
        overall_metrics = data.get("overall_metrics")
        if overall_metrics:
            exact_matches = int(overall_metrics.get("exact_match", 0) * num_questions) # Approximate back
            execution_matches = int(overall_metrics.get("execution_accuracy", 0) * num_questions) # Approximate back
            ves = overall_metrics.get("valid_efficiency_score", 0)
            logging.info("Using pre-calculated overall metrics from JSON.")
        else:
            # Calculate metrics if overall_metrics is not present (fallback)
            logging.info("Calculating metrics from individual results (overall_metrics not found).")
            exact_matches = sum(1 for r in results_list if r.get("exact_match", False))
            execution_matches = sum(1 for r in results_list if r.get("execution_match", False))
            # VES calculation might need more complex logic if not pre-calculated
            ves = sum(r.get("ves_score", 0) for r in results_list) # Example, adjust if needed

        exact_match_acc = (exact_matches / num_questions) * 100 if num_questions > 0 else 0
        execution_acc = (execution_matches / num_questions) * 100 if num_questions > 0 else 0

        print(f"--- Analysis Results ({results_path}) ---")
        print(f"Total Questions: {num_questions}")
        print(f"Exact Match Accuracy (EM): {exact_match_acc:.2f}% ({exact_matches}/{num_questions})")
        print(f"Execution Accuracy (EX): {execution_acc:.2f}% ({execution_matches}/{num_questions})")
        if overall_metrics:
            print(f"Valid Efficiency Score (VES): {ves:.2f}")
        else:
            print(f"Summed VES (if available): {ves:.2f}") # Indicate if it was calculated differently
        print("--- End Analysis ---")

    except FileNotFoundError:
        logging.error(f"Results file not found: {results_path}")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {results_path}")
    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}")
        # Optionally re-raise or print traceback for more detail
        # import traceback
        # traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Run MAC-SQL evaluation against Spider')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples to evaluate')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization of agent communication (currently disabled)')
    parser.add_argument('--output', type=str, default=None, help='Specify the output JSON file path. Default: output/spider_agent_results_[timestamp].json')
    args = parser.parse_args()
    
    # Find Spider path
    spider_path = find_dataset_paths()
    if not spider_path:
        return 1
    
    # Verify database structure
    if not verify_database_structure(spider_path):
        return 1
    
    # Run evaluation, passing the desired output path (or None for default)
    actual_output_path = run_evaluation(spider_path, args.samples, visualize=False, output_path=args.output)
    if not actual_output_path:
        return 1
    
    # Analyze results
    analyze_results(actual_output_path) # Pass the correct path
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 