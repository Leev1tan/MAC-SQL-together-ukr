"""
Benchmark Script for BIRD-UKR

This script evaluates language models on the BIRD-UKR benchmark using both
Exact Match (EM) and Execution (EX) accuracy metrics.

Usage:
    python benchmark.py --model_name "model-name" --api_key "your-api-key" 
                        [--output_file "results.json"] [--sample_size 100]
                        [--temperature 0.1] [--max_tokens 1024]
"""

import os
import json
import argparse
import time
import sqlite3
import random
from tqdm import tqdm
import requests
import logging
from datetime import datetime

# Import evaluation functions
from evaluate_em import evaluate_exact_match
from evaluate_ex import evaluate_execution

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("evaluation/benchmark.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
API_URL = "https://api.together.xyz/v1/completions"
DEFAULT_PROMPT_TEMPLATE = """
Ви - асистент з генерації SQL-запитів на основі питань українською мовою.
Для заданої схеми бази даних та питання українською мовою, надайте мені ТІЛЬКИ SQL-запит,
без додаткових пояснень чи коментарів.

Схема бази даних:
{schema}

Питання: {question}

SQL запит:
"""

def load_questions(questions_file="bird-ukr/questions.json"):
    """Load questions from the BIRD-UKR dataset."""
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        logger.info(f"Loaded {len(questions)} questions from {questions_file}")
        return questions
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []

def load_table_schema(db_id, tables_file="bird-ukr/tables.json"):
    """Load schema information for a specific database."""
    try:
        with open(tables_file, 'r', encoding='utf-8') as f:
            tables_data = json.load(f)
        
        if db_id not in tables_data:
            logger.error(f"Database {db_id} not found in tables.json")
            return ""
        
        db_schema = tables_data[db_id]
        schema_text = "Таблиці:\n"
        
        # Add table information
        for idx, table in enumerate(db_schema["table_names"]):
            schema_text += f"- {table}\n"
            
            # Find columns for this table
            table_columns = []
            for col_idx, (tab_idx, col_name) in enumerate(db_schema["column_names"]):
                if tab_idx == idx:
                    col_type = db_schema["column_types"][col_idx]
                    is_pk = col_idx in db_schema.get("primary_keys", [])
                    pk_mark = "PK" if is_pk else ""
                    table_columns.append(f"  - {col_name} ({col_type}) {pk_mark}")
            
            schema_text += "\n".join(table_columns) + "\n\n"
        
        # Add foreign key information
        if "foreign_keys" in db_schema and db_schema["foreign_keys"]:
            schema_text += "Зовнішні ключі:\n"
            for fk in db_schema["foreign_keys"]:
                from_col = db_schema["column_names"][fk[0]][1]
                from_table = db_schema["table_names"][db_schema["column_names"][fk[0]][0]]
                to_col = db_schema["column_names"][fk[1]][1]
                to_table = db_schema["table_names"][db_schema["column_names"][fk[1]][0]]
                schema_text += f"- {from_table}.{from_col} → {to_table}.{to_col}\n"
                
        return schema_text
    except Exception as e:
        logger.error(f"Error loading schema: {e}")
        return ""

def call_model_api(prompt, model_name, api_key, temperature=0.1, max_tokens=1024):
    """Call the Together.ai API to generate SQL from a prompt."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_name,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stop": [";", "\n\n"]
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["text"].strip()
        else:
            logger.error(f"Unexpected API response format: {result}")
            return ""
    except Exception as e:
        logger.error(f"API call error: {e}")
        return ""

def run_benchmark(model_name, api_key, output_file, sample_size=None, temperature=0.1, max_tokens=1024):
    """Run the benchmark evaluation."""
    results = {
        "model": model_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "sample_size": sample_size
        },
        "metrics": {
            "overall_em": 0,
            "overall_ex": 0,
            "simple_em": 0,
            "simple_ex": 0,
            "medium_em": 0,
            "medium_ex": 0,
            "complex_em": 0,
            "complex_ex": 0,
        },
        "details": []
    }
    
    # Load questions
    questions = load_questions()
    if not questions:
        return
    
    # Sample questions if specified
    if sample_size and sample_size < len(questions):
        logger.info(f"Sampling {sample_size} questions from {len(questions)} total")
        questions = random.sample(questions, sample_size)
    
    # Count questions by difficulty
    difficulty_counts = {"simple": 0, "medium": 0, "complex": 0}
    for q in questions:
        difficulty_counts[q["difficulty"]] += 1
    
    logger.info(f"Running benchmark with {len(questions)} questions")
    logger.info(f"Difficulty distribution: {difficulty_counts}")
    
    # Track correct counts
    correct_em = {"all": 0, "simple": 0, "medium": 0, "complex": 0}
    correct_ex = {"all": 0, "simple": 0, "medium": 0, "complex": 0}
    
    # Process each question
    for q in tqdm(questions, desc="Evaluating questions"):
        question_id = q["question_id"]
        db_id = q["db_id"]
        question_text = q["question"]
        gold_sql = q["gold_sql"]
        difficulty = q["difficulty"]
        
        # Get schema for this database
        schema_text = load_table_schema(db_id)
        
        # Create prompt
        prompt = DEFAULT_PROMPT_TEMPLATE.format(
            schema=schema_text,
            question=question_text
        )
        
        # Call API
        start_time = time.time()
        generated_sql = call_model_api(
            prompt, model_name, api_key, temperature, max_tokens
        )
        api_time = time.time() - start_time
        
        if not generated_sql:
            logger.warning(f"Empty response for question {question_id}")
            continue
        
        # Evaluate EM
        em_score = evaluate_exact_match(generated_sql, gold_sql)
        
        # Evaluate EX
        db_path = os.path.join("bird-ukr", q["db_path"])
        ex_score, execution_error = 0, None
        try:
            ex_score = evaluate_execution(generated_sql, gold_sql, db_path)
        except Exception as e:
            execution_error = str(e)
            logger.warning(f"Execution error on {question_id}: {e}")
        
        # Record results
        result_detail = {
            "question_id": question_id,
            "db_id": db_id,
            "question": question_text,
            "gold_sql": gold_sql,
            "generated_sql": generated_sql,
            "em_score": em_score,
            "ex_score": ex_score,
            "difficulty": difficulty,
            "api_time": api_time,
            "execution_error": execution_error
        }
        results["details"].append(result_detail)
        
        # Update correct counts
        if em_score == 1:
            correct_em["all"] += 1
            correct_em[difficulty] += 1
        if ex_score == 1:
            correct_ex["all"] += 1
            correct_ex[difficulty] += 1
    
    # Calculate overall metrics
    if questions:
        results["metrics"]["overall_em"] = correct_em["all"] / len(questions)
        results["metrics"]["overall_ex"] = correct_ex["all"] / len(questions)
        
        # Calculate metrics by difficulty
        for diff in ["simple", "medium", "complex"]:
            if difficulty_counts[diff] > 0:
                results["metrics"][f"{diff}_em"] = correct_em[diff] / difficulty_counts[diff]
                results["metrics"][f"{diff}_ex"] = correct_ex[diff] / difficulty_counts[diff]
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Benchmark complete. Results saved to {output_file}")
    logger.info(f"Overall EM: {results['metrics']['overall_em']:.2f}, EX: {results['metrics']['overall_ex']:.2f}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="BIRD-UKR Benchmark Evaluation")
    parser.add_argument("--model_name", required=True, help="Model name/path (e.g., meta-llama/Llama-3.3-70B-Instruct-Turbo)")
    parser.add_argument("--api_key", required=True, help="Together.ai API key")
    parser.add_argument("--output_file", default="evaluation/results/benchmark_results.json", help="Path to save results")
    parser.add_argument("--sample_size", type=int, help="Number of questions to sample (default: all)")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperature for generation")
    parser.add_argument("--max_tokens", type=int, default=1024, help="Maximum number of tokens to generate")
    
    args = parser.parse_args()
    
    run_benchmark(
        args.model_name,
        args.api_key,
        args.output_file,
        args.sample_size,
        args.temperature,
        args.max_tokens
    )

if __name__ == "__main__":
    main() 