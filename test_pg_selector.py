#!/usr/bin/env python
"""
Test script for the PostgreSQL Selector with table selection functionality.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import our PostgreSQL Selector
from utils.pg_selector import PostgreSQLSelector

def main():
    """
    Main function to test the PostgreSQL Selector.
    """
    # Check if database ID was provided
    if len(sys.argv) < 2:
        print("Usage: python test_pg_selector.py <database_id> [question]")
        print("Example: python test_pg_selector.py університет 'Які викладачі мають найбільше навантаження?'")
        return
    
    # Get database ID from command line
    db_id = sys.argv[1]
    
    # Get question from command line or use default
    question = sys.argv[2] if len(sys.argv) > 2 else "Які викладачі мають найбільше навантаження?"
    
    # Create the PostgreSQL Selector
    selector = PostgreSQLSelector(
        data_path="./bird-ukr",
        tables_json_path="./bird-ukr/converted/tables.json",
        model_name=os.environ.get("TOGETHER_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo"),
        dataset_name="bird-ukr"
    )
    
    # Create a test message
    message = {
        "db_id": db_id,
        "query": question,
        "evidence": ""
    }
    
    # Process the message with the selector
    logger.info(f"Testing selector with database {db_id} and question: {question}")
    result = selector.talk(message)
    
    # Print the selected tables
    if "selection_explanation" in result:
        logger.info(f"Selection explanation: {result['selection_explanation']}")
    
    # Print the schema information that was selected
    logger.info("Selected schema:")
    logger.info(result["desc_str"])
    
    logger.info("Selected foreign keys:")
    logger.info(result["fk_str"])
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    main() 