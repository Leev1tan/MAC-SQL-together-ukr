# BIRD-UKR Implementation Plan

## Overview

This document outlines the step-by-step implementation plan for completing the BIRD-UKR benchmark evaluation system. The plan is designed for junior developers and provides detailed instructions for each task.

## Prerequisites

Before starting, ensure you have:

- Python 3.8+ installed
- Git access to the project repository
- PostgreSQL 12+ installed and running
- Required Python packages: `psycopg2-binary`, `pandas`, `tqdm`, `numpy`, `matplotlib`

Install prerequisites with:

```bash
pip install psycopg2-binary pandas tqdm numpy matplotlib
```

## Phase 1: Evaluation Framework Setup

### Task 1.1: Create Evaluation Directory Structure

```bash
# Navigate to project root
cd /path/to/slowdown-macsql

# Create directories
mkdir -p evaluation/results
mkdir -p evaluation/visualizations
```

**Success Criteria**: Directory structure exists with proper permissions.

### Task 1.2: Move Evaluation Scripts

1. Move the existing evaluation scripts to the evaluation directory:

```bash
# Copy the scripts
cp scripts/evaluate_em.py evaluation/
cp scripts/evaluate_ex.py evaluation/
cp evaluate_metrics.py evaluation/
```

2. Verify that the scripts are properly moved and maintain their executable permissions:

```bash
chmod +x evaluation/evaluate_em.py
chmod +x evaluation/evaluate_ex.py
chmod +x evaluation/evaluate_metrics.py
```

**Success Criteria**: All three scripts are present in the evaluation directory and executable.

## Phase 2: PostgreSQL Adaptation

### Task 2.1: Update Database Connection Logic

1. Open `evaluation/evaluate_ex.py` and modify the database connection logic:

```python
def connect_to_database(db_path):
    """
    Підключається до бази даних PostgreSQL
    """
    # Extract database name from path
    db_name = os.path.basename(db_path)
    
    # Define connection parameters (from environment variables or config)
    params = {
        'dbname': db_name,
        'user': os.environ.get('PGUSER', 'postgres'),
        'password': os.environ.get('PGPASSWORD', ''),
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**params)
        return conn
    except Exception as e:
        print(f"Помилка підключення до бази даних: {e}")
        return None
```

2. Update any SQLite-specific code in the script to be compatible with PostgreSQL.

**Success Criteria**: The `connect_to_database` function successfully connects to a PostgreSQL database when given a valid database name.

### Task 2.2: Test PostgreSQL Connectivity

1. Create a simple test script to verify the connection:

```python
# evaluation/test_pg_connection.py
import os
import psycopg2
import sys

def test_connection(db_name):
    """Test PostgreSQL connection"""
    params = {
        'dbname': db_name,
        'user': os.environ.get('PGUSER', 'postgres'),
        'password': os.environ.get('PGPASSWORD', ''),
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**params)
        print(f"Successfully connected to database: {db_name}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pg_connection.py <database_name>")
        sys.exit(1)
    
    test_connection(sys.argv[1])
```

2. Run the test script with one of the BIRD-UKR databases:

```bash
python evaluation/test_pg_connection.py спортивний_клуб
```

**Success Criteria**: The script connects successfully to the specified database and displays a success message.

### Task 2.3: Update SQL Execution Logic

1. Modify the `execute_query` function in `evaluation/evaluate_ex.py`:

```python
def execute_query(conn, query):
    """
    Виконує SQL-запит і повертає результат
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        # For SELECT queries, fetch results
        if query.strip().lower().startswith(('select', 'with')):
            result = cursor.fetchall()
            cursor.close()
            return result
        # For non-SELECT queries
        else:
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
    except Exception as e:
        print(f"Помилка виконання запиту: {e}")
        print(f"Запит: {query}")
        return None
```

**Success Criteria**: The function successfully executes different types of SQL queries on PostgreSQL.

## Phase 3: Benchmark Runner Implementation

