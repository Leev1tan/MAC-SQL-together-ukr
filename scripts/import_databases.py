#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Import Script for BIRD-UKR Benchmark

This script automates the process of creating PostgreSQL databases and importing
data for each database in the BIRD-UKR benchmark collection.

Usage:
    python import_databases.py [--convert] [--cleanup] [--check] [--import]
    
Options:
    --convert  Convert MySQL syntax to PostgreSQL syntax
    --cleanup  Drop existing databases before import
    --check    Check PostgreSQL connection and create databases
    --import   Import schemas (default if no options provided)
    --help     Show this help message

Examples:
    python import_databases.py --convert --check --import
    python import_databases.py --cleanup --import
    python import_databases.py  # Just import
"""

import os
import subprocess
import sys
import psycopg2
from psycopg2 import sql
from getpass import getpass
import re
import argparse

# Configuration
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"  # Default PostgreSQL user, you may need to change this

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Database Import Script for BIRD-UKR Benchmark")
    parser.add_argument("--convert", action="store_true", help="Convert MySQL syntax to PostgreSQL syntax")
    parser.add_argument("--cleanup", action="store_true", help="Drop existing databases before import")
    parser.add_argument("--check", action="store_true", help="Check PostgreSQL connection and create databases")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import schemas (default if no options provided)")
    args = parser.parse_args()
    
    # If no actions specified, default to import
    if not (args.convert or args.cleanup or args.check or args.do_import):
        args.do_import = True
    
    return args

def convert_mysql_to_postgresql(file_path):
    """Convert MySQL syntax to PostgreSQL syntax in a schema file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create backup before modification
    backup_path = file_path + '.mysql.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created backup at {backup_path}")
    
    # Perform conversions
    # Replace AUTO_INCREMENT with SERIAL or BIGSERIAL
    content = re.sub(r'INT\s+AUTO_INCREMENT', 'SERIAL', content)
    content = re.sub(r'BIGINT\s+AUTO_INCREMENT', 'BIGSERIAL', content)
    
    # Replace ENUM types with VARCHAR and CHECK constraints
    enum_pattern = re.compile(r'ENUM\s*\(([^)]+)\)')
    
    def replace_enum(match):
        values = match.group(1)
        return f"VARCHAR CHECK ({{column_name}} IN ({values}))"
    
    content = enum_pattern.sub(replace_enum, content)
    
    # Find column definitions and properly replace the {column_name} placeholder
    column_pattern = re.compile(r'(\s*)(\w+)(\s+)(VARCHAR CHECK \(\{column_name\} IN \([^)]+\)\))')
    content = column_pattern.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}{m.group(4).replace('{column_name}', m.group(2))}", content)
    
    # Replace MySQL comments
    content = re.sub(r'COMMENT\s+\'([^\']+)\'', "-- \\1", content)
    
    # Write converted content back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Converted {file_path} to PostgreSQL syntax")
    return True

def convert_all_schemas(base_path, db_dirs=None):
    """Convert all schema files from MySQL to PostgreSQL syntax"""
    if db_dirs is None:
        # Get all database directories
        db_dirs = get_database_dirs(base_path)
    
    print(f"Converting {len(db_dirs)} schema files...")
    
    for db_dir in db_dirs:
        db_path = os.path.join(base_path, db_dir)
        schema_path = os.path.join(db_path, "schema.sql")
        
        if os.path.exists(schema_path):
            print(f"\nProcessing schema for {db_dir}...")
            convert_mysql_to_postgresql(schema_path)
        else:
            print(f"\nSchema file not found for {db_dir}")

def get_database_dirs(base_path):
    """Get all database directories"""
    return [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) 
            and not d.startswith('.') and not os.path.isfile(os.path.join(base_path, d, 'expansion_plan.md'))]

def create_database(db_name, user, password, host, port):
    """Create a PostgreSQL database"""
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="postgres"  # Connect to default database first
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cursor.fetchone()
    
    if not exists:
        # Create database with UTF-8 encoding
        cursor.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8' TEMPLATE template0").format(
            sql.Identifier(db_name)
        ))
        print(f"Database '{db_name}' created successfully")
    else:
        print(f"Database '{db_name}' already exists")
    
    cursor.close()
    conn.close()

