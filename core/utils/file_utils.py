"""
File Utilities

This module provides utility functions for file operations.
"""

import os
import json
import glob
from typing import List, Any

def load_json_file(path: str) -> Any:
    """
    Load and parse JSON file
    
    Args:
        path: Path to JSON file
        
    Returns:
        Parsed JSON data
    """
    with open(path, 'r', encoding='utf-8') as f:
        print(f"load json file from {path}")
        return json.load(f)

def get_files(root: str, suffix: str) -> List[str]:
    """
    Get all files with specified suffix in directory
    
    Args:
        root: Root directory to search
        suffix: File suffix to filter by
        
    Returns:
        List of absolute paths to matching files
    """
    if not os.path.exists(root):
        raise FileNotFoundError(f'path {root} not found.')
    res = glob.glob(f'{root}/**/*{suffix}', recursive=True)
    res = [os.path.abspath(p) for p in res]
    return res

def save_json_file(path: str, data: Any) -> None:
    """
    Save data to JSON file
    
    Args:
        path: Path to save file
        data: Data to save
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"save json file to {path}")

def read_txt_file(path: str) -> List[str]:
    """
    Read text file into list of lines
    
    Args:
        path: Path to text file
        
    Returns:
        List of non-empty lines
    """
    with open(path, 'r', encoding='utf-8') as f:
        print(f"load txt file from {path}")
        return [line.strip() for line in f if line.strip() != '']

# Export all functions
__all__ = [
    'load_json_file',
    'get_files',
    'save_json_file',
    'read_txt_file'
] 