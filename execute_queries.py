import json
import psycopg2
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
INPUT_JSON_PATH = "bird-ukr/all_questions.json"
OUTPUT_JSON_PATH = "bird-ukr/query_results.json"

# --- Environment Variable Check ---
# Ensure necessary environment variables are set
required_env_vars = ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file for PGHOST, PGPORT, PGUSER, and PGPASSWORD.")
    sys.exit(1) # Exit if configuration is missing

# --- Functions ---

def execute_query(db_name, sql_query):
    """Connects to the PostgreSQL database, executes the query, and returns results."""
    results = {"columns": [], "rows": []}
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=os.environ.get("PGUSER"),
            password=os.environ.get("PGPASSWORD"),
            host=os.environ.get("PGHOST"),
            port=os.environ.get("PGPORT")
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # Fetch column names if the query returned results
        if cursor.description:
            results["columns"] = [description[0] for description in cursor.description]

        # Fetch all rows if the query returned results
        if cursor.rowcount > 0 or cursor.description: # Check if there might be rows or if columns exist
             try:
                 results["rows"] = cursor.fetchall()
             except psycopg2.ProgrammingError:
                 # Handle cases like 'no results to fetch' for statements like INSERT/UPDATE
                 # or DDL commands which might not return rows but do have descriptions.
                 results["rows"] = []
        else:
            results["rows"] = [] # Ensure rows is always a list

    except psycopg2.Error as e:
        print(f"Error connecting to or querying database '{db_name}': {e}")
        print(f"Query: {sql_query}")
        # Consider returning a specific error structure or None
        # For now, return None to indicate failure
        return None
    finally:
        if conn:
            conn.close()
    return results

def main():
    """Main function to read JSON, execute queries, and save results."""
    # Read input JSON
    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input JSON file not found at {INPUT_JSON_PATH}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {INPUT_JSON_PATH}")
        return

    all_results = {}

    # Process each question
    for item in all_questions:
        question_id = item.get("question_id")
        db_id = item.get("db_id") # This is the database name for PostgreSQL
        gold_sql = item.get("gold_sql")

        if not all([question_id, db_id, gold_sql]):
            print(f"Skipping item due to missing fields: {item}")
            continue

        print(f"Executing query for {question_id} on database '{db_id}'...")
        query_result = execute_query(db_id, gold_sql)

        if query_result is not None:
            all_results[question_id] = query_result
        else:
            # Indicate error in output?
            all_results[question_id] = {"error": f"Failed to execute query on database {db_id}"}

    # Write output JSON
    try:
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=4)
        print(f"Successfully saved results to {OUTPUT_JSON_PATH}")
    except IOError as e:
        print(f"Error writing output JSON to {OUTPUT_JSON_PATH}: {e}")

# --- Entry Point ---
if __name__ == "__main__":
    main() 