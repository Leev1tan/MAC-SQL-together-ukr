#!/usr/bin/env python
"""
Run BIRD benchmark evaluation for MAC-SQL with Together API.
This script sets up the correct database paths and performs the evaluation.
"""

import os
import sys
import argparse
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import random

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bird_evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def find_dataset_paths():
    """Find the BIRD dataset directory."""
    possible_paths = [
        "MAC-SQL/data/bird",
        "data/bird",
        "../MAC-SQL/data/bird",
        "../data/bird",
        "MAC-SQL/data/minidev/MINIDEV",  # Additional BIRD-specific path
        "data/minidev/MINIDEV",          # Additional BIRD-specific path
    ]
    
    # First check if environment variable is set
    env_path = os.environ.get("BIRD_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Found BIRD data directory from environment variable: {env_path}")
        return env_path
    
    # Otherwise search in possible paths
    for path in possible_paths:
        if os.path.exists(path):
            logger.info(f"Found BIRD data directory: {path}")
            return path
    
    logger.error("BIRD dataset directory not found. Please set the BIRD_PATH environment variable.")
    return None

def verify_database_structure(bird_path):
    """Verify that the database structure is correct."""
    # Check if the database directory exists (BIRD uses "dev_databases" instead of "database")
    db_dir = os.path.join(bird_path, "dev_databases")
    if not os.path.exists(db_dir):
        db_dir = os.path.join(bird_path, "database")  # Try alternative name
        if not os.path.exists(db_dir):
            logger.error(f"Database directory not found: {db_dir}")
            return False
    
    # Check if tables.json or dev_tables.json exists
    tables_json_options = [
        os.path.join(bird_path, "tables.json"),
        os.path.join(bird_path, "dev_tables.json")  # BIRD often uses this name
    ]
    
    tables_json_found = False
    for tables_path in tables_json_options:
        if os.path.exists(tables_path):
            tables_json_found = True
            logger.info(f"Found tables schema at: {tables_path}")
            os.environ["BIRD_TABLES_PATH"] = tables_path  # Store for later use
            break
    
    if not tables_json_found:
        logger.error(f"Tables schema not found in any of the expected locations")
        return False
    
    # Check if dataset JSON exists (BIRD has different file names)
    dataset_files = [
        os.path.join(bird_path, "dev.json"),
        os.path.join(bird_path, "mini_dev.json"),
        os.path.join(bird_path, "mini_dev_sqlite.json")
    ]
    
    dataset_found = False
    for file_path in dataset_files:
        if os.path.exists(file_path):
            dataset_found = True
            break
    
    if not dataset_found:
        logger.error("BIRD queries file not found in any of the expected locations")
        return False
    
    # Check if at least one database exists
    # Unlike Spider, we don't know the exact DB names in advance, so check if the directory has content
    if len(os.listdir(db_dir)) == 0:
        logger.error(f"No database directories found in: {db_dir}")
        logger.error("Database files may be missing. Please download the BIRD dataset.")
        return False
    
    logger.info("Database structure verified successfully")
    return True