### Task 3.1: Create Benchmark Configuration

1. Create a configuration file for the benchmark:

```python
# evaluation/config.py
import os

# Database connection parameters
PG_CONFIG = {
    'user': os.environ.get('PGUSER', 'postgres'),
    'password': os.environ.get('PGPASSWORD', ''),
    'host': os.environ.get('PGHOST', 'localhost'),
    'port': os.environ.get('PGPORT', '5432')
}

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIRD_UKR_DIR = os.path.join(PROJECT_ROOT, 'bird-ukr')
QUESTIONS_FILE = os.path.join(BIRD_UKR_DIR, 'all_questions.json')
TABLES_FILE = os.path.join(BIRD_UKR_DIR, 'tables.json')
COLUMN_MEANING_FILE = os.path.join(BIRD_UKR_DIR, 'column_meaning.json')
DATABASE_DIR = os.path.join(BIRD_UKR_DIR, 'database')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'evaluation', 'results')
VISUALIZATIONS_DIR = os.path.join(PROJECT_ROOT, 'evaluation', 'visualizations')

# Together.ai API configuration
TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY', '')
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Benchmark parameters
NUM_ITERATIONS = 5  # For timing measurements in VES
NUM_CPUS = 4  # For parallel execution
```

**Success Criteria**: The configuration file exists and contains all necessary parameters.

### Task 3.2: Create API Interface for LLM

1. Create a wrapper for the Together.ai API:

```python
# evaluation/model_api.py
import requests
import json
import time
from typing import Dict, Any, List
from .config import TOGETHER_API_KEY, MODEL_NAME

class TogetherAPIClient:
    """Wrapper for Together.ai API"""
    
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or TOGETHER_API_KEY
        self.model = model or MODEL_NAME
        self.api_url = "https://api.together.xyz/v1/completions"
        
    def generate_sql(self, question: str, db_schema: str) -> str:
        """
        Generate SQL query for a given question and database schema
        
        Args:
            question: Natural language question in Ukrainian
            db_schema: Database schema description
            
        Returns:
            Generated SQL query
        """
        prompt = self._create_prompt(question, db_schema)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.1,
            "top_p": 0.9,
            "stop": ["```", "</sql>"]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("choices", [{}])[0].get("text", "").strip()
            
            # Extract SQL from the response
            sql_query = self._extract_sql(generated_text)
            return sql_query
            
        except Exception as e:
            print(f"Error calling Together.ai API: {e}")
            return "ERROR"
    
    def _create_prompt(self, question: str, db_schema: str) -> str:
        """Create a prompt for the model"""
        return f"""### Інструкція
Ти маєш згенерувати SQL-запит для PostgreSQL для наступного питання на основі наданої схеми бази даних.
Видай тільки SQL-запит, без додаткових пояснень.

### Схема бази даних
{db_schema}

### Питання
{question}

### SQL-запит
```sql
"""
    
    def _extract_sql(self, text: str) -> str:
        """Extract SQL query from generated text"""
        # If text contains SQL code blocks, extract the content
        if "```sql" in text:
            parts = text.split("```sql")
            if len(parts) > 1:
                sql_parts = parts[1].split("```")
                return sql_parts[0].strip()
        
        # If no code blocks, return the whole text
        return text.strip()
```

**Success Criteria**: The API client successfully calls the Together.ai API and returns SQL queries.

### Task 3.3: Create Schema Loader

1. Create a utility to load database schemas and format them for the model:

```python
# evaluation/schema_loader.py
import json
import os
from typing import Dict, Any, List
from .config import TABLES_FILE, COLUMN_MEANING_FILE, DATABASE_DIR

