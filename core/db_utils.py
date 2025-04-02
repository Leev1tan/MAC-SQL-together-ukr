#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database utility functions for MAC-SQL.
Provides connection handling for both SQLite and PostgreSQL databases.
"""

import os
import sqlite3
from dotenv import load_dotenv

# Try to import psycopg2, but make it optional
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

# Load environment variables
load_dotenv()

def get_db_connection(dataset_name, db_id, db_base_path=None):
    """
    Get a database connection based on the dataset type.
    
    Args:
        dataset_name: Name of the dataset ('spider', 'bird', or 'bird-ukr')
        db_id: Database identifier
        db_base_path: Base path for SQLite databases (only used for SQLite)
        
    Returns:
        tuple: (connection, db_type)
    """
    conn = None
    db_type = 'sqlite'  # Default
    
    # Determine database type from dataset name
    if dataset_name == 'bird-ukr':
        db_type = 'postgres'
    elif dataset_name in ['spider', 'bird']:
        db_type = 'sqlite'
    else:
        # Default to SQLite for unknown datasets
        db_type = 'sqlite'
    
    # PostgreSQL connection
    if db_type == 'postgres':
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL connections. "
                              "Please install it with: pip install psycopg2-binary")
        
        try:
            conn = psycopg2.connect(
                host=os.getenv("PG_HOST", "localhost"),
                port=os.getenv("PG_PORT", "5432"),
                user=os.getenv("PG_USER", "postgres"),
                password=os.getenv("PG_PASSWORD", ""),
                dbname=db_id
            )
        except psycopg2.Error as e:
            raise ConnectionError(f"Failed to connect to PostgreSQL database {db_id}: {e}")
    
    # SQLite connection
    elif db_type == 'sqlite':
        if db_base_path is None:
            # Try to determine base path based on dataset
            if dataset_name == 'spider':
                db_base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                           "data", "spider", "database")
            elif dataset_name == 'bird':
                db_base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                           "data", "bird", "database")
            else:
                raise ValueError(f"No db_base_path provided and couldn't determine it for dataset {dataset_name}")
        
        # Construct full path to SQLite file
        db_file_path = os.path.join(db_base_path, db_id, f"{db_id}.sqlite")
        
        if not os.path.exists(db_file_path):
            raise FileNotFoundError(f"SQLite database file not found: {db_file_path}")
        
        try:
            conn = sqlite3.connect(db_file_path)
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to SQLite database {db_file_path}: {e}")
    
    return conn, db_type

def get_schema(conn, db_type):
    """
    Get database schema (tables, columns, types) from a database connection.
    Works with both SQLite and PostgreSQL.
    
    Args:
        conn: Database connection
        db_type: Database type ('sqlite' or 'postgres')
        
    Returns:
        dict: Schema information containing tables and their columns
    """
    schema_info = {
        'tables': [],
        'columns': {},
        'primary_keys': {},
        'foreign_keys': {}
    }
    
    if db_type == 'postgres':
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        schema_info['tables'] = [row[0] for row in cursor.fetchall()]
        
        # Get columns and their types for each table
        for table_name in schema_info['tables']:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            schema_info['columns'][table_name] = [(col[0], col[1]) for col in cursor.fetchall()]
        
        # Get primary keys
        for table_name in schema_info['tables']:
            cursor.execute("""
                SELECT c.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage AS ccu 
                USING (constraint_schema, constraint_name)
                JOIN information_schema.columns AS c
                ON c.table_schema = tc.constraint_schema
                AND tc.table_name = c.table_name
                AND ccu.column_name = c.column_name
                WHERE constraint_type = 'PRIMARY KEY' AND tc.table_name = %s;
            """, (table_name,))
            pk_columns = [row[0] for row in cursor.fetchall()]
            if pk_columns:
                schema_info['primary_keys'][table_name] = pk_columns
        
        # Get foreign keys
        cursor.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY';
        """)
        foreign_keys = cursor.fetchall()
        for fk in foreign_keys:
            table_name, column_name, ref_table, ref_column = fk
            if table_name not in schema_info['foreign_keys']:
                schema_info['foreign_keys'][table_name] = []
            schema_info['foreign_keys'][table_name].append({
                'column': column_name,
                'ref_table': ref_table,
                'ref_column': ref_column
            })
            
        cursor.close()
    
    elif db_type == 'sqlite':
        cursor = conn.cursor()
        
        # Get tables (excluding sqlite_* tables)
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%';
        """)
        schema_info['tables'] = [row[0] for row in cursor.fetchall()]
        
        # Get columns and their types for each table
        for table_name in schema_info['tables']:
            cursor.execute(f'PRAGMA table_info("{table_name}");')
            # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
            pragma_results = cursor.fetchall()
            schema_info['columns'][table_name] = [(row[1], row[2]) for row in pragma_results]
            
            # Extract primary keys
            pk_columns = [row[1] for row in pragma_results if row[5] == 1]
            if pk_columns:
                schema_info['primary_keys'][table_name] = pk_columns
        
        # Get foreign keys for each table
        for table_name in schema_info['tables']:
            cursor.execute(f'PRAGMA foreign_key_list("{table_name}");')
            # PRAGMA foreign_key_list returns: id, seq, table, from, to, on_update, on_delete, match
            fk_results = cursor.fetchall()
            if fk_results:
                schema_info['foreign_keys'][table_name] = []
                for fk in fk_results:
                    schema_info['foreign_keys'][table_name].append({
                        'column': fk[3],  # 'from' column
                        'ref_table': fk[2],  # referenced table
                        'ref_column': fk[4]  # 'to' column
                    })
        
        cursor.close()
    
    return schema_info

def format_schema_for_prompt(schema_info, include_pk=True, include_fk=True):
    """
    Format schema information into a string for use in LLM prompts.
    
    Args:
        schema_info: Schema information from get_schema
        include_pk: Whether to include primary key information
        include_fk: Whether to include foreign key information
        
    Returns:
        str: Formatted schema string
    """
    schema_str = []
    
    for table_name in schema_info['tables']:
        column_info = []
        for col_name, col_type in schema_info['columns'][table_name]:
            # Mark primary keys if included
            pk_marker = ""
            if include_pk and table_name in schema_info['primary_keys'] and col_name in schema_info['primary_keys'][table_name]:
                pk_marker = " [PRIMARY KEY]"
            
            column_info.append(f"{col_name} ({col_type}){pk_marker}")
        
        # Add table definition with columns
        schema_str.append(f"Table: {table_name}")
        schema_str.append("Columns: " + ", ".join(column_info))
        
        # Add foreign key information if included
        if include_fk and table_name in schema_info['foreign_keys']:
            fk_info = []
            for fk in schema_info['foreign_keys'][table_name]:
                fk_info.append(f"{fk['column']} -> {fk['ref_table']}.{fk['ref_column']}")
            
            if fk_info:
                schema_str.append("Foreign Keys: " + ", ".join(fk_info))
        
        schema_str.append("")  # Add blank line between tables
    
    return "\n".join(schema_str)

def execute_query(conn, query, db_type, fetch=True):
    """
    Execute an SQL query and return results.
    
    Args:
        conn: Database connection
        query: SQL query to execute
        db_type: Database type ('sqlite' or 'postgres')
        fetch: Whether to fetch and return results
        
    Returns:
        list: Query results (if fetch=True)
    """
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        
        if fetch:
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            return {'rows': results, 'columns': column_names}
        else:
            conn.commit()
            cursor.close()
            return True
    except (sqlite3.Error, psycopg2.Error) as e:
        conn.rollback()
        cursor.close()
        raise Exception(f"Query execution error: {e}") 