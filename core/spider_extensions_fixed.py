"""
Spider Dataset Extensions for MAC-SQL
This module provides enhanced agents and utilities specifically designed for the Spider dataset.
"""

import os
import json
import sqlite3
import re
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

from core.agents import Selector, Refiner, Decomposer
from core.const import SYSTEM_NAME

logger = logging.getLogger(__name__)

class EnhancedSpiderSelector(Selector):
    """
    Enhanced Selector agent for Spider dataset.
    
    This agent extends the standard Selector with improved schema formatting
    and pruning for Spider databases.
    """
    
    def _format_spider_schema(self, db_id: str, schema_info: dict) -> str:
        """
        Format Spider schema in a way that's optimized for the LLM.
        
        Args:
            db_id: Database ID
            schema_info: Schema information dictionary
            
        Returns:
            Formatted schema string
        """
        result = [f"Database: {db_id}"]
        result.append("\nTables:")
        
        tables = schema_info.get('tables', [])
        for table in tables:
            table_name = table.get('table_name', '')
            result.append(f"\n{table_name}")
            
            # Column information with data types
            result.append("Columns:")
            for column in table.get('columns', []):
                column_name = column.get('column_name', '')
                column_type = column.get('column_type', 'text').upper()
                result.append(f"  {column_name} ({column_type})")
                
                # Add primary key information if available
                if column.get('is_primary_key', False):
                    result[-1] += " PRIMARY KEY"
        
        # Format foreign keys if available
        if 'foreign_keys' in schema_info and schema_info['foreign_keys']:
            result.append("\nForeign Keys:")
            for fk in schema_info['foreign_keys']:
                source_table = fk.get('source_table', '')
                source_column = fk.get('source_column', '')
                target_table = fk.get('target_table', '')
                target_column = fk.get('target_column', '')
                result.append(f"  {source_table}.{source_column} -> {target_table}.{target_column}")
        
        return "\n".join(result)
    
    def _load_db_info(self, db_id: str):
        """
        Enhanced database info loading with Spider-specific optimizations.
        
        Args:
            db_id: Database ID
            
        Returns:
            Formatted schema information
        """
        # First try standard method
        schema_info = super()._load_db_info(db_id)
        
        # If this is a Spider dataset, apply additional formatting
        if self.dataset_name.lower() == 'spider':
            # Check if we have schema info and it's in the expected format
            try:
                schema_dict = json.loads(schema_info) if isinstance(schema_info, str) else schema_info
                if isinstance(schema_dict, dict) and 'tables' in schema_dict:
                    # Apply Spider-specific formatting
                    return self._format_spider_schema(db_id, schema_dict)
            except:
                # If there's any error, just use the standard schema
                pass
        
        return schema_info
    
    def _prune(self, db_id: str, query: str, db_schema: str, db_fk: str, evidence: str = None) -> dict:
        """
        Enhanced schema pruning for Spider dataset.
        
        Args:
            db_id: Database ID
            query: Natural language query
            db_schema: Database schema string
            db_fk: Foreign key information
            evidence: Additional evidence for pruning
            
        Returns:
            Dictionary with pruned schema
        """
        if self.dataset_name.lower() == 'spider':
            prompt = f"""Given the following database schema and a question, identify the tables and columns that are relevant for answering the question.

DATABASE SCHEMA:
{db_schema}

FOREIGN KEY CONSTRAINTS:
{db_fk}

QUESTION: {query}

Think step by step to select the relevant tables and columns for answering this question.
First, identify key entities and conditions from the question.
Then, trace through the schema to find matching tables and their relationships.
Focus on tables and columns that are directly relevant to the question.
Consider join conditions needed to connect relevant tables.

PRUNED DATABASE SCHEMA:"""
            
            # Call LLM for pruning
            response = self.call_llm(prompt)
            
            return {"pruned_schema": response.strip()}
        else:
            # Use original method for other datasets
            return super()._prune(db_id, query, db_schema, db_fk, evidence)
    
    def talk(self, message: dict):
        """Enhanced talk method with Spider dataset optimizations"""
        if self.dataset_name.lower() == 'spider':
            # Add dataset-specific metadata
            message['dataset_type'] = 'spider'
        
        # Process with parent method
        super().talk(message)