def load_schema_for_db(db_id: str) -> str:
    """
    Load and format database schema for a specific database
    
    Args:
        db_id: Database identifier (e.g., 'спортивний_клуб')
        
    Returns:
        Formatted schema text suitable for LLM prompting
    """
    # Load tables.json
    with open(TABLES_FILE, 'r', encoding='utf-8') as f:
        tables_data = json.load(f)
    
    # Load column_meaning.json
    with open(COLUMN_MEANING_FILE, 'r', encoding='utf-8') as f:
        column_meanings = json.load(f)
    
    # Extract schema for specific database
    db_schema = tables_data.get(db_id, {})
    db_columns = column_meanings.get(db_id, {})
    
    if not db_schema:
        raise ValueError(f"Database '{db_id}' not found in tables.json")
    
    # Format the schema as text
    schema_text = f"База даних: {db_id}\n\n"
    
    # Add tables and columns
    for table_idx, table_name in enumerate(db_schema.get('table_names', [])):
        schema_text += f"Таблиця: {table_name}\n"
        
        # Get columns for this table
        table_columns = []
        for col_idx, (tab, col) in enumerate(db_schema.get('column_names', [])):
            if tab == table_name:
                col_type = db_schema.get('column_types', [])[col_idx] if col_idx < len(db_schema.get('column_types', [])) else "TEXT"
                meaning = db_columns.get(f"{table_name}.{col}", "")
                table_columns.append((col, col_type, meaning))
        
        # Add columns to schema text
        for col, col_type, meaning in table_columns:
            schema_text += f"  - {col} ({col_type})"
            if meaning:
                schema_text += f": {meaning}"
            schema_text += "\n"
        
        # Add primary key information
        primary_keys = []
        for pk_idx in db_schema.get('primary_keys', []):
            if pk_idx < len(db_schema.get('column_names', [])):
                tab, col = db_schema.get('column_names', [])[pk_idx]
                if tab == table_name:
                    primary_keys.append(col)
        
        if primary_keys:
            schema_text += f"  Первинний ключ: {', '.join(primary_keys)}\n"
        
        # Add foreign key information
        for fk_columns in db_schema.get('foreign_keys', []):
            if len(fk_columns) == 2:
                fk_col_idx, pk_col_idx = fk_columns
                if fk_col_idx < len(db_schema.get('column_names', [])) and pk_col_idx < len(db_schema.get('column_names', [])):
                    fk_tab, fk_col = db_schema.get('column_names', [])[fk_col_idx]
                    pk_tab, pk_col = db_schema.get('column_names', [])[pk_col_idx]
                    
                    if fk_tab == table_name:
                        schema_text += f"  Зовнішній ключ: {fk_col} -> {pk_tab}.{pk_col}\n"
        
        schema_text += "\n"
    
    return schema_text

def get_db_names() -> List[str]:
    """Get list of all database names in the benchmark"""
    with open(TABLES_FILE, 'r', encoding='utf-8') as f:
        tables_data = json.load(f)
    
    return list(tables_data.keys())
```

**Success Criteria**: The `load_schema_for_db` function returns a well-formatted schema text for a specified database.

### Task 3.4: Create Benchmark Runner

1. Create the main benchmark runner script:

```python
# evaluation/benchmark.py
import json
import os
import argparse
import time
from typing import Dict, Any, List, Tuple
from tqdm import tqdm
import psycopg2

from .config import QUESTIONS_FILE, RESULTS_DIR, TABLES_FILE, DATABASE_DIR
from .model_api import TogetherAPIClient
from .schema_loader import load_schema_for_db, get_db_names

# Import evaluation methods
from .evaluate_metrics import evaluate_queries
from .evaluate_em import compute_exact_match
from .evaluate_ex import evaluate_execution_accuracy

