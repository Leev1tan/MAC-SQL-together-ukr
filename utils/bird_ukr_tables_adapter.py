#!/usr/bin/env python
"""
Adapter for converting BIRD-UKR tables.json format to the format expected by MAC-SQL.
"""

import os
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def convert_tables_format(original_path: str, output_path: str = None) -> str:
    """
    Convert BIRD-UKR tables.json format to MAC-SQL compatible format.
    
    Args:
        original_path: Path to original BIRD-UKR tables.json
        output_path: Path to save converted tables.json (default: original_path + '.converted')
        
    Returns:
        Path to the converted tables.json file
    """
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"Original tables file not found: {original_path}")
    
    # Set default output path if not provided
    if output_path is None:
        output_path = original_path + '.converted'
    
    try:
        # Load the original tables data
        with open(original_path, 'r', encoding='utf-8') as f:
            bird_ukr_tables = json.load(f)
        
        # BIRD-UKR format: object with db_id as keys
        # MAC-SQL format: array of objects with db_id field
        
        # Create the converted format
        macsql_tables = []
        
        for db_id, db_info in bird_ukr_tables.items():
            table_names = db_info.get("table_names", [])
            column_names_raw = db_info.get("column_names", [])
            
            # Process column names to ensure proper format
            # MAC-SQL expects: [[table_idx, col_name], ...]
            processed_column_names = []
            
            # Add special * column for the whole database
            processed_column_names.append([0, "*"])
            
            # Process the rest of the columns
            for col_info in column_names_raw:
                if isinstance(col_info, list) and len(col_info) >= 2:
                    table_name, col_name = col_info
                    
                    # Find table index
                    if table_name in table_names:
                        table_idx = table_names.index(table_name)
                    else:
                        # If table not found, use -1 (or some default)
                        table_idx = -1
                        
                    processed_column_names.append([table_idx, col_name])
            
            # Create column types if not available
            column_types = db_info.get("column_types", ["text"] * len(processed_column_names))
            
            # Create a new entry in the format expected by MAC-SQL
            macsql_entry = {
                "db_id": db_id,
                "table_names": table_names,
                "column_names": processed_column_names,
                "column_names_original": processed_column_names,
                "column_types": column_types
            }
            
            # Add foreign keys if available
            if "foreign_keys" in db_info:
                macsql_entry["foreign_keys"] = db_info["foreign_keys"]
                
            # Add primary keys if available
            if "primary_keys" in db_info:
                macsql_entry["primary_keys"] = db_info["primary_keys"]
                
            macsql_tables.append(macsql_entry)
        
        # Save the converted format
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(macsql_tables, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Converted tables format saved to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error converting tables format: {e}")
        raise

def generate_compatible_tables_json(bird_ukr_path: str) -> str:
    """
    Generate a MAC-SQL compatible tables.json from BIRD-UKR dataset.
    
    Args:
        bird_ukr_path: Path to BIRD-UKR dataset directory
        
    Returns:
        Path to the generated tables.json file
    """
    # Find original tables.json
    original_path = os.path.join(bird_ukr_path, "tables.json")
    if not os.path.exists(original_path):
        raise FileNotFoundError(f"tables.json not found in {bird_ukr_path}")
    
    # Create output directory for converted files
    output_dir = os.path.join(bird_ukr_path, "converted")
    os.makedirs(output_dir, exist_ok=True)
    
    # Set output path
    output_path = os.path.join(output_dir, "tables.json")
    
    # Convert the format
    return convert_tables_format(original_path, output_path) 