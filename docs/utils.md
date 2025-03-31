# Documentation for core/utils.py

This module provides a collection of utility functions used throughout the MAC-SQL application. These functions cover various tasks including data validation, file manipulation, text parsing (JSON, SQL), schema extraction, and data loading/saving.

## Purpose

To centralize common helper functions, promoting code reuse and keeping the main logic in other modules (like agents) cleaner and more focused on their specific tasks.

## Key Functions

### Data Validation & Checking

*   `is_valid_date(date_str)`: Checks if a string represents a valid date in 'YYYY-MM-DD' format.
*   `is_valid_date_column(col_value_lst)`: Checks if all values in a list are valid dates using `is_valid_date`.
*   `is_email(string)`: Checks if a string matches a basic email pattern using regex.
*   `check_selector_response(json_data: Dict) -> bool`: Validates the structure and content of the JSON response expected from the `Selector` agent (checking for 'keep_all', 'drop_all', or list values).

### File & Directory Operations

*   `rename_file(file_path, new_name)`: Renames a file, adding a timestamp to the `new_name` to ensure uniqueness.
*   `get_files(root, suffix)`: Recursively finds all files with a given `suffix` within a specified `root` directory.
*   `read_txt_file(path)`: Reads a text file into a list of strings, stripping whitespace and removing empty lines.
*   `load_json_file(path)`: Loads data from a JSON file.
*   `load_jsonl_file(path)`: Loads data from a JSON Lines (.jsonl) file, where each line is a separate JSON object.
*   `append_file(path, string_lst)`: Appends a list of strings to a file, ensuring each string ends with a newline. Creates the directory if it doesn't exist.
*   `save_file(path, string_lst)`: Saves a list of strings to a file, overwriting existing content.
*   `save_json_file(path, data)`: Saves Python data structures (like dicts or lists) to a JSON file with indentation.
*   `save_jsonl_file(path, data)`: Saves a list of JSON-serializable objects to a JSON Lines file.

### Text & Message Parsing

*   `extract_world_info(message_dict: dict)`: Extracts common informational fields (like `idx`, `db_id`, `query`, `evidence`, etc.) from an agent message dictionary into a new dictionary.
*   `replace_multiple_spaces(text)`: Replaces sequences of multiple whitespace characters with a single space.
*   `parse_json(text: str) -> dict`: Extracts and parses a JSON block enclosed in ```json ... ``` markers within a larger string. Includes a call to `check_selector_response` for validation. Returns an empty dict if parsing or validation fails. *Note: There seem to be two definitions of `parse_json` in the provided code; the second one is likely the intended active version.*
*   `parse_sql(res: str) -> str`: A simpler SQL parser that ensures the result starts with 'SELECT' and replaces newlines with spaces. *Note: This seems less robust than `parse_sql_from_string`.*
*   `parse_sql_from_string(input_string)`: Extracts the content of the *last* SQL code block (```sql ... ```) found within a string using regex. Returns an error string if no SQL block is found.
*   `parse_single_sql(res: str) -> str`: Extracts the content of the *first* markdown code block (``` ... ```) found in a string.
*   `parse_qa_pairs(res: str, end_pos=2333) -> list`: Parses a string (typically LLM output) to find sub-question/SQL pairs based on a pattern (`Sub question X:`) followed by a ```sql ... ``` block.
*   `parse_subq(res: str) -> list`: Splits a string based on '-- ' delimiters, likely intended to extract sub-questions from a formatted comment block.
*   `add_prefix(sql)`: Ensures an SQL string starts with 'SELECT' (case-insensitive).

### Database Schema & SQL Analysis

*   `extract_table_names(sql_query)`: Extracts table names mentioned in FROM and JOIN clauses of an SQL query using regex. *Note: This appears less robust than `extract_tables_from_sql`.*
*   `get_used_tables(sql, db_path) -> dict`: Extracts tables used in an SQL query and lists all their columns (doesn't identify specific columns used).
*   `get_all_tables(db_path) -> dict`: Extracts all tables and their columns from a database schema.
*   `get_gold_columns(idx, db_path) -> dict`: Retrieves pre-defined "gold standard" relevant columns for a specific question index (`idx`) from a hardcoded file path (`data/bird/dev_gold_schema.json`) and combines them with a few random unused columns. Used for evaluation or specific modes in the BIRD dataset context.
*   `eval_hardness(sql)`: Evaluates the complexity ("easy", "medium", "hard", "extra") of a parsed SQL structure (likely from the Spider dataset's format) based on counts of different clauses, operators, and nesting. Functions like `get_nestedSQL`, `has_agg`, `count_agg`, `count_component1`, `count_component2`, `count_others` support this evaluation.
*   `extract_db_schema(data_path, db_id)`: Connects to a SQLite database and extracts its schema (tables and columns with types).
*   `extract_tables_from_sql(sql_query)`: A more robust function using regex to extract table names from FROM and JOIN clauses, handling potential aliases.
*   `extract_tables_from_schema(schema_dict)`: Simple utility to get a list of table names (keys) from a schema dictionary.
*   `format_schema_for_llm(schema_dict)`: Formats a schema dictionary into a plain text representation suitable for including in LLM prompts.

## Dependencies

*   `core.const`: Imports `subq_pattern`.
*   Standard libraries: `os`, `re`, `random`, `json`, `time`, `sqlite3`, `typing`.