def load_questions(filepath: str = QUESTIONS_FILE, db_filter: str = None) -> List[Dict[str, Any]]:
    """
    Load questions from the questions file
    
    Args:
        filepath: Path to questions JSON file
        db_filter: Optional database ID to filter questions
        
    Returns:
        List of question dictionaries
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    if db_filter:
        questions = [q for q in questions if q.get('db_id') == db_filter]
    
    return questions

def generate_predictions(model_client: TogetherAPIClient, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate SQL predictions for all questions
    
    Args:
        model_client: Initialized API client
        questions: List of question dictionaries
        
    Returns:
        List of question dictionaries with predictions added
    """
    results = []
    
    for question in tqdm(questions, desc="Generating predictions"):
        question_id = question.get('question_id')
        question_text = question.get('question')
        db_id = question.get('db_id')
        
        # Load schema for this database
        schema_text = load_schema_for_db(db_id)
        
        # Generate SQL query
        start_time = time.time()
        predicted_sql = model_client.generate_sql(question_text, schema_text)
        generation_time = time.time() - start_time
        
        # Create result dictionary
        result = question.copy()
        result['predicted_sql'] = predicted_sql
        result['generation_time'] = generation_time
        
        results.append(result)
    
    return results

def evaluate_results(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate predictions using multiple metrics
    
    Args:
        predictions: List of question dictionaries with predictions
        
    Returns:
        Dictionary with evaluation metrics
    """
    # Extract relevant data for evaluation
    pred_queries = [p.get('predicted_sql', '') for p in predictions]
    gold_queries = [p.get('gold_sql', '') for p in predictions]
    db_ids = [p.get('db_id', '') for p in predictions]
    
    # Use the unified evaluation function from evaluate_metrics.py
    metrics = evaluate_queries(
        pred_queries=pred_queries,
        gold_queries=gold_queries,
        db_ids=db_ids,
        db_dir=DATABASE_DIR,
        tables_json_path=TABLES_FILE
    )
    
    # Add additional statistics
    metrics['total_questions'] = len(predictions)
    metrics['questions_by_db'] = {}
    metrics['questions_by_difficulty'] = {}
    
    # Count questions by database
    for db_id in set(db_ids):
        count = sum(1 for p in predictions if p.get('db_id') == db_id)
        metrics['questions_by_db'][db_id] = count
    
    # Count questions by difficulty
    for difficulty in ['simple', 'medium', 'complex']:
        count = sum(1 for p in predictions if p.get('difficulty') == difficulty)
        metrics['questions_by_difficulty'][difficulty] = count
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Run BIRD-UKR benchmark")
    parser.add_argument("--model", type=str, default=None, help="Model name to use")
    parser.add_argument("--db", type=str, help="Specific database to test on")
    parser.add_argument("--input", type=str, help="Path to pre-generated predictions")
    parser.add_argument("--output", type=str, help="Path to save results")
    
    args = parser.parse_args()
    
    # Create results directory if it doesn't exist
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Set output file path
    output_file = args.output
    if not output_file:
        model_name = args.model or "default"
        db_suffix = f"_{args.db}" if args.db else ""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(RESULTS_DIR, f"{model_name}{db_suffix}_{timestamp}.json")
    
    # Load questions
    questions = load_questions(db_filter=args.db)
    print(f"Loaded {len(questions)} questions")
    
    # Generate predictions or load pre-generated ones
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        print(f"Loaded {len(predictions)} predictions from {args.input}")
    else:
        # Initialize model client
        model_client = TogetherAPIClient(model=args.model)
        print(f"Initialized API client for model: {model_client.model}")
        
        # Generate predictions
        predictions = generate_predictions(model_client, questions)
        print(f"Generated {len(predictions)} predictions")
    
    # Evaluate results
    print("Evaluating results...")
    metrics = evaluate_results(predictions)
    
    # Save results
    result_data = {
        "metrics": metrics,
        "predictions": predictions
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {output_file}")
    
    # Print summary
    print("\nResults Summary:")
    print(f"Total Questions: {metrics['total_questions']}")
    print(f"Exact Match (EM): {metrics['exact_match']*100:.2f}%")
    print(f"Execution Accuracy (EX): {metrics['execution_accuracy']*100:.2f}%")
    if 'valid_efficiency_score' in metrics:
        print(f"Valid Efficiency Score (VES): {metrics['valid_efficiency_score']:.2f}")
    
    print("\nResults by Database:")
    for db_id, count in metrics['questions_by_db'].items():
        print(f"  {db_id}: {count} questions")
    
    print("\nResults by Difficulty:")
    for difficulty, count in metrics['questions_by_difficulty'].items():
        print(f"  {difficulty}: {count} questions")

if __name__ == "__main__":
    main()
```

**Success Criteria**: The benchmark script successfully loads questions, generates SQL predictions (or loads pre-generated ones), evaluates the results, and saves the metrics.

## Phase 4: Baseline Testing

### Task 4.1: Generate Baseline Results

1. Run the benchmark with Llama-3-70B:

```bash
# Set API key
export TOGETHER_API_KEY="your_api_key_here"

# Run benchmark
python -m evaluation.benchmark --model "meta-llama/Llama-3.3-70B-Instruct-Turbo" --output "evaluation/results/llama3_baseline.json"
```

2. For comparison, run with a second model if available (e.g., a smaller model):

```bash
python -m evaluation.benchmark --model "meta-llama/Llama-3.2-8B-Instruct-Turbo" --output "evaluation/results/llama3_8b_baseline.json"
```

**Success Criteria**: Successfully generate prediction results for at least one model and save the metrics.

## Phase 5: Results Visualization

### Task 5.1: Create Basic Visualization Script

1. Create a visualization script:

```python
# evaluation/visualize_results.py
import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any, List
from .config import RESULTS_DIR, VISUALIZATIONS_DIR

def load_results(results_files: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Load results from multiple files
    
    Args:
        results_files: List of result file paths
        
    Returns:
        Dictionary mapping model names to their results
    """
    results = {}
    
    for file_path in results_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Use filename as model name
            model_name = os.path.basename(file_path).split('_')[0]
            results[model_name] = data.get('metrics', {})
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return results

def plot_overall_metrics(results: Dict[str, Dict[str, Any]], output_file: str = None):
    """
    Plot overall metrics comparison between models
    
    Args:
        results: Dictionary mapping model names to their results
        output_file: Path to save the plot
    """
    models = list(results.keys())
    em_scores = [results[model].get('exact_match', 0) * 100 for model in models]
    ex_scores = [results[model].get('execution_accuracy', 0) * 100 for model in models]
    
    # Check if VES is available
    has_ves = all('valid_efficiency_score' in results[model] for model in models)
    ves_scores = [results[model].get('valid_efficiency_score', 0) for model in models] if has_ves else None
    
    x = np.arange(len(models))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, em_scores, width, label='Exact Match (EM)')
    rects2 = ax.bar(x + width/2, ex_scores, width, label='Execution Accuracy (EX)')
    
    if has_ves:
        # Create secondary y-axis for VES
        ax2 = ax.twinx()
        ax2.plot(x, ves_scores, 'r-', marker='o', label='Valid Efficiency Score (VES)')
        ax2.set_ylabel('VES Score')
        ax2.legend(loc='upper right')
    
    ax.set_xlabel('Models')
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('BIRD-UKR Benchmark Results')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(loc='upper left')
    
    ax.bar_label(rects1, padding=3, fmt='%.1f')
    ax.bar_label(rects2, padding=3, fmt='%.1f')
    
    fig.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_file}")
    else:
        plt.show()

