#!/usr/bin/env python3
"""
Test script for MAC-SQL that runs a small subset of queries from the BIRD mini dataset
and evaluates the results.
"""
import os
import sys
import json
import random
import subprocess
import shutil
import glob
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check Together AI setup
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo")
USE_TOGETHER_AI = os.getenv("USE_TOGETHER_AI", "true").lower() == "true"

def check_environment():
    """Check if the environment is properly set up."""
    if USE_TOGETHER_AI and not TOGETHER_API_KEY:
        print("Error: TOGETHER_API_KEY not found in .env file")
        return False
    
    # Check if BIRD mini dataset is available
    if not os.path.exists("MAC-SQL/data/bird/MINIDEV/mini_dev_sqlite.json"):
        print("Error: BIRD mini dataset not found in MAC-SQL/data/bird/MINIDEV")
        return False
    
    # Check if databases exist
    db_dirs = glob.glob("MAC-SQL/data/bird/MINIDEV/dev_databases/*")
    if not db_dirs:
        print("Error: No database directories found in MAC-SQL/data/bird/MINIDEV/dev_databases")
        return False
    
    print(f"Found {len(db_dirs)} database directories: {[os.path.basename(d) for d in db_dirs]}")
    return True

def create_subset_dataset(db_type="sqlite", num_samples=3, db_filter=None):
    """Create a small subset of queries from the BIRD mini dataset, optionally filtering by database."""
    # Define paths based on database type
    if db_type not in ["sqlite", "mysql", "postgresql"]:
        print(f"Error: Unsupported database type: {db_type}")
        return None
    
    source_path = f"MAC-SQL/data/bird/MINIDEV/mini_dev_{db_type}.json"
    output_path = f"MAC-SQL/data/bird/mini_dev_{db_type}_subset.json"
    
    # Load the original dataset
    try:
        with open(source_path, "r") as f:
            queries = json.load(f)
        
        # Filter by database if specified
        if db_filter:
            filtered_queries = [q for q in queries if q['db_id'] in db_filter]
            if not filtered_queries:
                print(f"Warning: No queries found for database(s): {db_filter}")
                filtered_queries = queries
            queries = filtered_queries
        
        # Select a small subset of queries
        if len(queries) > num_samples:
            subset = random.sample(queries, num_samples)
        else:
            subset = queries
        
        # Save the subset to a new file
        with open(output_path, "w") as f:
            json.dump(subset, f, indent=2)
        
        print(f"Created subset dataset with {len(subset)} queries at {output_path}")
        # Print selected databases for debugging
        dbs = [item['db_id'] for item in subset]
        print(f"Selected queries from databases: {set(dbs)}")
        return output_path
    
    except Exception as e:
        print(f"Error creating subset: {str(e)}")
        return None

def get_available_databases():
    """Get a list of available databases in the BIRD mini dataset."""
    db_dirs = os.listdir("MAC-SQL/data/bird/MINIDEV/dev_databases")
    return db_dirs

