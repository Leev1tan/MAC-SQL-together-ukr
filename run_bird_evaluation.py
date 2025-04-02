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

def analyze_results(results_path):
    """Analyze the evaluation results."""
    if not os.path.exists(results_path):
        logger.error(f"Results file not found: {results_path}")
        return
    
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    # Extract metadata and results
    metadata = data.get("metadata", {})
    results = data.get("results", [])
    
    # Calculate metrics
    total = len(results)
    execution_matches = sum(1 for r in results if r.get("execution_match", False))
    execution_accuracy = (execution_matches / total) * 100 if total > 0 else 0
    
    # Calculate execution time metrics
    avg_gold_time = metadata.get("avg_gold_time", 0) 
    avg_pred_time = metadata.get("avg_pred_time", 0)
    
    # Calculate time efficiency ratio where available
    time_efficiency = "N/A"
    if avg_gold_time > 0 and avg_pred_time > 0:
        time_efficiency = avg_gold_time / avg_pred_time
    
    # Extract advanced metrics if available
    em_score = 0
    ex_score = execution_accuracy
    
    if metadata.get("metrics"):
        metrics = metadata.get("metrics", {})
        em_score = metrics.get("exact_match", 0) * 100
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY (BIRD Dataset)")
    print("="*60)
    print(f"Total queries: {total}")
    print(f"Execution matches: {execution_matches}/{total}")
    print(f"Execution Accuracy (EX): {execution_accuracy:.2f}%")
    
    # Print execution time metrics
    print(f"Average gold SQL execution time: {avg_gold_time:.4f} seconds")
    print(f"Average predicted SQL execution time: {avg_pred_time:.4f} seconds") 
    if time_efficiency != "N/A":
        print(f"Time efficiency ratio (gold/pred): {time_efficiency:.4f}")
        if time_efficiency > 1:
            print("  ✓ Predicted queries are faster on average")
        elif time_efficiency < 1:
            print("  ✗ Predicted queries are slower on average")
    
    if metadata.get("metrics"):
        print(f"Exact Match (EM): {em_score:.2f}%")
    
    # Print model information if available
    if metadata.get("model"):
        print(f"Model: {metadata.get('model')}")
    
    print(f"Timestamp: {metadata.get('timestamp', 'N/A')}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Run MAC-SQL evaluation against BIRD')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples to evaluate')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization of agent communication')
    parser.add_argument('--viz-format', type=str, default="html", choices=["html", "json", "mermaid"], 
                        help='Visualization format (if --visualize is used)')
    args = parser.parse_args()
    
    # Find BIRD path
    bird_path = find_dataset_paths()
    if not bird_path:
        return 1
    
    # Verify database structure
    if not verify_database_structure(bird_path):
        return 1
    
    # Run evaluation
    results_file = run_evaluation(
        bird_path, 
        args.samples, 
        visualize=args.visualize,
        viz_format=args.viz_format
    )
    
    if not results_file:
        return 1
    
    # Analyze results
    analyze_results(results_file)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 