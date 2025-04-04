#!/usr/bin/env python
"""
Debug script for Ukrainian BIRD evaluation to diagnose issues
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    """Debug BIRD-UKR evaluation issues"""
    try:
        # First apply our fixes
        from fix_ukr_refiner import apply_fixes
        apply_fixes()
        
        from utils.bird_ukr_loader import find_bird_ukr_data, load_questions
        from utils.pg_connection import init_connection_pool, close_connection_pool
        from test_macsql_agent_bird_ukr import (
            get_agent, 
            get_tables_json_path, 
            test_single_query
        )
        import types
        
        # Find BIRD-UKR data
        data_path = find_bird_ukr_data()
        logger.info(f"Found BIRD-UKR data at: {data_path}")
        
        # Get tables.json path
        tables_json_path = get_tables_json_path(data_path)
        logger.info(f"Using tables.json: {tables_json_path}")
        
        # Load a single question for testing
        questions_path = os.path.join(data_path, "questions.json")
        questions = load_questions(questions_path, limit=1)
        logger.info(f"Loaded {len(questions)} questions")
        
        if not questions:
            logger.error("No questions loaded!")
            return
            
        # Print the question structure
        logger.info(f"Question structure: {json.dumps(questions[0], indent=2, ensure_ascii=False)}")
        
        # Get database ID
        db_id = questions[0].get("db_id")
        if not db_id:
            logger.error("Question has no database ID!")
            return
            
        logger.info(f"Testing with database: {db_id}")
        
        # Initialize connection pool
        init_connection_pool(db_id)
        logger.info(f"Initialized connection pool for {db_id}")
        
        # Set up test arguments
        args = types.SimpleNamespace(
            data_path=data_path,
            force_execution=False,
            visualize=False,
            debug=True
        )
        
        # Get agent
        agent = get_agent(
            data_path=data_path,
            model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            tables_json_path=tables_json_path
        )
        logger.info("Agent initialized")
        
        # Run test on a single question
        result = test_single_query(
            agent=agent,
            args=args,
            query_id="debug-test",
            question=questions[0],
            db_id=db_id,
            tables_json_path=tables_json_path,
            gold_query=questions[0].get("gold_sql", ""),
            logger=logger
        )
        
        # Print result
        logger.info("Test completed")
        logger.info(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Clean up
        close_connection_pool(db_id)
        
    except Exception as e:
        logger.exception(f"Error in debug script: {e}")

if __name__ == "__main__":
    main() 