def plot_by_difficulty(results: Dict[str, Dict[str, Any]], output_file: str = None):
    """
    Plot metrics by difficulty level
    
    Args:
        results: Dictionary mapping model names to their results
        output_file: Path to save the plot
    """
    # TODO: Implement plotting by difficulty
    # This requires additional processing of the predictions
    pass

def plot_by_database(results: Dict[str, Dict[str, Any]], output_file: str = None):
    """
    Plot metrics by database
    
    Args:
        results: Dictionary mapping model names to their results
        output_file: Path to save the plot
    """
    # TODO: Implement plotting by database
    # This requires additional processing of the predictions
    pass

def main():
    parser = argparse.ArgumentParser(description="Visualize BIRD-UKR benchmark results")
    parser.add_argument("--results", nargs='+', help="Paths to result files")
    parser.add_argument("--output_dir", type=str, default=VISUALIZATIONS_DIR, help="Directory to save visualizations")
    
    args = parser.parse_args()
    
    # Create visualizations directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load results
    results = load_results(args.results)
    print(f"Loaded results for {len(results)} models")
    
    # Generate visualizations
    plot_overall_metrics(
        results, 
        output_file=os.path.join(args.output_dir, "overall_metrics.png")
    )
    
    # Additional visualizations can be added here

if __name__ == "__main__":
    main()
