"""
BIRD Dataset Extensions for MAC-SQL

This module provides enhanced agents and utilities specifically designed for the BIRD dataset.
"""

import os
import json
import sqlite3
import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.agents import Selector, Refiner
from core.const import SYSTEM_NAME

logger = logging.getLogger(__name__)

class EnhancedBirdSelector(Selector):
    """
    Enhanced Selector agent for BIRD dataset.
    
    This agent extends the standard Selector with improved schema formatting
    and pruning for BIRD databases.
    """
    
    def call_llm(self, prompt, temperature=None):
        """
        Call the Language Model with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Optional temperature parameter for the LLM
            
        Returns:
            The LLM's response as a string
        """
        from core import llm
        from core.utils import extract_world_info
        
        # Extract any required info from the message context
        word_info = extract_world_info(getattr(self, '_message', {}))
        
        # Set temperature if provided, otherwise use the default
        if temperature is not None:
            word_info['temperature'] = temperature
            
        # Call the LLM and return the response
        logger.info("Calling LLM with BIRD-specific selector prompt")
        response = llm.safe_call_llm(prompt, **word_info)
        return response
    
    def _format_bird_schema(self, db_id: str, schema_info: dict) -> str:
        """
        Format BIRD schema in a way that's optimized for the LLM, including example values.
        
        Args:
            db_id: Database ID
            schema_info: Schema information dictionary
            
        Returns:
            Formatted schema string
        """
        # Access the full DB info including values from the cache
        # Note: Selector base class loads db2infos in _load_db_info if not lazy
        # Or it's loaded within _load_single_db_info if called.
        # We assume self.db2infos[db_id] is populated before this formatting call.
        full_db_info = self.db2infos.get(db_id, {})
        value_dict = full_db_info.get('value_dict', {}) # {table_name: [(col_name, val_str), ...]}

        # Create a lookup for faster value retrieval
        table_value_lookup = {}
        for table_name, columns_values in value_dict.items():
            table_value_lookup[table_name] = {col_name: val_str for col_name, val_str in columns_values}

        result = [f"Database: {db_id}"]
        
        # Format tables and columns
        tables = schema_info.get('tables', [])
        for table in tables:
            table_name = table.get('table_name', '')
            result.append(f"\nTable: {table_name}")
            result.append("Columns:")

            column_value_lookup = table_value_lookup.get(table_name, {})
            # Column information with data types
            for column in table.get('columns', []):
                column_name = column.get('column_name', '')
                column_type = column.get('column_type', 'text').upper()
                column_info = f"  {column_name} ({column_type})"
                
                # Add primary key information if available
                if column.get('is_primary_key', False):
                    column_info += " PRIMARY KEY"
                    
                # Add example values if available
                example_values = column_value_lookup.get(column_name, '')
                if example_values:
                    column_info += f" Value examples: {example_values}"
                
                result.append(column_info)
        
        # Format foreign keys if available
        foreign_keys = []
        for fk in schema_info.get('foreign_keys', []):
            source_table = fk.get('source_table', '')
            source_column = fk.get('source_column', '')
            target_table = fk.get('target_table', '')
            target_column = fk.get('target_column', '')
            
            foreign_keys.append(f"{source_table}.{source_column} = {target_table}.{target_column}")
        
        if foreign_keys:
            result.append("\nForeign Keys:")
            result.extend([f"  {fk}" for fk in foreign_keys])
        
        return "\n".join(result)
    
    def _load_db_info(self, db_id: str) -> str:
        """
        Enhanced database info loading with BIRD-specific optimizations.
        
        Args:
            db_id: Database ID
            
        Returns:
            Formatted schema information as string
        """
        # First check cache
        if db_id in self.db2infos:
            return self.db2infos[db_id]
        
        try:
            # Try to load BIRD tables.json
            with open(self.tables_json_path, 'r') as f:
                tables_json = json.load(f)
            
            # Find schema for this database
            db_schema = None
            for item in tables_json:
                if isinstance(item, dict) and item.get('db_id') == db_id:
                    db_schema = item
                    break
            
            if not db_schema:
                logger.error(f"Schema for database {db_id} not found in {self.tables_json_path}")
                return f"Error: Schema for database {db_id} not found."
            
            # Format schema with BIRD-specific formatting
            formatted_schema = self._format_bird_schema(db_id, db_schema)
            
            # Cache and return
            self.db2infos[db_id] = formatted_schema
            return formatted_schema
            
        except Exception as e:
            logger.error(f"Error loading BIRD database info for {db_id}: {str(e)}")
            return f"Error loading database info: {str(e)}"
    
    def _prune(self, db_id: str, query: str, db_schema: str, db_fk: str, evidence: str = None) -> Dict:
        """
        Enhanced schema pruning for BIRD dataset.
        
        Args:
            db_id: Database ID
            query: Natural language query
            db_schema: Database schema string
            db_fk: Foreign key information
            evidence: Additional evidence for pruning
            
        Returns:
            Dictionary with pruned schema
        """
        if self.dataset_name.lower() == 'bird':
            # Add BIRD-specific evidence handling
            evidence_prompt = ""
            if evidence:
                evidence_prompt = f"""
Evidence: {evidence}

This evidence provides additional context that might help identify relevant tables and columns.
"""
            
            prompt = f"""Given the following database schema and a question, identify the tables and columns that are relevant for answering the question.

DATABASE SCHEMA:
{db_schema}

FOREIGN KEY CONSTRAINTS:
{db_fk}

QUESTION: {query}
{evidence_prompt}
Think step by step to select the relevant tables and columns for answering this question.
First, identify key entities and conditions from the question.
Then, trace through the schema to find matching tables and their relationships.
Focus on tables and columns that are directly relevant to the question.
Consider join conditions needed to connect relevant tables.

PRUNED DATABASE SCHEMA:"""
            
            # Call LLM for pruning
            logger.info(f"Using enhanced BIRD pruning for {db_id}")
            response = self.call_llm(prompt)
            
            return {"pruned_schema": response.strip()}
        else:
            # Use original method for other datasets
            return super()._prune(db_id, query, db_schema, db_fk, evidence)
    
    def talk(self, message: Dict):
        """Enhanced talk method with BIRD dataset optimizations"""
        if self.dataset_name.lower() == 'bird':
            # Add dataset-specific metadata
            message['dataset_type'] = 'bird'
        
        # Process with parent method
        super().talk(message)


