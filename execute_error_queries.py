import json
import psycopg2
import os
import sys
import datetime
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
INPUT_JSON_PATH = "bird-ukr/questions/generated_all_questions.json"
OUTPUT_JSON_PATH = "bird-ukr/error_query_results.json"

# --- Environment Variable Check ---
# Ensure necessary environment variables are set
required_env_vars = ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file for PGHOST, PGPORT, PGUSER, and PGPASSWORD.")
    sys.exit(1) # Exit if configuration is missing

# --- Custom JSON encoder to handle PostgreSQL-specific types ---
class PostgreSQLJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        if isinstance(obj, datetime.date):
            return obj.isoformat()  # Convert date to ISO format string
        if isinstance(obj, datetime.time):
            return obj.isoformat()  # Convert time to ISO format string
        if isinstance(obj, bytes):
            return obj.decode('utf-8')  # Convert bytes to string
        # Let the base class default method handle other types
        return super().default(obj)

# --- Functions ---

def execute_query(db_name, sql_query):
    """Connects to the PostgreSQL database, executes the query, and returns results."""
    results = {"columns": [], "rows": [], "success": True, "error_message": None, "error_details": None}
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
        # Capture detailed error information
        results["success"] = False
        results["error_message"] = str(e)
        results["error_details"] = {
            "pgcode": getattr(e, 'pgcode', None),
            "pgerror": getattr(e, 'pgerror', None),
            "diag": {
                "message_primary": getattr(e.diag, 'message_primary', None) if hasattr(e, 'diag') else None,
                "message_detail": getattr(e.diag, 'message_detail', None) if hasattr(e, 'diag') else None,
                "message_hint": getattr(e.diag, 'message_hint', None) if hasattr(e, 'diag') else None,
                "statement_position": getattr(e.diag, 'statement_position', None) if hasattr(e, 'diag') else None,
                "context": getattr(e.diag, 'context', None) if hasattr(e, 'diag') else None,
                "schema_name": getattr(e.diag, 'schema_name', None) if hasattr(e, 'diag') else None,
                "table_name": getattr(e.diag, 'table_name', None) if hasattr(e, 'diag') else None,
                "column_name": getattr(e.diag, 'column_name', None) if hasattr(e, 'diag') else None,
                "datatype_name": getattr(e.diag, 'datatype_name', None) if hasattr(e, 'diag') else None,
                "constraint_name": getattr(e.diag, 'constraint_name', None) if hasattr(e, 'diag') else None
            }
        }
        return results  # Return the results with error information instead of None
    finally:
        if conn:
            conn.close()
    return results

def main():
    """Main function to read JSON, execute queries, and save only failed queries."""
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

    error_results = {}

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
        
        # Only include results where an error occurred
        if not query_result["success"]:
            error_results[question_id] = {
                "query_result": query_result,
                "db_id": db_id,
                "gold_sql": gold_sql,
                "question": item.get("question", "")
            }

    # Write output JSON with custom encoder to handle PostgreSQL types
    try:
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(error_results, f, ensure_ascii=False, indent=4, cls=PostgreSQLJSONEncoder)
        print(f"Successfully saved error results to {OUTPUT_JSON_PATH}")
        print(f"Found {len(error_results)} queries with errors out of {len(all_questions)} total queries.")
    except IOError as e:
        print(f"Error writing output JSON to {OUTPUT_JSON_PATH}: {e}")

# --- Entry Point ---
if __name__ == "__main__":
    main() 