def drop_database(db_name, user, password, host, port):
    """Drop a PostgreSQL database if it exists"""
    try:
        # Connect to the default postgres database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"  # Connect to default database first
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if exists:
            # Terminate existing connections
            cursor.execute(
                sql.SQL("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = %s
                AND pid <> pg_backend_pid()
                """), 
                (db_name,)
            )
            
            # Drop the database
            cursor.execute(sql.SQL("DROP DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"Database '{db_name}' dropped successfully")
        else:
            print(f"Database '{db_name}' does not exist")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error dropping database {db_name}: {str(e)}")
        return False

def verify_import_files(base_dir, import_file):
    """Verify all files referenced in the import script exist"""
    with open(import_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all \i 'filename.sql' patterns
    files = re.findall(r"\\i\s+'([^']+)'", content)
    missing_files = []
    
    for file in files:
        full_path = os.path.join(os.path.dirname(import_file), file)
        if not os.path.isfile(full_path):
            missing_files.append(file)
    
    return missing_files

def prepare_import_file(import_file, temp_dir):
    """Create a temporary copy of the import file with absolute paths"""
    base_dir = os.path.dirname(import_file)
    
    try:
        with open(import_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace relative paths with absolute paths
        def replace_path(match):
            file_name = match.group(1)
            full_path = os.path.abspath(os.path.join(base_dir, file_name))
            # Use forward slashes for PostgreSQL compatibility
            full_path = full_path.replace('\\', '/')
            return f"\\i '{full_path}'"
        
        modified_content = re.sub(r"\\i\s+'([^']+)'", replace_path, content)
        
        # Create temp file
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, os.path.basename(import_file))
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"Created temporary import file: {temp_file}")
        return temp_file
    except Exception as e:
        print(f"Error preparing import file: {str(e)}")
        raise
        
def import_data(db_name, import_file, user, password, host, port, psql_path="psql"):
    """Import data into PostgreSQL database using psql"""
    try:
        # First, check if the import file exists
        if not os.path.isfile(import_file):
            print(f"Error: Import file not found: {import_file}")
            return False
            
        # First, check if all the files referenced in the import script exist
        missing_files = verify_import_files(os.path.dirname(import_file), import_file)
        if missing_files:
            print(f"Error: The following files referenced in {import_file} are missing:")
            for file in missing_files:
                print(f"  - {file}")
            return False
        
        # Create temp directory if it doesn't exist
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(script_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create temporary import file with absolute paths
        try:
            temp_import_file = prepare_import_file(import_file, temp_dir)
        except Exception as e:
            print(f"Failed to prepare import file: {str(e)}")
            return False
        
        # Use psql to run the import file
        cmd = [
            psql_path,
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", db_name,
            "-f", temp_import_file
        ]
        
        # Set PGPASSWORD environment variable for password
        env = os.environ.copy()
        env["PGPASSWORD"] = password
        
        # Run the command
        print(f"Importing {import_file} into {db_name}...")
        print(f"Running command: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Clean up temp file
        try:
            os.remove(temp_import_file)
        except:
            pass
        
        print(f"Import completed successfully for {db_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error importing {db_name}: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error importing {db_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def import_with_psycopg2(db_name, schema_file, user, password, host, port):
    """Import a schema file directly using psycopg2"""
    try:
        # Read the schema file
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Execute the schema
        print(f"Importing schema directly with psycopg2: {schema_file}")
        cursor.execute(schema_sql)
        
        # Close the connection
        cursor.close()
        conn.close()
        
        print(f"Schema imported successfully for {db_name}")
        return True
    except Exception as e:
        print(f"Error importing schema with psycopg2: {str(e)}")
        return False

def check_postgres_connection(host, port, user, password):
    """Check if PostgreSQL server is running and accessible"""
    try:
        # Try to connect to the default 'postgres' database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname="postgres"
        )
        conn.close()
        print("\n✅ Successfully connected to PostgreSQL server!")
        return True
    except Exception as e:
        print(f"\n⚠️ Error connecting to PostgreSQL: {e}")
        print("Please check that:")
        print("1. PostgreSQL service is running (check Services on Windows)")
        print("2. Your credentials are correct")
        print("3. PostgreSQL is accepting connections on specified host/port")
        return False

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Base path to database directories
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "MAC-SQL", "data", "bird-ukr", "database"))
    
    # Check if path exists
    if not os.path.exists(base_path):
        print(f"Error: Database path not found: {base_path}")
        print("Please make sure the path to the database directories is correct.")
        return
    
    print(f"Using database path: {base_path}")
    
    # Ask for PostgreSQL credentials
    db_user = input(f"PostgreSQL username [{DB_USER}]: ") or DB_USER
    db_password = getpass("PostgreSQL password: ")
    db_host = input(f"PostgreSQL host [{DB_HOST}]: ") or DB_HOST
    db_port = input(f"PostgreSQL port [{DB_PORT}]: ") or DB_PORT
    
    # Get all database directories
    db_dirs = get_database_dirs(base_path)
    print(f"Found {len(db_dirs)} database directories: {', '.join(db_dirs)}")
    
    # Check connection
    if args.check or args.cleanup or args.do_import:
        if not check_postgres_connection(db_host, db_port, db_user, db_password):
            return
    
    # Convert MySQL syntax to PostgreSQL syntax
    if args.convert:
        convert_all_schemas(base_path, db_dirs)
    
    # Clean up existing databases
    if args.cleanup:
        print("\nCleaning up existing databases...")
        confirm = input("⚠️ WARNING: This will drop all databases. Continue? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cleanup cancelled.")
        else:
            for db_dir in db_dirs:
                db_name = db_dir.lower().replace(' ', '_')
                drop_database(db_name, db_user, db_password, db_host, db_port)
    
    # Create databases
    if args.check:
        print("\nCreating databases...")
        for db_dir in db_dirs:
            db_name = db_dir.lower().replace(' ', '_')
            create_database(db_name, db_user, db_password, db_host, db_port)
    
    # Import data
    if args.do_import:
        # Check for psql command
        psql_path = "psql"  # Default: use from PATH
        use_psql = True
        try:
            # Try to run psql --version to check if it works
            subprocess.run([psql_path, "--version"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            print("Found psql in system PATH")
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: Could not find psql command in your PATH")
            use_custom_path = input("Do you want to specify the psql executable path? (y/n): ").lower().strip() == 'y'
            if use_custom_path:
                psql_path = input("Enter full path to psql executable: ").strip()
                if not os.path.exists(psql_path):
                    print(f"Error: The specified path '{psql_path}' does not exist")
                    use_psql = False
                    print("Falling back to direct psycopg2 import method")
            else:
                use_psql = False
                print("Falling back to direct psycopg2 import method")
        
        # Process each database
        successful_imports = 0
        failed_imports = []
        
        for db_dir in db_dirs:
            if os.path.isfile(os.path.join(base_path, db_dir, "README.md")) and not os.path.isfile(os.path.join(base_path, db_dir, "schema.sql")):
                print(f"Skipping {db_dir}: Documentation only, no schema file")
                continue
                
            # Convert Ukrainian names to Latin for PostgreSQL compatibility
            db_name = db_dir.lower().replace(' ', '_')
            import_file = os.path.join(base_path, db_dir, "import.sql")
            schema_file = os.path.join(base_path, db_dir, "schema.sql")
            
            # Create database if needed
            try:
                create_database(db_name, db_user, db_password, db_host, db_port)
                
                # Import data
                success = False
                if use_psql and os.path.isfile(import_file):
                    # Try with psql first
                    success = import_data(db_name, import_file, db_user, db_password, db_host, db_port, psql_path)
                    
                if not success and os.path.isfile(schema_file):
                    # Fall back to direct import if psql failed or not available
                    print(f"Trying direct import with psycopg2 for {db_dir}")
                    success = import_with_psycopg2(db_name, schema_file, db_user, db_password, db_host, db_port)
                    
                if success:
                    successful_imports += 1
                    print(f"✅ Successfully imported {db_dir}")
                else:
                    failed_imports.append((db_dir, "Import failed with both methods"))
            except Exception as e:
                print(f"❌ Error processing {db_dir}: {str(e)}")
                failed_imports.append((db_dir, str(e)))
        
        # Print summary
        print(f"\n=== Import Summary ===")
        print(f"Total database directories: {len(db_dirs)}")
        print(f"Successfully imported: {successful_imports}")
        print(f"Failed imports: {len(failed_imports)}")
        
        if failed_imports:
            print("\nFailed imports:")
            for db_dir, reason in failed_imports:
                print(f"  - {db_dir}: {reason}")

if __name__ == "__main__":
    main() 