class EnhancedSpiderRefiner(Refiner):
    """
    Enhanced Refiner agent for Spider dataset.
    
    This agent extends the standard Refiner with improved validation
    and error correction for Spider queries.
    """
    
    def _fix_spider_column_names(self, sql: str, db_id: str) -> str:
        """
        Fix common column name issues in Spider-generated SQL.
        
        Args:
            sql: SQL query
            db_id: Database ID
            
        Returns:
            Fixed SQL query
        """
        # Common fixes for Spider dataset
        
        # 1. Fix column references with table prefix but without quotes
        # Example: SELECT T1.student_id → SELECT T1."student_id"
        sql = re.sub(r'([Tt]\d+)\.([a-zA-Z_][a-zA-Z0-9_]*)', r'\1."\2"', sql)
        
        # 2. Fix missing quotes around table aliases
        # Example: AS T1 → AS "T1"
        sql = re.sub(r'\bAS\s+([Tt]\d+)\b', r'AS "\1"', sql, flags=re.IGNORECASE)
        
        # 3. Fix inconsistent table name casing
        sql = sql.replace(' Table ', ' table ')
        
        return sql
    
    def _execute_sql(self, sql: str, db_id: str) -> dict:
        """
        Execute SQL with Spider-specific fixes.
        
        Args:
            sql: SQL query
            db_id: Database ID
            
        Returns:
            Execution result dictionary
        """
        # Apply Spider-specific fixes
        if self.dataset_name.lower() == 'spider':
            sql = self._fix_spider_column_names(sql, db_id)
        
        # Call parent implementation
        return super()._execute_sql(sql, db_id)
    
    def _find_common_spider_errors(self, sql: str, error_msg: str, schema_info: str) -> str:
        """
        Find and fix common Spider dataset errors.
        
        Args:
            sql: SQL query with errors
            error_msg: Error message from execution
            schema_info: Database schema information
            
        Returns:
            Suggestions for fixing the errors
        """
        suggestions = []
        
        # Check for common Spider-specific errors
        
        # 1. No such table errors - common in Spider when using wrong table aliases
        if "no such table" in error_msg.lower():
            table_match = re.search(r'no such table:?\s*([^\s,;]+)', error_msg, re.IGNORECASE)
            if table_match:
                bad_table = table_match.group(1)
                suggestions.append(f"- Table '{bad_table}' is not found. Check table aliases and make sure all tables are properly referenced.")
                
                # Extract actual table names from schema
                table_names = re.findall(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*$', schema_info, re.MULTILINE)
                if table_names:
                    suggestions.append(f"- Available tables: {', '.join(table_names)}")
        
        # 2. No such column errors
        if "no such column" in error_msg.lower():
            col_match = re.search(r'no such column:?\s*([^\s,;]+)', error_msg, re.IGNORECASE)
            if col_match:
                bad_col = col_match.group(1)
                suggestions.append(f"- Column '{bad_col}' is not found. Check column names and table aliases.")
                
                # Try to extract table from bad column reference
                table_match = re.search(r'([Tt]\d+|[a-zA-Z_][a-zA-Z0-9_]*)\.', bad_col)
                if table_match:
                    table_name = table_match.group(1)
                    suggestions.append(f"- Check if table '{table_name}' has the referenced column.")
        
        # 3. Syntax errors
        if "syntax error" in error_msg.lower():
            # Check for join syntax errors
            if "JOIN" in sql:
                suggestions.append("- Check JOIN syntax. Make sure each JOIN has an ON condition with proper column references.")
            
            # Check for aggregation errors
            if any(x in sql.upper() for x in ["GROUP BY", "HAVING", "COUNT", "SUM", "AVG", "MAX", "MIN"]):
                suggestions.append("- Check aggregation functions and GROUP BY clause. Columns in SELECT that are not aggregated must appear in GROUP BY.")
        
        return "\n".join(suggestions) if suggestions else "No specific suggestions available for this error."
    
    def _refine(self, query: str, evidence: str, schema_info: str, fk_info: str, error_info: dict) -> dict:
        """
        Enhanced SQL refinement with Spider-specific handling.
        
        Args:
            query: Natural language query
            evidence: Additional evidence
            schema_info: Database schema information
            fk_info: Foreign key information
            error_info: Error information from SQL execution
            
        Returns:
            Dictionary with refined SQL
        """
        # For Spider dataset, add specific error analysis
        if self.dataset_name.lower() == 'spider' and error_info.get('error_msg'):
            suggestions = self._find_common_spider_errors(
                error_info.get('sql', ''),
                error_info.get('error_msg', ''),
                schema_info
            )
            
            prompt = f"""The previous SQL query has errors or does not produce correct results. Please fix the SQL query.

QUESTION: {query}

DATABASE SCHEMA:
{schema_info}

FOREIGN KEY CONSTRAINTS:
{fk_info}

PREVIOUS SQL QUERY WITH ERRORS:
{error_info.get('sql', '')}

ERROR MESSAGE:
{error_info.get('error_msg', '')}

ERROR ANALYSIS:
{suggestions}

Fix the SQL query to correctly answer the question. Make sure your query is properly formatted and uses valid tables and columns.

CORRECTED SQL QUERY:"""
            
            # Call LLM for refinement
            response = self.call_llm(prompt)
            
            # Extract SQL from response
            sql_match = re.search(r'```sql\s*(.*?)\s*```', response, re.DOTALL)
            if sql_match:
                return {"refined_sql": sql_match.group(1).strip()}
            
            # If no SQL code block, try to extract any SQL-like content
            sql_match = re.search(r'SELECT\s+.*?(?:;|$)', response, re.DOTALL | re.IGNORECASE)
            if sql_match:
                return {"refined_sql": sql_match.group(0).strip()}
            
            # Return the whole response as a fallback
            return {"refined_sql": response.strip()}
        else:
            # Use original method for other cases
            return super()._refine(query, evidence, schema_info, fk_info, error_info)
    
    def talk(self, message: dict):
        """Enhanced talk method with Spider dataset validation"""
        # Process the message with standard refiner
        super().talk(message)
        
        # Add spider-specific validation
        if self.dataset_name.lower() == 'spider' and 'pred' in message and 'ground_truth' in message:
            try:
                # Fix any formatting issues specific to Spider
                message['pred'] = self._fix_spider_column_names(message['pred'], message['db_id'])
                
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
                    message['execution_pred_data'] = pred_data[:10]  # Store only first 10 rows
                    message['execution_gold_data'] = gold_data[:10]  # Store only first 10 rows
                    
                    # If execution matching is successful, terminate the conversation
                    if execution_match:
                        message['send_to'] = SYSTEM_NAME
                
            except Exception as e:
                # If execution-based evaluation fails, just continue
                message['execution_error'] = str(e)


# Helper function to load Spider queries
def load_spider_subset(dataset_path, num_samples=5):
    """
    Load a subset of queries from the Spider dataset.
    
    Args:
        dataset_path: Path to the Spider dataset JSON file
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
        print(f"Error loading Spider dataset: {e}")
        return []
    
    # Ensure we have a list
    if not isinstance(data, list):
        print(f"Expected list, got {type(data)}")
        return []
    
    # Limit to num_samples
    if len(data) > num_samples:
        # Randomly sample to get a diverse set
        samples = random.sample(data, num_samples)
    else:
        samples = data
    
    # Format the samples for the agent
    formatted_samples = []
    for item in samples:
        formatted_item = {
            'db_id': item.get('db_id', ''),
            'question': item.get('question', ''),
            'SQL': item.get('query', ''),  # Spider uses 'query' instead of 'SQL'
            'evidence': '',  # Spider doesn't have evidence
            'difficulty': item.get('hardness', 'unknown')
        }
        formatted_samples.append(formatted_item)
    
    return formatted_samples


# Helper function to execute and compare queries
def execute_and_compare_queries(pred_sql, gold_sql, db_id, db_path=None):
    """
    Execute and compare the predicted and gold SQL queries.
    
    Args:
        pred_sql: Predicted SQL query
        gold_sql: Gold standard SQL query
        db_id: Database ID
        db_path: Path to the database directory
        
    Returns:
        Tuple of (execution_match, results_dict)
    """
    import sqlite3
    import os
    from pathlib import Path
    
    # Find the database file
    if db_path is None:
        # Try to find in standard locations
        possible_paths = [
            Path("MAC-SQL/data/spider/database"),
            Path("data/spider/database")
        ]
        
        for path in possible_paths:
            if path.exists():
                db_path = path
                break
    
    if db_path is None:
        return False, {"error": "Database path not found"}
    
    # Construct full path to the database file
    db_file = Path(db_path) / db_id / f"{db_id}.sqlite"
    
    if not db_file.exists():
        return False, {"error": f"Database file not found: {db_file}"}
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        
        # Execute predicted query
        try:
            cursor.execute(pred_sql)
            pred_result = cursor.fetchall()
        except Exception as e:
            return False, {"error": f"Error executing predicted SQL: {str(e)}"}
        
        # Execute gold query
        try:
            cursor.execute(gold_sql)
            gold_result = cursor.fetchall()
        except Exception as e:
            return False, {"error": f"Error executing gold SQL: {str(e)}"}
        
        # Compare results
        results_match = (pred_result == gold_result)
        
        return results_match, {
            "pred_result": pred_result[:10],  # First 10 rows
            "gold_result": gold_result[:10],  # First 10 rows
            "pred_count": len(pred_result),
            "gold_count": len(gold_result)
        }
        
    except Exception as e:
        return False, {"error": f"Unexpected error: {str(e)}"}
    
    finally:
        # Close the connection
        if 'conn' in locals():
            conn.close() 