```

**Success Criteria**: The script generates a graph comparing metrics across different models.

## Phase 6: Documentation Updates

### Task 6.1: Update README

1. Create or update the main README.md with instructions for running the benchmark:

```markdown
# BIRD-UKR Benchmark

## Setup and Running the Benchmark

### Prerequisites

1. Install required packages:
   ```
   pip install psycopg2-binary pandas tqdm numpy matplotlib
   ```

2. Set up PostgreSQL databases:
   - Import all 8 databases from the `bird-ukr/database` directory
   - Set environment variables for PostgreSQL connection:
     ```
     export PGUSER=your_username
     export PGPASSWORD=your_password
     export PGHOST=localhost
     export PGPORT=5432
     ```

### Running the Benchmark

1. To run the benchmark with a specific model:
   ```
   python -m evaluation.benchmark --model "model_name"
   ```

2. To test on a specific database:
   ```
   python -m evaluation.benchmark --model "model_name" --db "спортивний_клуб"
   ```

3. To use pre-generated predictions:
   ```
   python -m evaluation.benchmark --input "path/to/predictions.json"
   ```

### Visualizing Results

1. Generate visualization for multiple result files:
   ```
   python -m evaluation.visualize_results --results results/model1.json results/model2.json
   ```

## Metrics

The benchmark uses these key metrics:

1. **Exact Match (EM)**: Percentage of generated SQL queries that match the gold SQL queries after normalization.
2. **Execution Accuracy (EX)**: Percentage of generated SQL queries that produce the same results as the gold queries when executed.
3. **Valid Efficiency Score (VES)**: Measures the efficiency of correctly executing queries compared to the gold queries.

## Structure

- `bird-ukr/all_questions.json`: All questions with gold SQL queries
- `bird-ukr/tables.json`: Database schema definitions
- `bird-ukr/column_meaning.json`: Column descriptions
- `evaluation/`: Benchmark and evaluation scripts
- `evaluation/results/`: Benchmark results
- `evaluation/visualizations/`: Visualizations of results
```

**Success Criteria**: The README provides clear instructions for setting up and running the benchmark.

## Timeframe and Dependencies

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| 1. Evaluation Framework Setup | 1.1, 1.2 | 1 day | None |
| 2. PostgreSQL Adaptation | 2.1, 2.2, 2.3 | 2 days | Phase 1 |
| 3. Benchmark Runner Implementation | 3.1, 3.2, 3.3, 3.4 | 3 days | Phase 2 |
| 4. Baseline Testing | 4.1 | 1 day | Phase 3 |
| 5. Results Visualization | 5.1 | 1 day | Phase 4 |
| 6. Documentation Updates | 6.1 | 1 day | All previous phases |

Total estimated time: 9 days

## Testing Checklist

For each component:

- [ ] Evaluation scripts run successfully on a single question
- [ ] PostgreSQL connection works with all 8 databases
- [ ] API client correctly generates SQL for sample questions
- [ ] Schema loader correctly formats database schemas
- [ ] Benchmark runner successfully processes all questions
- [ ] Visualization script generates readable graphs
- [ ] Documentation is complete and accurate

## Future Improvements

- Implement more detailed error analysis
- Add support for more LLM providers
- Create a web interface for interactive testing
- Add support for few-shot prompting
- Implement cross-database generalization testing 