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

# --- Early Environment Setup --- 
from dotenv import load_dotenv

# Load .env file first, force override, and check result
load_result = load_dotenv(override=True)
print(f"load_dotenv result (found file?): {load_result}")
print(f"TOGETHER_MODEL after load_dotenv: {os.environ.get('TOGETHER_MODEL')}")

# Early parse for --model argument ONLY
# We need to parse this early to set the env var before core modules might be implicitly loaded
# by the subprocess or other parts of this script.
early_parser = argparse.ArgumentParser(add_help=False) 
early_parser.add_argument("--model", type=str, help="Override TOGETHER_MODEL env var")
early_args, _ = early_parser.parse_known_args()

# Set TOGETHER_MODEL env var if --model is provided, otherwise keep loaded value
if early_args.model:
    os.environ["TOGETHER_MODEL"] = early_args.model
    print(f"Overriding TOGETHER_MODEL with --model arg: {early_args.model}")
else:
    print(f"Using TOGETHER_MODEL from environment: {os.environ.get('TOGETHER_MODEL')}")
# ------------------------------

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

def run_evaluation(bird_path, num_samples=10, visualize=False, viz_format="html", output_path=None):
    """Run the evaluation using test_macsql_agent_bird.py."""
    # Make sure paths are absolute
    abs_bird_path = os.path.abspath(bird_path)
    
    # Set environment variables for the subprocess
    env = os.environ.copy() # Start with current environment (includes TOGETHER_MODEL)
    env["BIRD_PATH"] = abs_bird_path
    
    # Pass tables json path if we found it during verification
    if "BIRD_TABLES_PATH" in os.environ:
        env["BIRD_TABLES_PATH"] = os.environ["BIRD_TABLES_PATH"]
    
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"

    # For Windows, use a different path separator
    if os.name == 'nt':
        env["PYTHONPATH"] = f"{os.getcwd()};{env.get('PYTHONPATH', '')}"
    
    # --- Log the model being passed to the subprocess ---
    logger.info(f"Passing TOGETHER_MODEL={env.get('TOGETHER_MODEL')} to subprocess.")
    # ----------------------------------------------------

    # Create output directory for results
    os.makedirs("output", exist_ok=True)
    
    # Use provided output path or generate one with timestamp
    if not output_path:
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/bird_agent_results_{timestamp}.json"
    
    # Prepare the command
    cmd = [
        sys.executable,
        "test_macsql_agent_bird.py",
        "--samples", str(num_samples),
        "--output", output_path
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
        logger.info(f"Evaluation completed successfully, results stored in {output_path}")
        
        # Return the output file path for analysis
        return output_path
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
    # Use the regular full parser here
    parser = argparse.ArgumentParser(description='Run MAC-SQL evaluation against BIRD')
    # Add the --model argument back here for the full parse, but it's already handled
    parser.add_argument("--model", type=str, default=os.getenv("TOGETHER_MODEL"), # Default to env var
                        help="LLM model to use (sets TOGETHER_MODEL env var)")
    parser.add_argument("--dataset", type=str, default="bird", 
                        choices=["bird", "bird-dev", "bird-ukr"],
                        help="Dataset to use: bird (full), bird-dev (dev set), or bird-ukr (Ukrainian)")
    parser.add_argument("--num-samples", type=int, default=10, help="Number of samples to test")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--analyze-only", type=str, help="Only analyze the given results file")
    parser.add_argument("--visualize", action="store_true", help="Generate agent flow visualization")
    parser.add_argument("--viz-format", type=str, default="html", choices=["html", "json", "mermaid"], 
                        help="Visualization format")
    args = parser.parse_args()

    # Logging setup (can stay here)
    logger.info("Starting BIRD evaluation...")
    logger.info(f"Using model (from env): {os.getenv('TOGETHER_MODEL', 'Not Set')}") 

    if args.analyze_only:
        analyze_results(args.analyze_only, args.model)
        sys.exit(0)

    # Set the random seed
    random.seed(args.seed)

    # Determine which dataset path to use
    if args.dataset == "bird-ukr":
        # For Ukrainian BIRD dataset, we need a different approach
        logger.error("Use test_macsql_agent_bird_ukr.py directly for the Ukrainian dataset.")
        sys.exit(1)
    else:
        # For English BIRD dataset
        bird_path = find_dataset_paths()
        if not bird_path:
            sys.exit(1)
            
        # Verify database structure
        if not verify_database_structure(bird_path):
            sys.exit(1)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_id = args.model.split("/")[-1].replace("-", "_").lower()
    output_file = f"{model_id}_{args.dataset}_{args.num_samples}_{timestamp}.json"
    output_path = os.path.join(args.output_dir, output_file)
    
    # Make sure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Run the evaluation with the correct arguments
    results_path = run_evaluation(
        bird_path, 
        num_samples=args.num_samples,
        visualize=args.visualize,
        viz_format=args.viz_format,
        output_path=output_path
    )
    
    if results_path and os.path.exists(results_path):
        print(f"Test completed successfully. Results saved to {results_path}")
        analyze_results(results_path, args.model)
    else:
        print(f"Test failed or no results generated")
        sys.exit(1)

if __name__ == "__main__":
    # The early environment setup happens before this block
    sys.exit(main()) 