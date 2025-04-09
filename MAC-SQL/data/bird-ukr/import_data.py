# save as import_data.py
import psycopg2
import os
import sys

# Get the database name as UTF-8
db_name = "університет"  # This will be preserved correctly in Python
script_dir = r"F:\univ\praktika\projects\slowdown-macsql\MAC-SQL\data\bird-ukr\database\університет"

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="superuser",  # Replace with your actual password
    dbname=db_name
)
conn.autocommit = True
cursor = conn.cursor()

# Execute the schema file first
with open(os.path.join(script_dir, "schema.sql"), 'r', encoding='utf-8') as f:
    schema_sql = f.read()
    print("Executing schema.sql...")
    cursor.execute(schema_sql)

# Define the order of data files to execute
file_order = [
    "data_faculties.sql",
    "data_departments.sql",
    "data_teachers.sql", 
    "data_managers_update.sql",
    "data_students.sql",
    "data_courses.sql",
    "data_research.sql",  # Should contain публікації table
    "data_schedules.sql",
    "data_grades.sql",
    "data_scholarships.sql",
    "data_library.sql",
    "data_conferences.sql"  # Execute after публікації table is created
]

# Execute files in the specified order
for file in file_order:
    file_path = os.path.join(script_dir, file)
    if os.path.exists(file_path):
        print(f"Executing {file}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data_sql = f.read()
            try:
                cursor.execute(data_sql)
                print(f"Successfully executed {file}")
            except Exception as e:
                print(f"Error executing {file}: {e}")
                conn.rollback()
                # Don't exit, try to continue with other files
    else:
        print(f"Warning: File {file} not found, skipping")

# Process any remaining data files that might not be in the list
for file in os.listdir(script_dir):
    if file.startswith("data") and file.endswith(".sql") and file not in file_order:
        print(f"Executing additional file {file}...")
        with open(os.path.join(script_dir, file), 'r', encoding='utf-8') as f:
            data_sql = f.read()
            try:
                cursor.execute(data_sql)
                print(f"Successfully executed {file}")
            except Exception as e:
                print(f"Error executing {file}: {e}")
                conn.rollback()

print("Import complete!")