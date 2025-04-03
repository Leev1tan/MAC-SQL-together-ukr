#!/usr/bin/env python
"""
PostgreSQL connection utilities for BIRD-UKR dataset.
Provides connection pooling and query execution for PostgreSQL databases.
"""

import os
import time
import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Tuple, Any, Optional, Union
from dotenv import load_dotenv
from queue import Queue

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# PostgreSQL connection parameters
PG_USER = os.environ.get('PG_USER', 'postgres')
PG_PASSWORD = os.environ.get('PG_PASSWORD', '')
PG_HOST = os.environ.get('PG_HOST', 'localhost')
PG_PORT = os.environ.get('PG_PORT', '5432')

# Global connection pools
_connection_pools = {}

def init_connection_pool(db_name: str, pool_size: int = 5) -> None:
    """
    Initialize a connection pool for a database.
    
    Args:
        db_name: Database name
        pool_size: Number of connections in the pool
    """
    if db_name in _connection_pools:
        logger.warning(f"Connection pool for {db_name} already exists")
        return
    
    # Get PostgreSQL credentials from environment
    pg_user = os.environ.get('PG_USER', 'postgres')
    pg_password = os.environ.get('PG_PASSWORD', '')
    pg_host = os.environ.get('PG_HOST', 'localhost')
    pg_port = os.environ.get('PG_PORT', '5432')
    
    # Create a pool of connections
    pool = Queue(pool_size)
    
    # Initialize connections
    for _ in range(pool_size):
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=pg_user,
                password=pg_password,
                host=pg_host,
                port=pg_port
            )
            # Set timeout to avoid long-running queries
            cursor = conn.cursor()
            cursor.execute("SET statement_timeout = 30000")  # 30 seconds
            conn.commit()
            cursor.close()
            
            # Add to pool
            pool.put(conn)
        except Exception as e:
            logger.error(f"Error creating connection for {db_name}: {e}")
    
    # Store the pool
    _connection_pools[db_name] = pool
    logger.info(f"Created connection pool for database: {db_name}")

def get_pool_connection(db_name: str) -> Optional[Any]:
    """
    Get a connection from the pool.
    
    Args:
        db_name: Database name
        
    Returns:
        Database connection or None if no pool exists
    """
    if db_name not in _connection_pools:
        logger.warning(f"No connection pool for {db_name}")
        return None
    
    # Wait up to 5 seconds for a connection
    try:
        return _connection_pools[db_name].get(timeout=5)
    except Exception as e:
        logger.error(f"Error getting connection from pool for {db_name}: {e}")
        return None

def return_connection(db_name: str, connection: Any) -> None:
    """
    Return a connection to the pool.
    
    Args:
        db_name: Database name
        connection: Connection to return
    """
    if db_name not in _connection_pools:
        logger.warning(f"No connection pool for {db_name}")
        return
    
    # Reset the connection before returning it
    try:
        connection.rollback()  # Rollback any pending transaction
        cursor = connection.cursor()
        cursor.execute("SET statement_timeout = 30000")  # Reset timeout
        connection.commit()
        cursor.close()
        
        # Return to pool
        _connection_pools[db_name].put(connection)
    except Exception as e:
        logger.error(f"Error returning connection to pool for {db_name}: {e}")
        
        # Try to close the connection
        try:
            connection.close()
        except:
            pass

def close_connection_pool(db_name: str) -> None:
    """
    Close all connections in a pool.
    
    Args:
        db_name: Database name
    """
    if db_name not in _connection_pools:
        logger.warning(f"No connection pool for {db_name}")
        return
    
    # Close all connections
    pool = _connection_pools[db_name]
    closed_count = 0
    
    while not pool.empty():
        try:
            conn = pool.get_nowait()
            conn.close()
            closed_count += 1
        except Exception as e:
            logger.error(f"Error closing connection for {db_name}: {e}")
    
    # Remove the pool
    del _connection_pools[db_name]
    logger.info(f"Closed connection pool for {db_name}")

def execute_query(db_name: str, query: str, params: Optional[Dict] = None, 
                  as_dict: bool = False, timeout: float = 30.0) -> Tuple[bool, Any, float]:
    """
    Execute a SQL query on a PostgreSQL database and measure execution time.
    
    Args:
        db_name: PostgreSQL database name
        query: SQL query to execute
        params: Query parameters (if any)
        as_dict: Return results as dictionaries instead of tuples
        timeout: Query timeout in seconds
        
    Returns:
        Tuple of (success, results, execution_time)
        If success is False, results contains an error message
    """
    connection = None
    try:
        # Get connection from pool
        connection = get_pool_connection(db_name)
        if connection is None:
            return False, "Failed to get connection from pool", 0
        
        # Create cursor (dict or tuple based)
        cursor_type = RealDictCursor if as_dict else None
        cursor = connection.cursor(cursor_factory=cursor_type)
        
        # Set statement timeout (milliseconds)
        cursor.execute(f"SET statement_timeout = {int(timeout * 1000)}")
        
        # Measure execution time
        start_time = time.time()
        cursor.execute(query, params)
        results = cursor.fetchall()
        execution_time = time.time() - start_time
        
        # Clean up
        cursor.close()
        return_connection(db_name, connection)
        
        return True, results, execution_time
    except psycopg2.Error as e:
        if connection:
            connection.rollback()  # Roll back on error
            return_connection(db_name, connection)
        return False, str(e), 0
    except Exception as e:
        if connection:
            return_connection(db_name, connection)
        return False, str(e), 0

