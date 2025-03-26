"""
Database Utilities

This module provides utility functions for database operations
and schema extraction.
"""

import os
import json
import sqlite3
import re
from typing import Dict, List, Any, Set

def extract_world_info(message_dict: dict) -> dict:
    """
    Extract relevant information from a message dictionary
    
    Args:
        message_dict: Dictionary containing message data
        
    Returns:
        Dictionary with extracted information
    """
    info_dict = {}
    info_dict['idx'] = message_dict.get('idx', 0)
    info_dict['db_id'] = message_dict.get('db_id', '')
    info_dict['query'] = message_dict.get('query', '')
    info_dict['evidence'] = message_dict.get('evidence', '')
    info_dict['difficulty'] = message_dict.get('difficulty', '')
    info_dict['ground_truth'] = message_dict.get('ground_truth', '')
    info_dict['send_to'] = message_dict.get('send_to', '')
    return info_dict

def extract_table_names(sql_query: str) -> Set[str]:
    """
    Extract table names from SQL query
    
    Args:
        sql_query: SQL query string
        
    Returns:
        Set of table names
    """
    sql_query = sql_query.replace('`', '')
    table_names = re.findall(r'FROM\s+([\w]+)', sql_query, re.IGNORECASE) + \
                  re.findall(r'JOIN\s+([\w]+)', sql_query, re.IGNORECASE)
    return set(table_names)

def extract_tables_from_sql(sql_query: str) -> Set[str]:
    """
    Extract table names from SQL query
    
    This function is an alias for extract_table_names for backward compatibility
    
    Args:
        sql_query: SQL query string
        
    Returns:
        Set of table names
    """
    return extract_table_names(sql_query)

def extract_db_schema(data_path: str, db_id: str) -> dict:
    """
    Extract database schema information
    
    Args:
        data_path: Path to database directory
        db_id: Database ID
        
    Returns:
        Dictionary with database schema
    """
    db_path = os.path.join(data_path, db_id, f"{db_id}.sqlite")
    schema = {}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        
        for table in tables:
            # Get columns for each table
            cursor.execute(f"PRAGMA table_info(`{table}`);")
            columns = cursor.fetchall()
            
            schema[table] = {
                "columns": [col[1] for col in columns],
                "types": [col[2] for col in columns],
                "primary_keys": [col[1] for col in columns if col[5] == 1]
            }
            
            # Try to get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list(`{table}`);")
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                schema[table]["foreign_keys"] = [
                    {
                        "column": fk[3],
                        "references": {
                            "table": fk[2],
                            "column": fk[4]
                        }
                    } for fk in foreign_keys
                ]
        
        conn.close()
        return schema
        
    except Exception as e:
        print(f"Error extracting schema: {e}")
        return {}

def extract_tables_from_schema(schema_dict: dict) -> List[str]:
    """
    Extract table names from schema dictionary
    
    Args:
        schema_dict: Dictionary with database schema
        
    Returns:
        List of table names
    """
    return list(schema_dict.keys())

def format_schema_for_llm(schema_dict: dict) -> str:
    """
    Format schema dictionary into string for LLM
    
    Args:
        schema_dict: Dictionary with database schema
        
    Returns:
        Formatted schema string
    """
    output = []
    for table, info in schema_dict.items():
        output.append(f"Table: {table}")
        columns = info.get("columns", [])
        types = info.get("types", [""] * len(columns))
        
        for i, col in enumerate(columns):
            col_type = types[i] if i < len(types) else "unknown"
            output.append(f"  - {col} ({col_type})")
        
        if "foreign_keys" in info:
            for fk in info["foreign_keys"]:
                output.append(f"  - Foreign Key: {fk['column']} -> {fk['references']['table']}.{fk['references']['column']}")
        
        output.append("")  # Add newline between tables
    
    return "\n".join(output)

def is_email(string: str) -> bool:
    """
    Check if string is a valid email
    
    Args:
        string: String to check
        
    Returns:
        True if string is a valid email, False otherwise
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    match = re.match(pattern, string)
    return bool(match)

def is_valid_date(date_str) -> bool:
    """
    Check if string is a valid date
    
    Args:
        date_str: String to check
        
    Returns:
        True if string is a valid date, False otherwise
    """
    if not isinstance(date_str, str):
        return False
    date_str = date_str.split()[0]
    if len(date_str) != 10:
        return False
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(pattern, date_str):
        year, month, day = map(int, date_str.split('-'))
        if year < 1 or month < 1 or month > 12 or day < 1 or day > 31:
            return False
        else:
            return True
    else:
        return False

def is_valid_date_column(col_value_lst: List[str]) -> bool:
    """
    Check if all values in a list are valid dates
    
    Args:
        col_value_lst: List of strings to check
        
    Returns:
        True if all strings are valid dates, False otherwise
    """
    for col_value in col_value_lst:
        if not is_valid_date(col_value):
            return False
    return True

# Export all functions
__all__ = [
    'extract_world_info',
    'extract_table_names',
    'extract_tables_from_sql',
    'extract_db_schema',
    'extract_tables_from_schema',
    'format_schema_for_llm',
    'is_email',
    'is_valid_date',
    'is_valid_date_column'
] 