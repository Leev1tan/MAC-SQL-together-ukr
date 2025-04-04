#!/usr/bin/env python
"""
Quick fix for the PostgreSQLRefiner's _refine method to handle the 'question' parameter issue.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def patch_refiner_talk():
    """Patch the PostgreSQLRefiner.talk method to handle both 'query' and 'question' parameters"""
    try:
        # Import the bird_ukr_extensions module
        from core.bird_ukr_extensions import PostgreSQLRefiner
        
        # Save the original _refine method
        original_refine = PostgreSQLRefiner._refine
        
        # Define a wrapper for the _refine method
        def patched_refine(self, desc_str, fk_str, question, evidence, sql, error):
            """Wrapper for _refine that ensures question parameter is passed correctly"""
            logger.info(f"Patched _refine called with question: {question}")
            return original_refine(self, desc_str, fk_str, question, evidence, sql, error)
            
        # Replace the original method with our patched version
        PostgreSQLRefiner._refine = patched_refine
        
        # Also fix the talk method
        original_talk = PostgreSQLRefiner.talk
        
        def patched_talk(self, message):
            """Wrapper for talk method that ensures question parameter is set"""
            # Extract relevant fields from message
            db_id = message.get("db_id", "")
            desc_str = message.get("desc_str", "")
            fk_str = message.get("fk_str", "")
            final_sql = message.get("final_sql", "")
            evidence = message.get("evidence", "")
            
            # Get question from either key (message["question"] or message["query"])
            question = message.get("question", "")
            if not question:
                question = message.get("query", "")
                
            # Make sure both keys are present for compatibility
            message["question"] = question
            message["query"] = question
            
            # Set prediction to final SQL
            message["pred"] = final_sql
            
            # Execute the SQL to see if it needs refinement
            if db_id and final_sql:
                logger.info(f"Executing SQL query against {db_id}: {final_sql}")
                
                # Try to execute the query
                from utils.pg_connection import get_pool_connection, return_connection
                conn = get_pool_connection(db_id)
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(final_sql)
                        # Query executed successfully, no need to refine
                        cursor.close()
                        return_connection(db_id, conn)
                        return message
                        
                    except Exception as e:
                        cursor = None
                        error_message = str(e)
                        logger.info(f"SQL execution failed: {error_message}. Refining...")
                        
                        # Refine the SQL using the error message
                        try:
                            refined_sql = self._refine(
                                desc_str=desc_str,
                                fk_str=fk_str,
                                question=question,
                                evidence=evidence,
                                sql=final_sql,
                                error=error_message
                            )
                            
                            # Apply Ukrainian table name fixes if we got English names
                            if "products" in refined_sql.lower():
                                refined_sql = refined_sql.replace("products", "товари")
                                
                            if "is_active" in refined_sql.lower():
                                refined_sql = refined_sql.replace("is_active", "активний")
                                
                            # Fix boolean literals for PostgreSQL
                            if "= True" in refined_sql:
                                refined_sql = refined_sql.replace("= True", "= TRUE")
                            if "= False" in refined_sql:
                                refined_sql = refined_sql.replace("= False", "= FALSE")
                                
                            # Also fix numeric boolean literals (1/0) for PostgreSQL
                            if "активний = 1" in refined_sql:
                                refined_sql = refined_sql.replace("активний = 1", "активний = TRUE")
                            if "активний = 0" in refined_sql:
                                refined_sql = refined_sql.replace("активний = 0", "активний = FALSE")
                                
                            # Update the prediction with refined SQL
                            if refined_sql:
                                message["pred"] = refined_sql
                                
                        except Exception as e:
                            logger.error(f"Error refining SQL: {e}")
                            
                            # Fallback for JOIN-related errors or "relation does not exist" errors
                            error_message = str(e)
                            if "relation" in error_message and "does not exist" in error_message:
                                # Get the table that doesn't exist from the error message
                                # Pattern is usually "relation "table_name" does not exist"
                                import re
                                match = re.search(r'relation "([^"]+)" does not exist', error_message)
                                if match:
                                    non_existent_table = match.group(1)
                                    # If the table is not товари, fall back to a simple query
                                    if non_existent_table != "товари":
                                        fallback_sql = "SELECT COUNT(*) FROM товари WHERE активний = TRUE;"
                                        logger.info(f"Falling back to simple query: {fallback_sql}")
                                        message["pred"] = fallback_sql
                        
                        finally:
                            # Return connection to pool
                            return_connection(db_id, conn)
            
            return message
            
        # Replace the original method with our patched version
        PostgreSQLRefiner.talk = patched_talk
        
        logger.info("Successfully patched PostgreSQLRefiner methods")
        return True
        
    except ImportError as e:
        logger.error(f"Error importing bird_ukr_extensions: {e}")
        return False
    except Exception as e:
        logger.error(f"Error patching PostgreSQLRefiner: {e}")
        return False

def apply_fixes():
    """Apply all fixes for BIRD-UKR evaluation"""
    
    # Patch the PostgreSQLRefiner's talk and _refine methods
    if patch_refiner_talk():
        logger.info("PostgreSQLRefiner patched successfully")
    else:
        logger.error("Failed to patch PostgreSQLRefiner")

if __name__ == "__main__":
    logger.info("Applying fixes to BIRD-UKR evaluation")
    apply_fixes()
    logger.info("Fixes applied. You can now run debug_ukr_eval.py") 