#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import sys
import json

# --- Configuration ---
# IMPORTANT: Replace with your actual PostgreSQL connection details
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "ukraine_readonly",  # Replace with your username
    "password": "readonly_pass" # Replace with your password
}

# List of database names to process
DATABASE_NAMES = ["ресторан", "спортивний_клуб", "університет", "авіакомпанія", "бібліотека","інтернет_магазин", "лікарня", "туристичне_агентство"] # Add/remove DB names as needed

# --- SQL Queries ---
SQL_GET_TABLES = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;
"""

SQL_GET_COLUMNS = """
SELECT column_name, data_type, ordinal_position
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = %s
ORDER BY ordinal_position;
"""

SQL_GET_PRIMARY_KEYS = """
SELECT kcu.column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema = 'public'
  AND tc.table_name = %s;
"""

SQL_GET_FOREIGN_KEYS = """
SELECT
    kcu.column_name,  -- Column in the current table
    ccu.table_name AS foreign_table_name, -- The table this column references
    ccu.column_name AS foreign_column_name -- The column in the foreign table
FROM
    information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND tc.table_name = %s;
"""

# --- Main Logic ---
def get_schema_info(db_name, config):
    """Connects to a database and extracts schema information."""
    conn = None
    schema = {"db_id": db_name, "tables": {}}
    try:
        print(f"\n--- Connecting to database: {db_name} ---")
        conn = psycopg2.connect(
            dbname=db_name,
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"]
        )
        cur = conn.cursor()
        print(" Connection successful.")

        # 1. Get Tables
        print(" Fetching tables...")
        cur.execute(SQL_GET_TABLES)
        tables = [row[0] for row in cur.fetchall()]
        print(f"  Found tables: {tables}")
        schema["table_names"] = tables # Store for later formatting

        # 2. Get Info for Each Table
        for table_name in tables:
            print(f"  Processing table: {table_name}")
            schema["tables"][table_name] = {}

            # 2a. Get Columns
            cur.execute(SQL_GET_COLUMNS, (table_name,))
            columns_data = cur.fetchall()
            schema["tables"][table_name]["columns"] = [
                {"name": c[0], "type": c[1], "position": c[2]} for c in columns_data
            ]
            print(f"   Columns: {schema['tables'][table_name]['columns']}")


            # 2b. Get Primary Keys
            cur.execute(SQL_GET_PRIMARY_KEYS, (table_name,))
            pk_data = cur.fetchall()
            schema["tables"][table_name]["primary_keys"] = [pk[0] for pk in pk_data]
            print(f"   Primary Keys: {schema['tables'][table_name]['primary_keys']}")

            # 2c. Get Foreign Keys
            cur.execute(SQL_GET_FOREIGN_KEYS, (table_name,))
            fk_data = cur.fetchall()
            schema["tables"][table_name]["foreign_keys"] = [
                 {"column": fk[0], "references_table": fk[1], "references_column": fk[2]} for fk in fk_data
            ]
            print(f"   Foreign Keys: {schema['tables'][table_name]['foreign_keys']}")


        cur.close()
        return schema

    except psycopg2.OperationalError as e:
        print(f" ERROR connecting to {db_name}: {e}", file=sys.stderr)
        print(" Please check connection details (host, port, user, password, dbname) and ensure the server is running.", file=sys.stderr)
        return None
    except Exception as e:
        print(f" ERROR processing {db_name}: {e}", file=sys.stderr)
        return None
    finally:
        if conn:
            conn.close()
            print(f" Connection to {db_name} closed.")

# --- Script Execution ---
if __name__ == "__main__":
    all_schemas = []
    print("Starting schema extraction...")
    print("Ensure 'psycopg2' library is installed (`pip install psycopg2-binary`)")

    for dbname in DATABASE_NAMES:
        db_schema = get_schema_info(dbname, DB_CONFIG)
        if db_schema:
            all_schemas.append(db_schema)

    print("\n--- Schema Extraction Complete ---")

    output_filename = "extracted_schema_raw.json"
    print(f"Saving raw extracted data to: {output_filename}")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_schemas, f, indent=4, ensure_ascii=False)
        print("Successfully saved raw schema data.")
    except Exception as e:
        print(f" ERROR saving data to {output_filename}: {e}", file=sys.stderr)


    # At this point, 'all_schemas' contains the raw data saved to the file.
    # You would later add code here to format 'all_schemas' into the final tables.json structure.
    # print("\nRaw extracted data:")
    # Optional: Print the collected data structure
    # print(json.dumps(all_schemas, indent=4, ensure_ascii=False))

    print("\nNext step: Implement formatting logic to convert this raw data (from the file) into the specific tables.json format.") 