def run_macsql_subset(db_type="sqlite", num_samples=3):
    """Run MAC-SQL on a subset of the BIRD mini dataset."""
    # Get available databases
    available_dbs = get_available_databases()
    if not available_dbs:
        print("No databases available in the BIRD mini dataset")
        return False
    
    print(f"Available databases: {available_dbs}")
    
    # Create subset file, filtering for available databases
    subset_file = create_subset_dataset(db_type, num_samples, db_filter=available_dbs)
    if not subset_file:
        return False
    
    # Set up paths for BIRD dataset
    db_path = "MAC-SQL/data/bird/MINIDEV/dev_databases"
    tables_json_path = "MAC-SQL/data/bird/MINIDEV/dev_tables.json"
    output_file = f"MAC-SQL/output_bird_mini_{db_type}_subset.jsonl"
    log_file = f"MAC-SQL/log_bird_mini_{db_type}_subset.txt"
    eval_dir = "MAC-SQL/eval_results"
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    os.makedirs(eval_dir, exist_ok=True)
    
    # Build command
    cmd = [
        "python", "MAC-SQL/run.py",
        "--dataset_name", "bird",
        "--dataset_mode", "dev",
        "--input_file", subset_file,
        "--db_path", db_path,
        "--output_file", output_file,
        "--log_file", log_file
    ]
    
    # Add tables_json_path if it exists
    if os.path.exists(tables_json_path):
        cmd.extend(["--tables_json_path", tables_json_path])
    else:
        print(f"Warning: {tables_json_path} not found")
    
    print("\nRunning MAC-SQL with the following command:")
    print(" ".join(cmd))
    print("\n" + "=" * 80)
    
    try:
        # Run the command
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 80)
        print(f"MAC-SQL execution completed successfully!")
        print(f"Output saved to: {output_file}")
        print(f"Log saved to: {log_file}")
        
        # Check results from prediction file
        bird_pred_file = os.path.join(os.path.dirname(output_file), "predict_dev.json")
        if os.path.exists(bird_pred_file):
            with open(bird_pred_file, "r") as f:
                bird_results = json.load(f)
                
            if bird_results:
                print(f"\nFound {len(bird_results)} SQL predictions in BIRD format")
                
                # Display results
                for i, result in enumerate(bird_results, 1):
                    question = result[0]
                    sql_parts = result[1].split("----- bird -----")
                    pred_sql = sql_parts[0].strip()
                    db_id = sql_parts[1].strip() if len(sql_parts) > 1 else "unknown"
                    
                    print(f"\nResult {i}/{len(bird_results)}:")
                    print(f"Database: {db_id}")
                    print(f"Question: {question}")
                    print(f"Predicted SQL:")
                    print("-" * 40)
                    print(pred_sql)
                    print("-" * 40)
                
                # Now try to evaluate against gold SQL
                evaluate_bird_results(bird_pred_file, subset_file, db_type, eval_dir)
            else:
                print("No predictions found in the BIRD output file")
        else:
            print(f"Warning: BIRD prediction file not found at {bird_pred_file}")
            
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error running MAC-SQL: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def evaluate_bird_results(pred_file, input_file, db_type, eval_dir):
    """Evaluate BIRD-format prediction results against gold queries."""
    # Load gold queries
    gold_file = f"MAC-SQL/data/bird/MINIDEV/mini_dev_{db_type}_gold.sql"
    if not os.path.exists(gold_file):
        print(f"Error: Gold SQL file {gold_file} not found")
        return
    
    try:
        # Load predictions
        with open(pred_file, "r") as f:
            predictions = json.load(f)
        
        # Load input queries
        with open(input_file, "r") as f:
            input_queries = json.load(f)
        
        # Create a map of questions to their original data
        question_to_orig = {q["question"]: q for q in input_queries}
        
        # Load gold SQL
        with open(gold_file, "r") as f:
            gold_sql_content = f.read()
        
        # Parse the gold SQL file
        gold_entries = []
        current_entry = {"db": None, "question": None, "sql": []}
        
        for line in gold_sql_content.strip().split('\n'):
            if line.startswith('-- Database:'):
                if current_entry["db"] and current_entry["question"]:
                    gold_entries.append(current_entry.copy())
                current_entry = {"db": line.replace('-- Database:', '').strip(), "question": None, "sql": []}
            elif line.startswith('-- Question:'):
                if current_entry["db"] and current_entry["question"]:
                    gold_entries.append(current_entry.copy())
                current_entry["question"] = line.replace('-- Question:', '').strip()
                current_entry["sql"] = []
            elif current_entry["db"] and current_entry["question"]:
                current_entry["sql"].append(line)
        
        # Add the last entry
        if current_entry["db"] and current_entry["question"] and current_entry["sql"]:
            gold_entries.append(current_entry)
        
        # Create a map for gold queries
        gold_map = {entry["question"]: "\n".join(entry["sql"]).strip() for entry in gold_entries}
        
        # Evaluate predictions
        correct_count = 0
        total_count = len(predictions)
        evaluation_results = []
        
        print("\nEvaluation Results:")
        print("=" * 50)
        
        for i, pred in enumerate(predictions, 1):
            question = pred[0]
            sql_parts = pred[1].split("----- bird -----")
            pred_sql = sql_parts[0].strip()
            db_id = sql_parts[1].strip() if len(sql_parts) > 1 else "unknown"
            
            # Find the gold SQL
            gold_sql = gold_map.get(question, "Not found")
            
            # Simple exact match evaluation
            exact_match = normalize_sql(pred_sql) == normalize_sql(gold_sql)
            
            if exact_match:
                correct_count += 1
                status = "✅ CORRECT"
            else:
                status = "❌ INCORRECT"
            
            # Build result entry
            result = {
                "db_id": db_id,
                "question": question,
                "predicted_sql": pred_sql,
                "gold_sql": gold_sql,
                "exact_match": exact_match
            }
            
            evaluation_results.append(result)
            
            print(f"\nResult {i}/{total_count}: {status}")
            print(f"Database: {db_id}")
            print(f"Question: {question}")
            print(f"Predicted SQL:")
            print("-" * 40)
            print(pred_sql)
            print("-" * 40)
            print(f"Gold SQL:")
            print("-" * 40)
            print(gold_sql)
            print("-" * 40)
        
        # Calculate accuracy
        accuracy = correct_count / total_count if total_count > 0 else 0
        print(f"\nOverall Accuracy: {accuracy:.2%} ({correct_count}/{total_count})")
        
        # Save evaluation results
        eval_output = {
            "model": TOGETHER_MODEL,
            "db_type": db_type,
            "total_queries": total_count,
            "correct_queries": correct_count,
            "accuracy": accuracy,
            "results": evaluation_results
        }
        
        eval_output_file = os.path.join(eval_dir, f"eval_bird_mini_{db_type}_subset.json")
        with open(eval_output_file, "w") as f:
            json.dump(eval_output, f, indent=2)
        
        print(f"Detailed evaluation results saved to: {eval_output_file}")
        
    except Exception as e:
        print(f"Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

def normalize_sql(sql):
    """Normalize SQL for comparison."""
    if not sql:
        return ""
    
    # Convert to lowercase
    sql = sql.lower()
    
    # Remove extra spaces
    sql = " ".join(sql.split())
    
    # Remove trailing semicolons
    sql = sql.rstrip(";")
    
    return sql

def main():
    """Run a small test of MAC-SQL with a subset of the BIRD mini dataset."""
    if not check_environment():
        return
    
    print(f"Testing MAC-SQL with Together AI ({TOGETHER_MODEL})")
    print("=" * 80)
    
    # Default to SQLite for simplicity
    db_type = "sqlite"
    num_samples = 3  # Use a small number for quick testing
    
    success = run_macsql_subset(db_type, num_samples)
    
    if success:
        print(f"\nBIRD mini {db_type} test complete! MAC-SQL ran and was evaluated successfully.")
    else:
        print(f"\nBIRD mini {db_type} test failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 