class EnhancedBirdRefiner(Refiner):
    """
    Enhanced Refiner agent for BIRD dataset.
    
    This agent extends the standard Refiner with improved validation
    and error correction for BIRD queries.
    """
    
    def call_llm(self, prompt, temperature=None):
        """
        Call the Language Model with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Optional temperature parameter for the LLM
            
        Returns:
            The LLM's response as a string
        """
        from core import llm
        from core.utils import extract_world_info
        
        # Extract any required info from the message context
        word_info = extract_world_info(getattr(self, '_message', {}))
        
        # Set temperature if provided, otherwise use the default
        if temperature is not None:
            word_info['temperature'] = temperature
            
        # Call the LLM and return the response
        logger.info("Calling LLM with BIRD-specific prompt")
        response = llm.safe_call_llm(prompt, **word_info)
        return response
    
    def _fix_bird_column_names(self, sql: str, db_id: str) -> str:
        """
        Fix common column name issues in BIRD-generated SQL.
        
        Args:
            sql: SQL query
            db_id: Database ID
            
        Returns:
            Fixed SQL query
        """
        # Strip any extra double quotes that might be causing issues
        sql = sql.replace('"', '')
        
        # Remove any backtick quotes that might be causing issues
        sql = sql.replace('`', '')
        
        # Make sure it's a string
        if isinstance(sql, dict) and 'refined_sql' in sql:
            sql = sql['refined_sql']
            
        # Return the simplified SQL without extra quotes
        return sql
    
    def _execute_sql(self, sql: str, db_id: str) -> Dict:
        """
        Execute SQL with BIRD-specific fixes.
        
        Args:
            sql: SQL query
            db_id: Database ID
            
        Returns:
            Execution result dictionary
        """
        # Apply BIRD-specific fixes
        if self.dataset_name.lower() == 'bird':
            sql = self._fix_bird_column_names(sql, db_id)
        
        # For BIRD, adjust database path
        try:
            # Find database file for BIRD dataset
            db_file = os.path.join(self.data_path, "dev_databases", db_id, f"{db_id}.sqlite")
            
            if not os.path.exists(db_file):
                # Try alternative path without the extra 'dev_databases' directory
                db_file = os.path.join(self.data_path, db_id, f"{db_id}.sqlite")
                if not os.path.exists(db_file):
                    logger.error(f"BIRD database file not found: {db_file}")
                    return {"error": True, "error_msg": f"Database file not found: {db_file}"}
            
            # Connect to database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(sql)
            data = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Close connection
            conn.close()
            
            return {
                "error": False, 
                "data": data, 
                "columns": column_names,
                "sql": sql
            }
            
        except Exception as e:
            logger.error(f"Error executing BIRD SQL: {str(e)}")
            return {"error": True, "error_msg": str(e), "sql": sql}
    
    def _refine(self, query: str, evidence: str, schema_info: str, fk_info: str, error_info: Dict) -> Dict:
        """
        Enhanced SQL refinement with BIRD-specific handling.
        
        Args:
            query: Natural language query
            evidence: Additional evidence
            schema_info: Database schema information
            fk_info: Foreign key constraints
            error_info: Error information from SQL execution
            
        Returns:
            Dictionary with refined SQL
        """
        # For BIRD dataset, add evidence to the prompt
        if self.dataset_name.lower() == 'bird' and evidence:
            evidence_prompt = f"""
Evidence: {evidence}

This evidence provides additional context that might help refine the SQL query.
"""
            
            # Format execution result
            if error_info.get('error', False):
                execution_result = f"Error: {error_info.get('error_msg', 'Unknown error')}"
            else:
                data = error_info.get('data', [])
                columns = error_info.get('columns', [])
                
                # Format result as table
                execution_result = "Success. Results:\n"
                if columns:
                    execution_result += "| " + " | ".join(columns) + " |\n"
                    execution_result += "| " + " | ".join(["---"] * len(columns)) + " |\n"
                
                # Add first few rows
                max_rows = 5
                for i, row in enumerate(data[:max_rows]):
                    execution_result += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
                
                if len(data) > max_rows:
                    execution_result += f"... and {len(data) - max_rows} more rows\n"
            
            prompt = f"""The previous SQL query needs to be refined based on the database schema and execution results.

QUESTION: {query}

DATABASE SCHEMA:
{schema_info}

{evidence_prompt}
PREVIOUS SQL QUERY:
{error_info.get('sql', '')}

EXECUTION RESULT:
{execution_result}

Analyze the query and execution results to identify any issues. Consider:
1. SQL syntax errors
2. Incorrect table or column references
3. Logic errors in joins or conditions
4. Missing or incorrect aggregations

Provide a refined SQL query that correctly answers the question:"""
            
            # Call LLM for refinement
            logger.info("Using enhanced BIRD refinement")
            response = self.call_llm(prompt)
            
            # Extract SQL from response
            import re
            sql_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL)
            if sql_match:
                return sql_match.group(1).strip()
            
            # If no SQL code block, try to extract any SQL-like content
            sql_match = re.search(r'SELECT\s+.*?(?:;|$)', response, re.DOTALL | re.IGNORECASE)
            if sql_match:
                return sql_match.group(0).strip()
            
            # Return the whole response as a fallback
            return response.strip()
        else:
            # Use original method for other cases
            result = super()._refine(query, evidence, schema_info, fk_info, error_info)
            # If the original returns a dict, extract the 'refined_sql' value
            if isinstance(result, dict) and 'refined_sql' in result:
                return result['refined_sql']
            return result
    
    def talk(self, message: Dict):
        """Enhanced talk method with BIRD dataset validation"""
        # Process with parent method first
        super().talk(message)
        
        # Add BIRD-specific validation
        if self.dataset_name.lower() == 'bird' and 'pred' in message and 'ground_truth' in message:
            try:
                # Fix any formatting issues specific to BIRD
                message['pred'] = self._fix_bird_column_names(message['pred'], message['db_id'])
                
                # Execute both predicted and ground truth queries
                pred_result = self._execute_sql(message['pred'], message['db_id'])
                gold_result = self._execute_sql(message['ground_truth'], message['db_id'])
                
                # Compare results
                pred_success = not pred_result.get('error', True)
                gold_success = not gold_result.get('error', True)
                
                # Check if both queries executed successfully
                if pred_success and gold_success:
                    # Compare result sets (simplified)
                    pred_data = pred_result.get('data', [])
                    gold_data = gold_result.get('data', [])
                    
                    # Simple exact match for now
                    execution_match = (pred_data == gold_data)
                    
                    # Store execution evaluation results
                    message['execution_match'] = execution_match
                    
                    # If execution matching is successful, terminate the conversation
                    if execution_match:
                        message['send_to'] = SYSTEM_NAME
                        logger.info("Execution match successful, terminating agent chain")
                
            except Exception as e:
                # If execution-based evaluation fails, just continue
                logger.error(f"Error in BIRD validation: {str(e)}")
                message['execution_error'] = str(e)


# Helper function to load BIRD queries
def load_bird_subset(dataset_path, num_samples=5):
    """
    Load a subset of queries from the BIRD dataset.
    
    Args:
        dataset_path: Path to the BIRD dataset JSON file
        num_samples: Number of samples to load
        
    Returns:
        List of query dictionaries
    """
    from pathlib import Path
    import json
    import random
    
    # Load the dataset
    try:
        with open(dataset_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading BIRD dataset: {e}")
        return []
    
    # Get the data array
    if isinstance(data, dict) and 'data' in data:
        items = data['data']
    elif isinstance(data, list):
        items = data
    else:
        logger.error(f"Unexpected BIRD data format: {type(data)}")
        return []
    
    # Limit to num_samples
    if len(items) > num_samples:
        # Randomly sample to get a diverse set
        samples = random.sample(items, num_samples)
    else:
        samples = items
    
    # Format the samples for the agent
    formatted_samples = []
    for item in samples:
        formatted_item = {
            'db_id': item.get('db_id', ''),
            'question': item.get('question', ''),
            'SQL': item.get('SQL', ''),
            'evidence': item.get('evidence', ''),
            'difficulty': item.get('difficulty', 'unknown')
        }
        formatted_samples.append(formatted_item)
    
    return formatted_samples 