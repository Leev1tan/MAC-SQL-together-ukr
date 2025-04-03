#!/usr/bin/env python
"""
Common utility functions used across the codebase.
"""

import os
import logging
import sys
from typing import Optional

def set_up_logging(
    level: str = "INFO", 
    log_file: Optional[str] = None,
    format_str: Optional[str] = None
) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (if None, logs to console only)
        format_str: Custom log format string
        
    Returns:
        None
    """
    # Set up numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Default format
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Basic configuration
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(format_str))
    handlers.append(console_handler)
    
    # File handler if requested
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(format_str))
        handlers.append(file_handler)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=format_str,
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Suppress overly verbose loggers
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    # Log that logging is set up
    logging.info(f"Logging set up at level {level}")

def ensure_dir_exists(path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logging.info(f"Created directory: {path}")

def get_file_extension(path: str) -> str:
    """
    Get the extension of a file path.
    
    Args:
        path: File path
        
    Returns:
        File extension (without the dot)
    """
    return os.path.splitext(path)[1][1:] 