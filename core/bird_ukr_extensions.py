#!/usr/bin/env python
"""
Extensions for the BIRD-UKR dataset.
Provides PostgreSQL-compatible agents for the Ukrainian BIRD dataset.
"""

import os
import logging
import time
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Tuple, Optional

from utils.pg_selector import PostgreSQLSelector
from core.agents import Decomposer, Refiner, BaseAgent
from core.const_ukr import SELECTOR_NAME, DECOMPOSER_NAME, REFINER_NAME, refiner_template_ukr
from core.utils import parse_sql_from_string
from core.api import safe_call_llm
from utils.pg_connection import get_pool_connection, return_connection

logger = logging.getLogger(__name__)

class PostgreSQLRefiner(BaseAgent):
    """
    PostgreSQL Refiner for executing SQL queries against PostgreSQL databases.
    """
    
    def __init__(self, data_path: str, model_name: str, dataset_name: str):
        """
        Initialize the PostgreSQL Refiner.
        
        Args:
            data_path: Path to the dataset
            model_name: Name of the model to use
            dataset_name: Name of the dataset
        """
        super().__init__()
        self.name = REFINER_NAME
        self.data_path = data_path
        self.model_name = model_name
        self.dataset_name = dataset_name
        
        # Get PostgreSQL credentials from environment
        self.pg_user = os.environ.get('PG_USER', 'postgres')
        self.pg_password = os.environ.get('PG_PASSWORD', '')
        self.pg_host = os.environ.get('PG_HOST', 'localhost')
        self.pg_port = os.environ.get('PG_PORT', '5432')
        
        logger.info("Initialized PostgreSQL Refiner")
    
    def talk(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message, execute the SQL query, and refine if needed.
        
        Args:
            message: The message to process
            
        Returns:
            The updated message
        """
        # Get relevant data from message
        db_id = message.get("db_id", "")
        pred_sql = message.get("pred", "")
        query = message.get("query", "")
        desc_str = message.get("desc_str", "")
        fk_str = message.get("fk_str", "")
        try_times = message.get("try_times", 0)
        
        # Check if there's a final_sql field and use it if pred_sql is empty
        if not pred_sql and "final_sql" in message:
            pred_sql = message.get("final_sql", "")
            # Store the SQL in the pred field for consistency
            message["pred"] = pred_sql
        
        # Initialize result
        message["try_times"] = try_times + 1
        
        # Check if we have all required information
        if not db_id or not pred_sql:
            logger.warning("Missing db_id or SQL query")
            message["send_to"] = "System"
            return message
        
        # Try to execute the SQL
        logger.info(f"Executing SQL query against {db_id}: {pred_sql}")
        success, result, error = self._execute_sql(db_id, pred_sql)
        
        # Check if we need to refine
        if not success and try_times < 3:
            # SQL execution failed, need to refine
            logger.info(f"SQL execution failed: {error}. Refining...")
            
            new_sql = self._refine(
                query=query, 
                evidence=message.get("evidence", ""),
                desc_str=desc_str, 
                fk_str=fk_str, 
                sql=pred_sql, 
                sqlite_error=error
            )
            
            if new_sql and new_sql != pred_sql:
                # We got a refined SQL query, try again
                message["pred"] = new_sql
                message["fixed"] = True
                message["send_to"] = REFINER_NAME  # Send back to self for another try
                return message
        
        # No need to refine or refinement failed/not possible
        message["send_to"] = "System"
        message["execution_result"] = result if success else None
        message["execution_error"] = error if not success else None
        
        return message
    
    def _execute_sql(self, db_id: str, sql: str) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Execute SQL query against a PostgreSQL database.
        
        Args:
            db_id: Database identifier
            sql: SQL query to execute
            
        Returns:
            Tuple of (success, result, error_message)
        """
        try:
            # Create connection
            conn = psycopg2.connect(
                dbname=db_id,
                user=self.pg_user,
                password=self.pg_password,
                host=self.pg_host,
                port=self.pg_port
            )
            
            # Create cursor
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Set timeout (30 seconds)
            cursor.execute("SET statement_timeout = 30000")
            
            # Execute query
            start_time = time.time()
            cursor.execute(sql)
            result = cursor.fetchall()
            execution_time = time.time() - start_time
            
            # Convert result to list of dictionaries
            result_list = [dict(row) for row in result]
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            logger.info(f"SQL executed successfully in {execution_time:.2f}s. Rows: {len(result_list)}")
            return True, result_list, None
            
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
            return False, None, str(e)
    
    def _refine(self, query: str, evidence: str, desc_str: str, 
                fk_str: str, sql: str, sqlite_error: str) -> str:
        """
        Refine the SQL query based on the error.
        
        Args:
            query: Natural language query
            evidence: Additional evidence
            desc_str: Database schema description
            fk_str: Foreign key description
            sql: Original SQL query that failed
            sqlite_error: Error message from PostgreSQL
            
        Returns:
            Refined SQL query
        """
        try:
            # Create prompt for the LLM
            prompt = refiner_template_ukr.format(
                question=query,
                evidence=evidence,
                desc_str=desc_str,
                fk_str=fk_str,
                sql=sql,
                sqlite_error=sqlite_error,
                exception_class="PostgreSQLError"
            )
            
            # Call the LLM
            response = safe_call_llm(prompt)
            
            # Parse the SQL from the response
            new_sql = parse_sql_from_string(response)
            
            if new_sql and new_sql != sql:
                logger.info(f"Refined SQL: {new_sql}")
                return new_sql
            else:
                logger.warning("Failed to extract valid refined SQL")
                return sql
                
        except Exception as e:
            logger.error(f"Error refining SQL: {str(e)}")
            return sql

def load_pg_selector(*args, **kwargs) -> PostgreSQLSelector:
    """
    Create and return a PostgreSQL-compatible Selector for the BIRD-UKR dataset.
    
    Args:
        *args: Additional positional arguments
        **kwargs: Additional keyword arguments
        
    Returns:
        PostgreSQLSelector instance
    """
    logger.info("Loading PostgreSQL Selector for BIRD-UKR dataset")
    selector = PostgreSQLSelector(*args, **kwargs)
    return selector

def load_bird_ukr_extensions(data_path: str, model_name: str, **kwargs) -> Dict[str, Any]:
    """
    Load the BIRD-UKR extension agents.
    
    Args:
        data_path: Path to the dataset
        model_name: Name of the model to use
        **kwargs: Additional keyword arguments
        
    Returns:
        Dictionary mapping agent names to agent instances
    """
    logger.info("Loading BIRD-UKR extensions")
    
    # Create the agents
    selector = load_pg_selector(
        data_path=data_path,
        tables_json_path=kwargs.get('tables_json_path'),
        model_name=model_name,
        dataset_name="bird-ukr"
    )
    
    decomposer = Decomposer(
        model_name=model_name,
        dataset_name="bird" # Use standard BIRD for decomposer as the prompt is similar
    )
    decomposer.name = DECOMPOSER_NAME
    
    refiner = PostgreSQLRefiner(
        data_path=data_path,
        model_name=model_name,
        dataset_name="bird-ukr"
    )
    
    # Create dictionary of agents
    agents = {
        SELECTOR_NAME: selector,
        DECOMPOSER_NAME: decomposer,
        REFINER_NAME: refiner
    }
    
    return agents 