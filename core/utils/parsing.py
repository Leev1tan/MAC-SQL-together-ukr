"""
Parsing Utilities

This module provides utility functions for parsing text, SQL, and JSON data.
"""

import re
import json
from typing import Dict, List, Any

def parse_json(text: str) -> dict:
    """
    Extract and parse JSON data from text string
    
    Args:
        text: String that may contain JSON content
        
    Returns:
        Parsed JSON as dictionary or empty dict if parsing fails
    """
    # Search for JSON block in markdown format
    start = text.find("```json")
    end = text.find("```", start + 7)
    
    # If JSON block is found
    if start != -1 and end != -1:
        json_string = text[start + 7: end]
        
        try:
            # Parse JSON string
            json_data = json.loads(json_string)
            valid = check_selector_response(json_data)
            if valid:
                return json_data
            else:
                return {}
        except Exception:
            return {}
    
    return {}

def check_selector_response(json_data: Dict) -> bool:
    """
    Check if selector response is valid
    
    Args:
        json_data: JSON data to validate
        
    Returns:
        Boolean indicating whether the data is valid
    """
    FLAGS = ['keep_all', 'drop_all']
    for k, v in json_data.items():
        if isinstance(v, str):
            if v not in FLAGS:
                return False
        elif isinstance(v, list):
            pass
        else:
            return False
    return True

def parse_sql_from_string(input_string: str) -> str:
    """
    Extract SQL query from a string
    
    Args:
        input_string: String that may contain SQL
        
    Returns:
        Extracted SQL query or error message
    """
    sql_pattern = r'```sql(.*?)```'
    all_sqls = []
    
    # Find all SQL blocks in the string
    for match in re.finditer(sql_pattern, input_string, re.DOTALL):
        all_sqls.append(match.group(1).strip())

    if all_sqls:
        return all_sqls[-1]
    else:
        return "error: No SQL found in the input string"

def add_prefix(sql: str) -> str:
    """
    Add SELECT prefix to SQL if needed
    
    Args:
        sql: SQL query string
        
    Returns:
        SQL with SELECT prefix if needed
    """
    if 'SELECT' not in sql and 'select' not in sql:
        sql = 'SELECT ' + sql
    return sql.strip()

# Export all functions
__all__ = [
    'parse_json',
    'check_selector_response',
    'parse_sql_from_string',
    'add_prefix'
] 