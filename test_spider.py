#!/usr/bin/env python
"""
Simple test script for MAC-SQL with Together AI using the Spider dataset.
"""

import os
import json
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/test_spider.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import MAC-SQL components
from core.enhanced_chat_manager import EnhancedChatManager
from core.spider_extensions import load_spider_subset
from core.macsql_together_adapter import TogetherAIAdapter
from core.const import ENGINE_TOGETHER

# Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", ENGINE_TOGETHER)

def find_spider_data():
    """Find the Spider dataset files"""
    try:
        # Check multiple possible paths
        possible_paths = [
            Path("data/spider"),
            Path("MAC-SQL/data/spider"),
            Path("../MAC-SQL/data/spider")
        ]
        
        # Find the first existing path
        data_dir = None
        for path in possible_paths:
            if path.exists():
                data_dir = path
                break
        
        if not data_dir:
            logger.error(f"Spider data directory not found. Checked: {[str(p) for p in possible_paths]}")
            return None, None, None
        
        logger.info(f"Found Spider data directory at: {data_dir}")
        
        # Look for dev.json or train_spider.json
        dataset_options = [
            data_dir / "dev.json",
            data_dir / "train_spider.json"
        ]
        
        dataset_path = None
        for path in dataset_options:
            if path.exists():
                dataset_path = path
                break
        
        if not dataset_path:
            logger.error("Could not find Spider dataset file")
            return None, None, None
        
        # Look for tables.json
        tables_path = data_dir / "tables.json"
        if not tables_path.exists():
            logger.error("Could not find tables.json")
            return None, None, None
        
        # Look for database directory
        db_path = data_dir / "database"
        if not db_path.exists():
            logger.error("Could not find database directory")
            return None, None, None
        
        return dataset_path, db_path, tables_path
    
    except Exception as e:
        logger.error(f"Error finding Spider data: {str(e)}")
        return None, None, None

def test_single_query(db_id, question):
    """Test a single query using the agent-based approach"""
    dataset_path, db_path, tables_path = find_spider_data()
    if not dataset_path or not db_path or not tables_path:
        logger.error("Spider dataset files not found")
        return
    
    # Configure Together AI integration
    TogetherAIAdapter.set_api_integration()
    
    # Configure model
    model_name = TOGETHER_MODEL
    
    # Initialize chat manager
    manager = EnhancedChatManager(
        data_path=str(db_path),
        tables_json_path=str(tables_path),
        log_path="logs/test_spider_single.log",
        model_name=model_name,
        dataset_name="spider"
    )
    
    # Create message
    message = {
        'db_id': db_id,
        'query': question,
        'evidence': '',
        'extracted_schema': {},
        'ground_truth': '',
        'difficulty': 'unknown',
        'send_to': "Selector"
    }
    
    # Process through agents
    logger.info(f"Processing query for database '{db_id}': {question}")
    manager.start(message)
    
    # Show results
    if 'pred' in message:
        logger.info(f"Generated SQL: {message['pred']}")
        
        # Save result to file
        result = {
            'db_id': db_id,
            'question': question,
            'sql': message['pred']
        }
        
        os.makedirs("output", exist_ok=True)
        with open("output/test_spider_result.json", "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Result saved to output/test_spider_result.json")
    else:
        logger.error("No SQL generated")

def test_sample_queries(num_samples=3):
    """Test a sample of queries from the Spider dataset"""
    dataset_path, db_path, tables_path = find_spider_data()
    if not dataset_path or not db_path or not tables_path:
        logger.error("Spider dataset files not found")
        return
    
    # Load queries
    logger.info(f"Loading {num_samples} sample queries from {dataset_path}")
    queries = load_spider_subset(dataset_path, num_samples=num_samples)
    
    if not queries:
        logger.error("No queries loaded")
        return
    
    # Configure Together AI integration
    TogetherAIAdapter.set_api_integration()
    
    # Configure model
    model_name = TOGETHER_MODEL
    
    # Initialize chat manager
    manager = EnhancedChatManager(
        data_path=str(db_path),
        tables_json_path=str(tables_path),
        log_path="logs/test_spider_sample.log",
        model_name=model_name,
        dataset_name="spider"
    )
    
    # Process each query
    results = []
    for i, query in enumerate(queries):
        logger.info(f"Processing query {i+1}/{len(queries)}: {query['db_id']}")
        logger.info(f"Question: {query['question']}")
        
        # Create message
        message = {
            'db_id': query['db_id'],
            'query': query['question'],
            'evidence': '',
            'extracted_schema': {},
            'ground_truth': query.get('SQL', ''),
            'difficulty': query.get('difficulty', 'unknown'),
            'send_to': "Selector"
        }
        
        # Process through agents
        manager.start(message)
        
        # Store result
        result = {
            'db_id': query['db_id'],
            'question': query['question'],
            'sql': message.get('pred', ''),
            'ground_truth': query.get('SQL', ''),
            'execution_match': message.get('execution_match', False)
        }
        
        results.append(result)
        
        logger.info(f"Generated SQL: {result['sql']}")
        logger.info(f"Execution match: {result['execution_match']}")
        logger.info("-" * 50)
    
    # Save results
    os.makedirs("output", exist_ok=True)
    with open("output/test_spider_results.json", "w") as f:
        json.dump({'results': results}, f, indent=2)
    
    logger.info(f"Results saved to output/test_spider_results.json")
    
    # Calculate accuracy
    if results:
        execution_matches = sum(1 for r in results if r['execution_match'])
        accuracy = execution_matches / len(results)
        logger.info(f"Execution accuracy: {accuracy:.2%} ({execution_matches}/{len(results)})")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test MAC-SQL with Together AI on Spider dataset")
    parser.add_argument("--db", type=str, help="Database ID for single query test")
    parser.add_argument("--question", type=str, help="Question for single query test")
    parser.add_argument("--samples", type=int, default=3, help="Number of samples to test")
    
    args = parser.parse_args()
    
    if args.db and args.question:
        # Test single query
        test_single_query(args.db, args.question)
    else:
        # Test sample queries
        test_sample_queries(args.samples)

if __name__ == "__main__":
    main() 