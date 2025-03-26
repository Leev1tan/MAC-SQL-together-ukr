#!/usr/bin/env python
"""
Evaluation metrics for text-to-SQL models based on BIRD and Spider benchmarks.
Implements Exact Match Accuracy (EM), Execution Accuracy (EX), and Valid Efficiency Score (VES).
"""

import os
import json
import math
import sqlite3
import time
import argparse
import multiprocessing as mp
from typing import List, Dict, Tuple, Any, Optional, Union
from pathlib import Path

# Import Spider evaluation components if available
try:
    from MAC_SQL.evaluation.evaluation_spider import build_foreign_key_map_from_json, Evaluator, get_schema, get_sql, Schema
    from MAC_SQL.evaluation.exec_eval import eval_exec_match
    SPIDER_EVAL_AVAILABLE = True
except ImportError:
    try:
        # Try alternative import paths
        try:
            # Use a module name without hyphens
            import sys
            sys.path.append("MAC-SQL")
            from evaluation.evaluation_spider import build_foreign_key_map_from_json, Evaluator, get_schema, get_sql, Schema
            from evaluation.exec_eval import eval_exec_match
            SPIDER_EVAL_AVAILABLE = True
        except ImportError:
            SPIDER_EVAL_AVAILABLE = False
            print("Warning: Spider evaluation components not available. Exact Match (EM) will be disabled.")
    except ImportError:
        SPIDER_EVAL_AVAILABLE = False
        print("Warning: Spider evaluation components not available. Exact Match (EM) will be disabled.")

# Globals for parallel execution
_execution_results = []

def result_callback(result: Dict[str, Any]) -> None:
    """Callback function for parallel SQL execution."""
    _execution_results.append(result)

def execute_sql(sql: str, db_path: str, timeout: float = 30.0) -> Tuple[bool, Any, float]:
    """
    Execute SQL query on a database and measure execution time.
    
    Args:
        sql: SQL query to execute
        db_path: Path to SQLite database
        timeout: Maximum execution time in seconds
        
    Returns:
        Tuple of (success, results, execution_time)
    """
    if not os.path.exists(db_path):
        return False, f"Database file not found: {db_path}", 0
    
    try:
        conn = sqlite3.connect(db_path)
        conn.text_factory = str
        cursor = conn.cursor()
        
        # Set timeout (convert to milliseconds)
        conn.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)}")
        
        # Measure execution time
        start_time = time.time()
        cursor.execute(sql)
        results = cursor.fetchall()
        execution_time = time.time() - start_time
        
        conn.close()
        return True, results, execution_time
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return False, str(e), 0

