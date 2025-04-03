#!/usr/bin/env python
"""
BIRD-UKR dataset loader utilities.
Functions for loading and processing Ukrainian BIRD-UKR dataset files.
"""

import os
import json
import logging
import random
from typing import Dict, List, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)

def load_questions(file_path: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Load questions from a BIRD-UKR JSON file.
    
    Args:
        file_path: Path to the questions JSON file
        limit: Maximum number of questions to load (None for all)
        
    Returns:
        List of question objects
    """
    if not os.path.exists(file_path):
        logger.error(f"Questions file not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        logger.info(f"Loaded {len(questions)} questions from {file_path}")
        
        # Apply limit if specified
        if limit and limit > 0:
            questions = questions[:limit]
            logger.info(f"Limited to {limit} questions")
        
        return questions
    except Exception as e:
        logger.error(f"Error loading questions from {file_path}: {e}")
        return []

def load_bird_ukr_subset(
    data_path: str, 
    num_samples: int = 10, 
    db_filter: Optional[List[str]] = None,
    random_seed: Optional[int] = None,
    random_sample: bool = False
) -> List[Dict[str, Any]]:
    """
    Load a subset of questions from the BIRD-UKR dataset.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        num_samples: Maximum number of questions to load (total)
        db_filter: List of database IDs to include (None for all)
        random_seed: Optional seed for random sampling
        random_sample: If True, select questions randomly rather than sequentially
        
    Returns:
        List of question objects
    """
    # First try questions.json, then fallback to all_questions.json
    questions_path = os.path.join(data_path, "questions.json")
    all_questions_path = os.path.join(data_path, "all_questions.json")
    
    # Try to load questions from questions.json first
    if os.path.exists(questions_path):
        questions = load_questions(questions_path)
    elif os.path.exists(all_questions_path):
        questions = load_questions(all_questions_path)
    else:
        # If neither file exists, load from individual files
        questions = load_from_individual_files(data_path)
    
    # Filter by database IDs if specified
    if db_filter:
        questions = [q for q in questions if q.get("db_id") in db_filter]
        logger.info(f"Filtered to {len(questions)} questions for databases: {db_filter}")
    
    # Random sampling if requested
    if random_sample and questions:
        if random_seed is not None:
            random.seed(random_seed)
        if num_samples and num_samples > 0 and num_samples < len(questions):
            questions = random.sample(questions, num_samples)
            logger.info(f"Randomly sampled {num_samples} questions")
    # Otherwise limit sequentially
    elif num_samples and num_samples > 0 and num_samples < len(questions):
        questions = questions[:num_samples]
        logger.info(f"Limited to {num_samples} questions")
    
    return questions

def load_from_individual_files(data_path: str) -> List[Dict[str, Any]]:
    """
    Load questions from individual database question files.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        
    Returns:
        List of combined question objects
    """
    questions_dir = os.path.join(data_path, "questions")
    if not os.path.exists(questions_dir):
        logger.error(f"Questions directory not found: {questions_dir}")
        return []
    
    # Get all JSON files in the questions directory
    question_files = [f for f in os.listdir(questions_dir) if f.endswith("_questions.json")]
    logger.info(f"Found {len(question_files)} question files in {questions_dir}")
    
    all_questions = []
    for file_name in question_files:
        file_path = os.path.join(questions_dir, file_name)
        db_questions = load_questions(file_path)
        all_questions.extend(db_questions)
        logger.info(f"Loaded {len(db_questions)} questions from {file_name}")
    
    logger.info(f"Loaded a total of {len(all_questions)} questions")
    return all_questions

def load_tables_schema(data_path: str) -> Dict:
    """
    Load the database schemas from tables.json.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        
    Returns:
        Dictionary with database schema information
    """
    tables_path = os.path.join(data_path, "tables.json")
    if not os.path.exists(tables_path):
        logger.error(f"Tables file not found: {tables_path}")
        return {}
    
    try:
        with open(tables_path, 'r', encoding='utf-8') as f:
            tables_data = json.load(f)
        
        logger.info(f"Loaded schema information for {len(tables_data)} databases")
        return tables_data
    except Exception as e:
        logger.error(f"Error loading tables from {tables_path}: {e}")
        return {}

def load_column_meaning(data_path: str) -> Dict:
    """
    Load column meaning descriptions from column_meaning.json.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        
    Returns:
        Dictionary mapping column names to their descriptions
    """
    meaning_path = os.path.join(data_path, "column_meaning.json")
    if not os.path.exists(meaning_path):
        logger.info(f"Column meaning file not found: {meaning_path}")
        return {}
    
    try:
        with open(meaning_path, 'r', encoding='utf-8') as f:
            meaning_data = json.load(f)
        
        logger.info(f"Loaded meaning information for {len(meaning_data)} columns")
        return meaning_data
    except Exception as e:
        logger.error(f"Error loading column meanings from {meaning_path}: {e}")
        return {}

def get_database_path(data_path: str, db_id: str) -> str:
    """
    Get the path to a specific database directory.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        db_id: Database ID
        
    Returns:
        Path to the database directory
    """
    db_path = os.path.join(data_path, "database", db_id)
    if not os.path.exists(db_path):
        logger.warning(f"Database directory not found: {db_path}")
    return db_path

def normalize_ukr_query(query: str) -> str:
    """
    Normalize a Ukrainian SQL query for comparison.
    Handle PostgreSQL-specific syntax and Ukrainian identifiers.
    
    Args:
        query: SQL query to normalize
        
    Returns:
        Normalized SQL query
    """
    if not query:
        return ""
    
    # Convert to lowercase (except strings)
    # TODO: Add string preservation logic
    query = query.lower()
    
    # Remove comments
    query = remove_comments(query)
    
    # Remove trailing semicolon
    query = query.strip().rstrip(';')
    
    # Normalize whitespace
    query = ' '.join(query.split())
    
    # Normalize keywords
    # PostgreSQL-specific functions
    query = query.replace("extract(", "extract (")
    query = query.replace("current_date", "current_date")
    query = query.replace("interval", "interval")
    
    # Remove quotes around identifiers (handle both double and single quotes)
    # TODO: Improve quote handling for identifiers with spaces
    
    return query

def remove_comments(query: str) -> str:
    """
    Remove SQL comments from a query.
    Handles both single-line and multi-line comments.
    
    Args:
        query: SQL query with comments
        
    Returns:
        SQL query without comments
    """
    # TODO: Implement proper comment removal
    # For now, just handle basic single line comments
    result = []
    for line in query.split('\n'):
        line = line.split('--')[0]
        if line.strip():
            result.append(line)
    return ' '.join(result)

def get_database_ids(data_path: str) -> List[str]:
    """
    Get the list of all database IDs in the dataset.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        
    Returns:
        List of database IDs
    """
    db_path = os.path.join(data_path, "database")
    if not os.path.exists(db_path):
        logger.error(f"Database directory not found: {db_path}")
        return []
    
    # Get all subdirectories in the database directory
    db_ids = [name for name in os.listdir(db_path) 
              if os.path.isdir(os.path.join(db_path, name))]
    
    logger.info(f"Found {len(db_ids)} database IDs")
    return db_ids

def find_bird_ukr_data():
    """Find the BIRD-UKR dataset directory."""
    # First check environment variable
    env_path = os.environ.get("BIRD_UKR_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Found BIRD-UKR data from environment variable: {env_path}")
        return str(env_path)
    
    # Try standard locations
    possible_paths = [
        "bird-ukr",
        "data/bird-ukr",
        "../bird-ukr",
        "./bird-ukr",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            # Check if it contains essential files
            has_questions = (os.path.exists(os.path.join(path, "questions.json")) or 
                            os.path.exists(os.path.join(path, "all_questions.json")))
            has_tables = os.path.exists(os.path.join(path, "tables.json"))
            has_database = os.path.exists(os.path.join(path, "database"))
            
            if has_questions and has_tables and has_database:
                logger.info(f"Found BIRD-UKR data at: {path}")
                return os.path.abspath(path)
    
    raise FileNotFoundError("BIRD-UKR dataset not found. Please put it in 'bird-ukr' directory or set BIRD_UKR_PATH environment variable.")

def load_random_subset(
    data_path: str, 
    num_samples: int = 10, 
    random_seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Load a random subset of questions from the BIRD-UKR dataset.
    
    Args:
        data_path: Path to the BIRD-UKR dataset folder
        num_samples: Number of questions to sample
        random_seed: Optional seed for random sampling
        
    Returns:
        List of randomly sampled question objects
    """
    # Set random seed if provided
    if random_seed is not None:
        random.seed(random_seed)
        logger.info(f"Set random seed to {random_seed}")
    
    # Load all questions
    questions_path = os.path.join(data_path, "questions.json")
    questions = load_questions(questions_path)
    
    if not questions:
        logger.error("No questions found to sample from")
        return []
    
    # Sample randomly
    sample_size = min(num_samples, len(questions))
    sampled_questions = random.sample(questions, sample_size)
    
    logger.info(f"Randomly sampled {len(sampled_questions)} questions")
    return sampled_questions

if __name__ == "__main__":
    # Test the loader
    logging.basicConfig(level=logging.INFO)
    
    TEST_PATH = "../bird-ukr"  # Adjust to your dataset location
    
    # Test loading questions
    questions = load_bird_ukr_subset(TEST_PATH, num_samples=5)
    print(f"Loaded {len(questions)} questions")
    if questions:
        print(f"Sample question: {questions[0]['question']}")
        print(f"Sample SQL: {questions[0]['gold_sql']}")
    
    # Test loading tables schema
    tables = load_tables_schema(TEST_PATH)
    print(f"Loaded schema for {len(tables)} databases")
    
    # Test getting database IDs
    db_ids = get_database_ids(TEST_PATH)
    print(f"Database IDs: {db_ids}") 