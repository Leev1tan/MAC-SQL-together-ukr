#!/usr/bin/env python
"""
Example script showing how to use MAC-SQL with Together AI for the Spider dataset.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_chat_manager import EnhancedChatManager
from core.macsql_together_adapter import TogetherAIAdapter

# Load environment variables from .env file
load_dotenv()

def setup_path():
    """Ensure necessary directories exist"""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Create output directory
    Path("output").mkdir(exist_ok=True)

def find_spider_data():
    """Find the Spider dataset in the data directory"""
    data_dir = Path("data/spider")
    
    # Check if Spider directory exists
    if not data_dir.exists():
        print(f"Error: Spider data directory not found at {data_dir}")
        return None, None, None
    
    # Look for tables.json
    tables_path = data_dir / "tables.json"
    if not tables_path.exists():
        print("Error: Could not find tables.json. Please ensure it's installed.")
        return None, None, None
    
    # Check for database directory
    db_path = data_dir / "database"
    if not db_path.exists():
        print("Error: Could not find Spider database directory. Please ensure it's installed.")
        return None, None, None
    
    return data_dir, db_path, tables_path

def process_query(db_id, question):
    """
    Process a natural language query on a Spider database.
    
    Args:
        db_id: Database ID
        question: Natural language question
        
    Returns:
        Generated SQL query
    """
    # Setup paths
    setup_path()
    
    # Find Spider data
    data_dir, db_path, tables_path = find_spider_data()
    if not data_dir or not db_path or not tables_path:
        print("Error: Could not find Spider dataset files")
        return None
    
    # Configure Together AI integration
    if not TogetherAIAdapter.set_api_integration():
        print("Error: Failed to configure Together AI integration")
        return None
    
    # Print configuration
    print(f"Using Together AI model: {os.getenv('TOGETHER_MODEL', 'meta-llama/Meta-Llama-3.1-70B-Instruct')}")
    print(f"Database ID: {db_id}")
    print(f"Question: {question}")
    print("")
    
    # Initialize enhanced chat manager
    manager = EnhancedChatManager(
        data_path=str(db_path),
        tables_json_path=str(tables_path),
        log_path="logs/spider_example.log",
        model_name=os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct"),
        dataset_name="spider"
    )
    
    # Create message for chat manager
    message = {
        'db_id': db_id,
        'query': question,
        'evidence': '',  # Spider doesn't use evidence
        'extracted_schema': {},
        'ground_truth': '',  # No ground truth in this example
        'difficulty': 'unknown',
        'send_to': "Selector"
    }
    
    print("Processing query through agents...")
    
    # Process through agents
    manager.start(message)
    
    # Get the generated SQL
    generated_sql = message.get('pred', '')
    
    print("\nGenerated SQL:")
    print(generated_sql)
    
    # Return the generated SQL
    return generated_sql

def main():
    """
    Main function with example usage
    """
    # Example query for the Spider dataset
    # This uses the 'concert_singer' database from Spider
    db_id = "concert_singer"
    question = "What is the name of the singer who has the most concerts?"
    
    # Process the query
    generated_sql = process_query(db_id, question)
    
    # Save the result to a file
    if generated_sql:
        result = {
            "db_id": db_id,
            "question": question,
            "generated_sql": generated_sql
        }
        
        with open("output/spider_example_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print("\nResult saved to output/spider_example_result.json")

if __name__ == "__main__":
    main() 