def iterated_execute_sql(pred_sql: str, gold_sql: str, db_path: str, iterations: int = 5) -> Dict[str, Any]:
    """
    Execute SQL queries multiple times to get more accurate timing for VES.
    
    Args:
        pred_sql: Predicted SQL query
        gold_sql: Gold standard SQL query
        db_path: Path to SQLite database
        iterations: Number of iterations for timing measurement
        
    Returns:
        Dictionary with execution results and timing information
    """
    pred_success, pred_result, pred_total_time = False, None, 0
    gold_success, gold_result, gold_total_time = False, None, 0
    
    # Execute gold SQL first to check if it's valid
    gold_success, gold_result, gold_time = execute_sql(gold_sql, db_path)
    
    if not gold_success:
        return {
            "pred_success": False,
            "gold_success": False,
            "execution_match": False,
            "time_ratio": 0,
            "error": f"Gold SQL failed: {gold_result}"
        }
    
    # Execute predicted SQL
    pred_success, pred_result, pred_time = execute_sql(pred_sql, db_path)
    
    if not pred_success:
        return {
            "pred_success": False,
            "gold_success": True,
            "execution_match": False,
            "time_ratio": 0,
            "error": f"Predicted SQL failed: {pred_result}"
        }
    
    # Check execution match
    execution_match = pred_result == gold_result
    
    # If matching and iterations > 1, run multiple times to get better timing
    if execution_match and iterations > 1:
        pred_times = []
        gold_times = []
        
        for _ in range(iterations):
            # Execute gold SQL
            _, _, g_time = execute_sql(gold_sql, db_path)
            gold_times.append(g_time)
            
            # Execute predicted SQL
            _, _, p_time = execute_sql(pred_sql, db_path)
            pred_times.append(p_time)
        
        # Use median to reduce impact of outliers
        pred_times.sort()
        gold_times.sort()
        pred_time = pred_times[iterations // 2]
        gold_time = gold_times[iterations // 2]
    
    # Calculate time ratio for VES (avoid division by zero)
    time_ratio = 0
    if execution_match and gold_time > 0:
        # Lower is better (gold time / predicted time)
        # If pred_time > gold_time, ratio < 1
        # If pred_time < gold_time, ratio > 1 (more efficient than gold)
        time_ratio = gold_time / max(pred_time, 1e-9)
    
    return {
        "pred_success": pred_success,
        "gold_success": gold_success,
        "execution_match": execution_match,
        "pred_time": pred_time,
        "gold_time": gold_time,
        "time_ratio": time_ratio,
        "pred_result": str(pred_result)[:200] if pred_result else None,  # Limit result size
        "gold_result": str(gold_result)[:200] if gold_result else None   # Limit result size
    }

def execute_parallel(query_pairs: List[Tuple[str, str]], db_paths: List[str], 
                     num_cpus: int = 1, iterations: int = 5) -> List[Dict[str, Any]]:
    """
    Execute SQL queries in parallel for faster evaluation.
    
    Args:
        query_pairs: List of (predicted_sql, gold_sql) pairs
        db_paths: List of database paths
        num_cpus: Number of CPU cores to use
        iterations: Number of iterations for timing measurement
        
    Returns:
        List of execution results
    """
    global _execution_results
    _execution_results = []
    
    pool = mp.Pool(processes=num_cpus)
    
    for i, (pred_sql, gold_sql) in enumerate(query_pairs):
        db_path = db_paths[i]
        pool.apply_async(
            iterated_execute_sql, 
            args=(pred_sql, gold_sql, db_path, iterations),
            callback=result_callback
        )
    
    pool.close()
    pool.join()
    
    # Sort results by index to maintain original order
    return sorted(_execution_results, key=lambda x: x.get('idx', i))

def compute_execution_accuracy(results: List[Dict[str, Any]]) -> float:
    """
    Compute Execution Accuracy (EX) from execution results.
    
    Args:
        results: List of execution results
        
    Returns:
        Execution accuracy score (0.0 to 1.0)
    """
    if not results:
        return 0.0
    
    matches = sum(1 for r in results if r.get("execution_match", False))
    return matches / len(results)

def compute_valid_efficiency_score(results: List[Dict[str, Any]]) -> float:
    """
    Compute Valid Efficiency Score (VES) from execution results.
    
    VES is calculated as the geometric mean of the square root of the time ratios
    for all correctly executed queries. Higher is better.
    
    Args:
        results: List of execution results
        
    Returns:
        Valid efficiency score
    """
    if not results:
        return 0.0
    
    # Filter for correct execution matches only
    valid_results = [r for r in results if r.get("execution_match", False)]
    
    if not valid_results:
        return 0.0
    
    # Calculate geometric mean of square root of time ratios
    # (time_ratio = gold_time / pred_time, higher means more efficient)
    product = 1.0
    count = 0
    
    for result in valid_results:
        time_ratio = result.get("time_ratio", 0)
        if time_ratio > 0:
            product *= math.sqrt(time_ratio)
            count += 1
    
    if count == 0:
        return 0.0
    
    # return geometric mean * 100 (scaled to 0-100 range)
    return pow(product, 1.0 / count) * 100

def compute_exact_match(pred_queries: List[str], gold_queries: List[str], 
                       db_ids: List[str], tables_json_path: str) -> float:
    """
    Compute Exact Match (EM) score using Spider's official evaluation.
    
    Args:
        pred_queries: List of predicted SQL queries
        gold_queries: List of gold standard SQL queries
        db_ids: List of database IDs corresponding to each query
        tables_json_path: Path to tables.json file
        
    Returns:
        Exact match score (0.0 to 1.0)
    """
    if not SPIDER_EVAL_AVAILABLE:
        print("Warning: Spider evaluation components not available. Returning 0.0 for Exact Match.")
        return 0.0
    
    if not os.path.exists(tables_json_path):
        print(f"Warning: tables.json file not found at {tables_json_path}. Returning 0.0 for Exact Match.")
        return 0.0
    
    if len(pred_queries) != len(gold_queries) or len(pred_queries) != len(db_ids):
        print("Warning: Mismatched number of queries and database IDs. Returning 0.0 for Exact Match.")
        return 0.0
    
    # Load database schemas
    kmaps = build_foreign_key_map_from_json(tables_json_path)
    
    # Initialize evaluator
    evaluator = Evaluator()
    
    # Evaluate each query pair
    correct = 0
    for i, (pred, gold, db_id) in enumerate(zip(pred_queries, gold_queries, db_ids)):
        schema = Schema(get_schema(db_id, tables_json_path))
        
        try:
            gold_ast = get_sql(schema, gold)
            pred_ast = get_sql(schema, pred)
            
            exact_match = evaluator.eval_exact_match(pred_ast, gold_ast)
            if exact_match:
                correct += 1
        except Exception as e:
            print(f"Error evaluating query {i} for exact match: {e}")
            continue
    
    return correct / len(pred_queries) if pred_queries else 0.0

def evaluate_mac_sql_execution_accuracy(pred_queries: List[str], gold_queries: List[str],
                                       db_ids: List[str], db_dir: str) -> float:
    """
    Compute Execution Accuracy (EX) using MAC-SQL's official evaluation.
    
    Args:
        pred_queries: List of predicted SQL queries
        gold_queries: List of gold standard SQL queries
        db_ids: List of database IDs corresponding to each query
        db_dir: Path to the database directory
        
    Returns:
        Execution accuracy score (0.0 to 1.0)
    """
    if not SPIDER_EVAL_AVAILABLE:
        print("Warning: Spider evaluation components not available. Falling back to basic execution match.")
        return None
    
    correct = 0
    total = len(pred_queries)
    
    for i, (pred, gold, db_id) in enumerate(zip(pred_queries, gold_queries, db_ids)):
        # Skip empty or error predictions
        if not pred or pred == "ERROR":
            continue
            
        try:
            # Construct database path
            db_path = os.path.join(db_dir, db_id, f"{db_id}.sqlite")
            
            # Use MAC-SQL's eval_exec_match function
            # 0 means execution match, 1 means no match
            result = eval_exec_match(
                db_path, 
                pred,
                gold,
                plug_value=False,
                keep_distinct=True,
                progress_bar_for_each_datapoint=False
            )
            
            # Convert result (0=match, 1=no match) to boolean (True=match)
            execution_match = (result == 0)
            
            if execution_match:
                correct += 1
                
        except Exception as e:
            print(f"Error evaluating query {i} for execution match: {e}")
            continue
    
    return correct / total if total > 0 else 0.0

def evaluate_queries(pred_queries: List[str], gold_queries: List[str], 
                    db_ids: List[str], db_dir: str, tables_json_path: str,
                    num_cpus: int = 1, iterations: int = 5) -> Dict[str, float]:
    """
    Evaluate the quality of predicted SQL queries using multiple metrics.
    
    Args:
        pred_queries: List of predicted SQL queries
        gold_queries: List of gold standard SQL queries
        db_ids: List of database IDs corresponding to each query
        db_dir: Directory containing the databases
        tables_json_path: Path to tables.json file
        num_cpus: Number of CPU cores to use for parallel execution
        iterations: Number of iterations for timing measurements
        
    Returns:
        Dictionary containing evaluation metrics:
        - exact_match: Exact Match (EM) score
        - execution_accuracy: Execution Accuracy (EX)
        - valid_efficiency_score: Valid Efficiency Score (VES)
    """
    if len(pred_queries) != len(gold_queries) or len(pred_queries) != len(db_ids):
        raise ValueError("Mismatched number of queries and database IDs")
    
    results = {}
    
    # Compute Exact Match (EM) using Spider's official evaluation
    results["exact_match"] = compute_exact_match(
        pred_queries, gold_queries, db_ids, tables_json_path
    )
    
    # First try to compute Execution Accuracy (EX) using MAC-SQL's official evaluation
    ex_result = evaluate_mac_sql_execution_accuracy(
        pred_queries, gold_queries, db_ids, db_dir
    )
    
    # If official evaluation is not available, fall back to our implementation
    if ex_result is None:
        # Prepare database paths
        db_paths = [os.path.join(db_dir, db_id, f"{db_id}.sqlite") for db_id in db_ids]
        
        # Execute queries in parallel
        execution_results = execute_parallel(
            list(zip(pred_queries, gold_queries)),
            db_paths,
            num_cpus=num_cpus,
            iterations=iterations
        )
        
        # Compute Execution Accuracy (EX)
        results["execution_accuracy"] = compute_execution_accuracy(execution_results)
        
        # Compute Valid Efficiency Score (VES)
        results["valid_efficiency_score"] = compute_valid_efficiency_score(execution_results)
    else:
        # Use the result from MAC-SQL's official evaluation
        results["execution_accuracy"] = ex_result
        
        # For VES, we still need our own implementation since MAC-SQL doesn't have it
        # Prepare database paths
        db_paths = [os.path.join(db_dir, db_id, f"{db_id}.sqlite") for db_id in db_ids]
        
        # Execute queries in parallel
        execution_results = execute_parallel(
            list(zip(pred_queries, gold_queries)),
            db_paths,
            num_cpus=num_cpus,
            iterations=iterations
        )
        
        # Compute Valid Efficiency Score (VES)
        results["valid_efficiency_score"] = compute_valid_efficiency_score(execution_results)
    
    return results

def load_queries_from_file(file_path: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Load queries from a JSON file.
    
    Args:
        file_path: Path to JSON file containing queries
        
    Returns:
        Tuple of (pred_queries, gold_queries, db_ids)
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Extract queries and database IDs based on file format
    if isinstance(data, list):
        # Assume list of dictionaries with query information
        pred_queries = [item.get("predicted_sql", "") for item in data]
        gold_queries = [item.get("gold_sql", "") for item in data]
        db_ids = [item.get("db_id", "") for item in data]
    elif isinstance(data, dict):
        # Assume dictionary with 'results' key containing list of query information
        results = data.get("results", [])
        pred_queries = [item.get("predicted_sql", "") for item in results]
        gold_queries = [item.get("gold_sql", "") for item in results]
        db_ids = [item.get("db_id", "") for item in results]
    else:
        raise ValueError(f"Unsupported JSON format in {file_path}")
    
    return pred_queries, gold_queries, db_ids

def main():
    parser = argparse.ArgumentParser(description="Evaluate text-to-SQL model predictions")
    parser.add_argument("--pred_file", type=str, required=True, help="Path to predicted queries JSON file")
    parser.add_argument("--gold_file", type=str, help="Path to gold queries JSON file (if separate from pred_file)")
    parser.add_argument("--db_dir", type=str, required=True, help="Path to database directory")
    parser.add_argument("--tables_json", type=str, required=True, help="Path to tables.json file")
    parser.add_argument("--num_cpus", type=int, default=4, help="Number of CPU cores to use")
    parser.add_argument("--iterations", type=int, default=5, help="Number of iterations for timing measurements")
    parser.add_argument("--output", type=str, help="Path to output file for results")
    
    args = parser.parse_args()
    
    # Load queries
    if args.gold_file:
        # Load predicted and gold queries from separate files
        with open(args.pred_file, 'r') as f:
            pred_data = json.load(f)
        
        with open(args.gold_file, 'r') as f:
            gold_data = json.load(f)
        
        # Extract queries and database IDs
        pred_queries = [item.get("query", "") for item in pred_data]
        gold_queries = [item.get("query", "") for item in gold_data]
        db_ids = [item.get("db_id", "") for item in gold_data]
    else:
        # Load both predicted and gold queries from the same file
        pred_queries, gold_queries, db_ids = load_queries_from_file(args.pred_file)
    
    # Evaluate queries
    metrics = evaluate_queries(
        pred_queries=pred_queries,
        gold_queries=gold_queries,
        db_ids=db_ids,
        db_dir=args.db_dir,
        tables_json_path=args.tables_json,
        num_cpus=args.num_cpus,
        iterations=args.iterations
    )
    
    # Print metrics
    print(f"Exact Match (EM): {metrics['exact_match']*100:.2f}%")
    print(f"Execution Accuracy (EX): {metrics['execution_accuracy']*100:.2f}%")
    print(f"Valid Efficiency Score (VES): {metrics['valid_efficiency_score']:.2f}")
    
    # Save results to output file if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Results saved to {args.output}")

if __name__ == "__main__":
    main() 