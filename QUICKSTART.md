# BIRD-UKR Quick Start Guide

This guide will help you quickly set up and run the MAC-SQL agent on the Ukrainian BIRD-UKR dataset.

## Prerequisites

1. PostgreSQL server installed and running
2. Python 3.8+ with pip
3. MAC-SQL repository cloned
4. BIRD-UKR dataset downloaded

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install psycopg2-binary  # For PostgreSQL support
```

### 2. Configure PostgreSQL Connection

Create or edit `.env` file in the project root with your PostgreSQL credentials:

```
PG_USER=postgres
PG_PASSWORD=your_password
PG_HOST=localhost
PG_PORT=5432
```

### 3. Setup Dataset Location

Place the BIRD-UKR dataset in a directory named `bird-ukr` in the project root, or set the environment variable:

```
BIRD_UKR_PATH=/path/to/bird-ukr
```

The directory should have the following structure:
```
bird-ukr/
  ├── questions.json        # Main questions file
  ├── tables.json           # Database schema definitions
  ├── column_meaning.json   # Column descriptions
  └── database/             # Database directories
      ├── інтернет_магазин/
      ├── авіакомпанія/
      ├── ...
```

## Running Evaluation

### Basic Run

Run the evaluation script with default settings:

```bash
python test_macsql_agent_bird_ukr.py
```

This will test 10 random questions and save results to `output/bird_ukr/{timestamp}/results.json`.

### Common Options

```bash
# Test on specific number of questions
python test_macsql_agent_bird_ukr.py --num-samples 20

# Test on specific databases
python test_macsql_agent_bird_ukr.py --db-filter інтернет_магазин авіакомпанія

# Use random sampling with a seed for reproducibility
python test_macsql_agent_bird_ukr.py --random --seed 42

# Specify output file location
python test_macsql_agent_bird_ukr.py --output results/my_results.json
```

### Agent Flow Visualization

To generate visualizations of the agent's decision process:

```bash
python test_macsql_agent_bird_ukr.py --visualize --viz-format html
```

Visualization formats include `html`, `json`, and `mermaid`.

## Understanding Results

The evaluation script measures:

1. **Execution Accuracy (EX)**: Whether the SQL query executes and produces the same results as the gold query
2. **Execution Time**: How long it takes to execute both predicted and gold queries
3. **Agent Processing Time**: How long the agent takes to generate SQL

Results are saved in a JSON file with the following structure:

```json
{
  "results": [
    {
      "question_id": "інтернет_магазин_001",
      "db_id": "інтернет_магазин",
      "question": "Question text in Ukrainian",
      "gold_sql": "Gold SQL query",
      "pred_sql": "Predicted SQL query",
      "execution_match": true,
      "gold_time": 0.0123,
      "pred_time": 0.0145,
      "agent_time": 3.456,
      "difficulty": "simple"
    },
    ...
  ],
  "summary": {
    "total_queries": 10,
    "execution_matches": 8,
    "execution_accuracy": 0.8,
    "avg_gold_time": 0.015,
    "avg_pred_time": 0.018
  }
}
```

## Troubleshooting

### PostgreSQL Connection Issues

If you encounter connection issues:

1. Verify PostgreSQL is running: `pg_isready -h localhost`
2. Check credentials in `.env` file
3. Ensure the databases are imported into PostgreSQL

### Missing tables.json or questions.json

The script expects the dataset to follow a specific structure. Verify that:

1. `questions.json` exists in your BIRD-UKR directory
2. `tables.json` exists in your BIRD-UKR directory
3. Database folders are in the `database/` subdirectory

For more detailed information, check the debug logs in the `logs/bird_ukr/{timestamp}/` directory. 