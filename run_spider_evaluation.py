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

def run_evaluation(spider_path, num_samples=10, visualize=False):
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
    
    # Prepare the command
    cmd = [
        sys.executable,
        "test_macsql_agent_spider.py",
        "--samples", str(num_samples)
    ]
    
    if visualize:
        cmd.append("--visualize")
    
    # Run the evaluation
    logger.info(f"Running evaluation with command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, env=env, check=True)
        logger.info("Evaluation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Evaluation failed: {e}")
        return False

def analyze_results():
    """Analyze the evaluation results."""
    results_path = "output/spider_agent_results.json"
    if not os.path.exists(results_path):
        logger.error(f"Results file not found: {results_path}")
        return
    
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Calculate metrics
    total = len(results)
    execution_matches = sum(1 for r in results if r.get("execution_match", False))
    execution_accuracy = (execution_matches / total) * 100 if total > 0 else 0
    
    # Extract advanced metrics if available
    em_score = 0
    ex_score = execution_accuracy
    ves_score = 0
    
    if "metrics" in results[0]:
        metrics_counts = 0
        em_total = 0
        ves_total = 0
        
        for r in results:
            if "metrics" in r:
                metrics = r["metrics"]
                metrics_counts += 1
                if "exact_match" in metrics:
                    em_total += metrics["exact_match"]
                if "valid_efficiency_score" in metrics:
                    ves_total += metrics["valid_efficiency_score"]
        
        if metrics_counts > 0:
            em_score = (em_total / metrics_counts) * 100
            ves_score = ves_total / metrics_counts
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY (Spider Dataset)")
    print("="*60)
    print(f"Total queries: {total}")
    print(f"Execution matches: {execution_matches}/{total}")
    print(f"Execution Accuracy (EX): {execution_accuracy:.2f}%")
    print(f"Exact Match (EM): {em_score:.2f}%")
    print(f"Valid Efficiency Score (VES): {ves_score:.2f}")
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Run MAC-SQL evaluation against Spider')
    parser.add_argument('--samples', type=int, default=10, help='Number of samples to evaluate')
    parser.add_argument('--visualize', action='store_true', help='Generate visualization of agent communication (currently disabled)')
    args = parser.parse_args()
    
    # Find Spider path
    spider_path = find_dataset_paths()
    if not spider_path:
        return 1
    
    # Verify database structure
    if not verify_database_structure(spider_path):
        return 1
    
    # Run evaluation without visualization
    if not run_evaluation(spider_path, args.samples, visualize=False):
        return 1
    
    # Analyze results
    analyze_results()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 