def execute_and_compare_queries(db_name: str, pred_sql: str, gold_sql: str, 
                               timeout: float = 30.0) -> Dict[str, Any]:
    """
    Execute both predicted and gold SQL queries and compare their results.
    
    Args:
        db_name: PostgreSQL database name
        pred_sql: Predicted SQL query
        gold_sql: Gold standard SQL query
        timeout: Query timeout in seconds
        
    Returns:
        Dictionary with execution results and timing information
    """
    result = {
        "execution_match": False,
        "gold_time": 0,
        "pred_time": 0,
        "gold_error": None,
        "pred_error": None
    }
    
    if not pred_sql or not gold_sql:
        result["pred_error"] = "Empty SQL query"
        return result
    
    # Execute gold SQL first to check if it's valid
    gold_success, gold_result, gold_time = execute_query(db_name, gold_sql, timeout=timeout)
    
    if not gold_success:
        result["gold_error"] = str(gold_result)
        return result
    
    result["gold_time"] = gold_time
    
    # Execute predicted SQL
    pred_success, pred_result, pred_time = execute_query(db_name, pred_sql, timeout=timeout)
    
    if not pred_success:
        result["pred_error"] = str(pred_result)
        return result
    
    result["pred_time"] = pred_time
    
    # Compare results
    # For PostgreSQL, we normalize results to handle ordering differences
    try:
        execution_match = compare_query_results(gold_result, pred_result)
        result["execution_match"] = execution_match
    except Exception as e:
        result["pred_error"] = f"Error comparing results: {str(e)}"
    
    return result

def compare_query_results(gold_result: List, pred_result: List) -> bool:
    """
    Compare query results with proper normalization for PostgreSQL.
    
    Args:
        gold_result: Gold standard query results
        pred_result: Predicted query results
        
    Returns:
        True if results match, False otherwise
    """
    # Check if we have same row counts
    if len(gold_result) != len(pred_result):
        return False
    
    # Handle empty results
    if len(gold_result) == 0 and len(pred_result) == 0:
        return True
    
    # Convert both results to sets of tuples for comparison
    # This addresses ordering differences
    gold_set = set()
    pred_set = set()
    
    # Convert each row to a string tuple for comparison
    for row in gold_result:
        if isinstance(row, dict):
            # Handle dict result
            values = tuple(str(v) for v in row.values())
        else:
            # Handle tuple result
            values = tuple(str(v) for v in row)
        gold_set.add(values)
    
    for row in pred_result:
        if isinstance(row, dict):
            # Handle dict result
            values = tuple(str(v) for v in row.values())
        else:
            # Handle tuple result
            values = tuple(str(v) for v in row)
        pred_set.add(values)
    
    # Compare sets
    return gold_set == pred_set

def get_database_schema(db_name: str) -> Tuple[bool, Union[List[Dict], str]]:
    """
    Get schema information for a database.
    
    Args:
        db_name: PostgreSQL database name
        
    Returns:
        Tuple of (success, result)
        If success is True, result contains schema information
        If success is False, result contains an error message
    """
    query = """
    SELECT 
        t.table_name, 
        c.column_name, 
        c.data_type,
        c.is_nullable,
        (SELECT count(*) FROM information_schema.table_constraints tc
         JOIN information_schema.constraint_column_usage ccu 
         ON tc.constraint_name = ccu.constraint_name
         WHERE tc.constraint_type = 'PRIMARY KEY' 
         AND tc.table_name = t.table_name 
         AND ccu.column_name = c.column_name) > 0 as is_primary,
        obj_description(pgc.oid) as table_comment
    FROM 
        information_schema.tables t
    JOIN 
        information_schema.columns c ON t.table_name = c.table_name
    LEFT JOIN 
        pg_class pgc ON pgc.relname = t.table_name
    WHERE 
        t.table_schema = 'public'
    ORDER BY 
        t.table_name, 
        c.ordinal_position;
    """
    
    success, result, _ = execute_query(db_name, query, as_dict=True)
    return success, result

def close_all_connection_pools():
    """
    Close all connection pools.
    """
    logger = logging.getLogger(__name__)
    
    # Get all database IDs with open pools
    db_ids = list(_connection_pools.keys())
    
    # Close each pool
    for db_id in db_ids:
        try:
            close_connection_pool(db_id)
        except Exception as e:
            logger.error(f"Error closing connection pool for database {db_id}: {e}")
    
    # Clear the pools dictionary
    _connection_pools.clear()

if __name__ == "__main__":
    # Test connection functionality
    logging.basicConfig(level=logging.INFO)
    
    TEST_DB = "інтернет_магазин"  # Replace with a valid database name
    test_query = "SELECT * FROM інформація_система LIMIT 5;"
    
    print(f"Testing connection to {TEST_DB}...")
    init_connection_pool(TEST_DB)
    
    success, result, exec_time = execute_query(TEST_DB, test_query)
    if success:
        print(f"Query executed in {exec_time:.4f} seconds")
        print(f"Number of rows: {len(result)}")
    else:
        print(f"Error: {result}")
    
    close_connection_pool(TEST_DB) 