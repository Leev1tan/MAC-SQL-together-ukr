# MAC-SQL with Together AI

This integration allows you to use Together AI models with the MAC-SQL framework for text-to-SQL generation, with support for both BIRD and Spider datasets.

## Setup

1. Copy `.env.example` to `.env` and add your Together AI API key:
   ```
   TOGETHER_API_KEY=your_together_api_key_here
   TOGETHER_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
   USE_TOGETHER_AI=true
   ```

   Available models include:
   - `meta-llama/Llama-3.3-70B-Instruct-Turbo` (default)
   - `meta-llama/Meta-Llama-3.1-70B-Instruct`
   - `mistralai/Mixtral-8x7B-Instruct-v0.1`

2. Install the required packages:
   ```
   pip install together python-dotenv pandas
   ```

3. Make sure you have the BIRD dataset downloaded in the MAC-SQL data directory structure:
   ```
   MAC-SQL/data/bird/MINIDEV/mini_dev_sqlite.json
   MAC-SQL/data/bird/MINIDEV/dev_databases/
   ```

## Usage

### BIRD Testing

Run the test script with a specific number of samples:

```
python test_bird_with_together.py --num_samples 5
```

Command line arguments:
- `--num_samples <number>`: Number of samples to test (default: 1)
- `--model <model_name>`: Together AI model to use (overrides .env setting)

### Full MAC-SQL Usage

To use MAC-SQL with Together AI for a specific query:

```bash
python MAC-SQL/run.py --dataset_name bird --db_id concert_singer --query "How many singers do we have?"
```

To run on the entire BIRD mini development set:

```bash
python MAC-SQL/run.py --dataset_name bird --dataset_mode dev --input_file MAC-SQL/data/bird/MINIDEV/mini_dev_sqlite.json --db_path MAC-SQL/data/bird/MINIDEV/dev_databases --tables_json_path MAC-SQL/data/bird/MINIDEV/dev_tables.json --output_file MAC-SQL/output_bird.jsonl --log_file MAC-SQL/log_bird.txt
```

## Features

- **Schema Formatting**: Extracts database schemas and formats them as SQL CREATE statements
- **Sample Data**: Includes rows of sample data from each table to help the model understand the data
- **SQL Extraction**: Implements smart SQL extraction from the model's response
- **Evaluation Metrics**:
  - **Exact Match**: Checks if the generated SQL is exactly the same as the gold SQL (after normalization)
  - **Execution Accuracy (EX)**: Executes both the generated and gold SQL queries and compares the results
  - **Valid Efficiency Score (VES)**: *(Planned)* Measures the efficiency of valid SQL queries

## Output

Results are saved to `output/bird_together_results.json` with detailed information about each query, including:
- The database ID
- The original question
- Generated SQL
- Gold SQL
- Match status (exact and execution-based)

## Customization

You can customize the Together AI model by changing the `TOGETHER_MODEL` variable in your `.env` file.

Parameter recommendations for optimal SQL generation:
- `max_tokens`: 1024 (ensures enough space for complex queries)
- `temperature`: 0.1 (for deterministic, consistent output)
- `top_p`: 0.9 (allows controlled variation while maintaining precision)

## Debugging

Set `DEBUG_MODE=true` in your `.env` file or environment to enable verbose output, which helps with troubleshooting:
- API calls and responses
- SQL extraction details
- Schema formatting
- Database connections
- Query execution for evaluation

## Troubleshooting

1. **Missing API Key**: Ensure your Together AI API key is correctly set in the `.env` file
2. **Dataset Issues**: Verify that the BIRD dataset is properly downloaded and placed in the correct directories
3. **SQL Execution Errors**: Check debug output for SQL syntax errors or column name mismatches
4. **Missing Dependencies**: Ensure pandas is installed for execution-based evaluation

---

The integrated `run_with_together.py` script in the MAC-SQL directory can be imported and used in other parts of the MAC-SQL framework if needed. It provides all the functionality needed for Together AI integration. 