def run_evaluation(bird_path, num_samples=10, visualize=False, viz_format="html"):
    """Run the evaluation using test_macsql_agent_bird.py."""
    # Make sure paths are absolute
    abs_bird_path = os.path.abspath(bird_path)
    
    # Set environment variables
    env = os.environ.copy()
    env["BIRD_PATH"] = abs_bird_path
    
    # Pass tables json path if we found it during verification
    if "BIRD_TABLES_PATH" in os.environ:
        env["BIRD_TABLES_PATH"] = os.environ["BIRD_TABLES_PATH"]
    
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"

    # For Windows, use a different path separator
    if os.name == 'nt':
        env["PYTHONPATH"] = f"{os.getcwd()};{env.get('PYTHONPATH', '')}"
    
    # Create output directory for results
    os.makedirs("output", exist_ok=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"output/bird_agent_results_{timestamp}.json"
    
    # Prepare the command
    cmd = [
        sys.executable,
        "test_macsql_agent_bird.py",
        "--samples", str(num_samples),
        "--output", output_file
    ]
    
    if visualize:
        cmd.append("--visualize")
        cmd.extend(["--viz-format", viz_format])
        
        # Add default visualization output path
        extension = ".html" if viz_format == "html" else ".json" if viz_format == "json" else ".md"
        viz_output = f"output/bird_agent_flow_{timestamp}{extension}"
        cmd.extend(["--viz-output", viz_output])
    
    # Run the evaluation
    logger.info(f"Running evaluation with command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env, check=True)
        logger.info(f"Evaluation completed successfully, results stored in {output_file}")
        
        # Return the output file path for analysis
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Evaluation failed: {e}")
        return None

def analyze_results(results_path, model_info=None):
    """Analyze the results of the BIRD dataset evaluation."""
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    metadata = data.get('metadata', {})
    
    # Get dataset type (BIRD or BIRD-UKR)
    dataset_type = metadata.get('dataset', 'BIRD')
    
    # Check if results exist
    if not results:
        print("No results found.")
        return

    # Calculate total questions and number of matches
    total = len(results)
    matches = sum(1 for r in results if r.get('execution_match', False))
    
    # Calculate execution accuracy
    ex = matches / total if total > 0 else 0
    
    # Calculate EM if available
    em_matches = sum(1 for r in results if r.get('exact_match', False))
    em = em_matches / total if total > 0 else 0
    
    # Calculate average execution times
    valid_gold_times = [r.get('gold_time', 0) for r in results if r.get('gold_time') is not None]
    valid_pred_times = [r.get('pred_time', 0) for r in results if r.get('pred_time') is not None]
    
    avg_gold_time = sum(valid_gold_times) / len(valid_gold_times) if valid_gold_times else 0
    avg_pred_time = sum(valid_pred_times) / len(valid_pred_times) if valid_pred_times else 0
    
    # Calculate time efficiency ratio (smaller is better)
    time_ratio = avg_pred_time / avg_gold_time if avg_gold_time > 0 else float('inf')
    
    # Print summary
    print("=" * 50)
    print(f"Dataset: {dataset_type}")
    if model_info:
        print(f"Model: {model_info}")
    print(f"Total queries: {total}")
    print(f"Execution matches: {matches}")
    print(f"Execution accuracy (EX): {ex:.4f}")
    
    if any('exact_match' in r for r in results):
        print(f"Exact matches: {em_matches}")
        print(f"Exact match score (EM): {em:.4f}")
    
    print(f"Average gold SQL time: {avg_gold_time:.4f}s")
    print(f"Average pred SQL time: {avg_pred_time:.4f}s")
    print(f"Time efficiency ratio: {time_ratio:.4f}")
    print("=" * 50)
    
    return {
        "dataset": dataset_type,
        "total": total,
        "matches": matches,
        "ex": ex,
        "em_matches": em_matches,
        "em": em,
        "avg_gold_time": avg_gold_time,
        "avg_pred_time": avg_pred_time,
        "time_ratio": time_ratio
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="meta-llama/Llama-3.3-70B-Instruct-Turbo", 
                       help="LLM model to use")
    parser.add_argument("--dataset", type=str, default="bird", 
                        choices=["bird", "bird-dev", "bird-ukr"],
                        help="Dataset to use: bird (full), bird-dev (dev set), or bird-ukr (Ukrainian)")
    parser.add_argument("--num-samples", type=int, default=10, help="Number of samples to test")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--analyze-only", type=str, help="Only analyze the given results file")
    parser.add_argument("--db-filter", type=str, nargs="*", help="Filter by database IDs (space-separated)")
    args = parser.parse_args()

    if args.analyze_only:
        analyze_results(args.analyze_only)
        sys.exit(0)

    # Set the random seed
    random.seed(args.seed)

    # Determine which test script to run based on the dataset
    if args.dataset == "bird-ukr":
        # For Ukrainian BIRD dataset, use the specialized test script
        test_script = "test_macsql_agent_bird_ukr.py"
        data_path = "bird-ukr"
    else:
        # For English BIRD dataset, use the original test script
        test_script = "test_macsql_agent_bird.py"
        data_path = "bird" if args.dataset == "bird" else "bird-dev"

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_id = args.model.split("/")[-1].replace("-", "_").lower()
    output_file = f"{model_id}_{args.dataset}_{args.num_samples}_{timestamp}.json"
    output_path = os.path.join(args.output_dir, output_file)

    # Build the command
    cmd = [
        "python",
        test_script,
        f"--model={args.model}",
        f"--data-path={data_path}",
        f"--num-samples={args.num_samples}",
        f"--output={output_path}"
    ]

    # Add database filter if specified
    if args.db_filter:
        cmd.append(f"--db-filter={' '.join(args.db_filter)}")

    # Run the test
    print(f"Running command: {' '.join(cmd)}")
    process = subprocess.run(cmd)

    # Check if the test was successful
    if process.returncode == 0 and os.path.exists(output_path):
        print(f"Test completed successfully. Results saved to {output_path}")
        analyze_results(output_path, args.model)
    else:
        print(f"Test failed with return code {process.returncode}")

if __name__ == "__main__":
    sys.exit(main()) 