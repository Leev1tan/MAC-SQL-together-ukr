#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enhanced Chat Manager with support for both PostgreSQL and SQLite databases.
This module extends the existing functionality to support the BIRD-UKR dataset.
"""

# Import all necessary components from the existing code
from core.enhanced_chat_manager import EnhancedChatManager, Message, QueryState
from core.const import (
    SELECTOR_NAME, DECOMPOSER_NAME, REFINER_NAME, SYSTEM_NAME,
    SELECTOR_PROMPT_UK, DECOMPOSER_PROMPT_UK, REFINER_PROMPT_UK,
    BIRD_UKR_QUESTION_PATH, BIRD_UKR_TABLES_PATH
)
from core.db_utils import get_db_connection, get_schema, format_schema_for_prompt, execute_query

# This is an example class that shows how the database utilities would be integrated
# with the existing EnhancedChatManager. This is NOT meant to replace the existing
# EnhancedChatManager directly, but to provide a guide for how to integrate PostgreSQL
# support into it.
class PgEnhancedChatManager:
    """
    Enhanced Chat Manager with support for both PostgreSQL and SQLite databases.
    This is an example class showing the changes needed to support BIRD-UKR.
    """
    
    def __init__(self, config):
        self.config = config
        self.dataset_name = config.get('dataset_name', 'spider')
        self.query_state = QueryState()
        
        # Language detection (Ukrainian for BIRD-UKR, English for others)
        self.language = 'uk' if self.dataset_name == 'bird-ukr' else 'en'
        
        # Select appropriate prompts based on language
        if self.language == 'uk':
            self.selector_prompt = SELECTOR_PROMPT_UK
            self.decomposer_prompt = DECOMPOSER_PROMPT_UK
            self.refiner_prompt = REFINER_PROMPT_UK
        else:
            # Use existing English prompts
            # This would be imported from the existing EnhancedChatManager
            pass
    
    def get_database_connection(self, db_id):
        """
        Get a database connection based on the dataset type.
        
        Args:
            db_id: Database identifier
            
        Returns:
            tuple: (connection, db_type)
        """
        # Use the unified connection function from db_utils
        db_base_path = self.config.get('db_path', None)
        return get_db_connection(self.dataset_name, db_id, db_base_path)
    
    def get_database_schema(self, conn, db_type):
        """
        Get database schema information.
        
        Args:
            conn: Database connection
            db_type: Database type ('sqlite' or 'postgres')
            
        Returns:
            str: Formatted schema string for prompts
        """
        # Get schema information
        schema_info = get_schema(conn, db_type)
        
        # Format schema for prompt
        return format_schema_for_prompt(schema_info)
    
    def execute_sql_query(self, conn, db_type, query):
        """
        Execute an SQL query on the connected database.
        
        Args:
            conn: Database connection
            db_type: Database type ('sqlite' or 'postgres')
            query: SQL query to execute
            
        Returns:
            dict: Query results with rows and column names
        """
        return execute_query(conn, query, db_type)
    
    def process_query(self, user_query, db_id):
        """
        Process a user query against a specific database.
        
        Args:
            user_query: Natural language query from user
            db_id: Database identifier
            
        Returns:
            str: Generated SQL query
        """
        # Get database connection
        conn, db_type = self.get_database_connection(db_id)
        
        # Get database schema
        schema_str = self.get_database_schema(conn, db_type)
        
        # Here would be the existing logic for:
        # 1. Running the Selector agent
        # 2. Running the Decomposer agent
        # 3. Running the Refiner agent
        # 4. Executing the generated query (for validation)
        # 5. Returning the result
        
        # This is just a placeholder to show where the integration would happen
        return "SELECT * FROM example_table"  # Placeholder
    
    def close(self):
        """Close any open resources"""
        # Cleanup logic here
        pass


# Example usage:
def main():
    # Configuration would typically come from command line arguments or a config file
    config = {
        'dataset_name': 'bird-ukr',  # Or 'spider' or 'bird'
        'engine': 'meta-llama/Llama-3.3-70B-Instruct-Turbo',
        'temperature': 0.1,
        'api_key': 'YOUR_API_KEY'  # Should come from .env
    }
    
    # Initialize the manager
    manager = PgEnhancedChatManager(config)
    
    # Process a query
    sql_query = manager.process_query(
        user_query="Скільки студентів навчається на факультеті комп'ютерних наук?",
        db_id="університет"
    )
    
    print(f"Generated SQL: {sql_query}")
    
    # Clean up
    manager.close()

if __name__ == "__main__":
    main() 