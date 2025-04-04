#!/usr/bin/env python
"""
PostgreSQL Selector for the BIRD-UKR dataset.
Optimized for Ukrainian database schema handling.
"""

import os
import logging
import json
from typing import Dict, List, Any, Tuple, Optional
import re

import psycopg2
from psycopg2.extras import RealDictCursor

# Import base Selector
from core.agents import Selector, BaseAgent
from core.const_ukr import selector_template_ukr, SELECTOR_NAME, DECOMPOSER_NAME
from core.utils import parse_json
from core.api import call_llm

logger = logging.getLogger(__name__)

class PostgreSQLSelector(BaseAgent):
    """
    Smart PostgreSQL Selector optimized for BIRD-UKR dataset.
    """
    
    def __init__(self, data_path: str, tables_json_path: str, 
                 model_name: str, dataset_name: str):
        """
        Initialize the PostgreSQL Selector.
        
        Args:
            data_path: Path to the dataset
            tables_json_path: Path to the tables.json file
            model_name: Name of the model to use
            dataset_name: Name of the dataset
        """
        super().__init__()
        self.name = SELECTOR_NAME
        self.data_path = data_path
        self.tables_json_path = tables_json_path
        self.model_name = model_name
        self.dataset_name = dataset_name
        
        # Get PostgreSQL credentials from environment
        self.pg_user = os.environ.get('PG_USER', 'postgres')
        self.pg_password = os.environ.get('PG_PASSWORD', '')
        self.pg_host = os.environ.get('PG_HOST', 'localhost')
        self.pg_port = os.environ.get('PG_PORT', '5432')
        
        # Cache for database schema information
        self.schema_cache = {}
        
        logger.info("Initialized PostgreSQL Selector")
        
    def talk(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message, analyze the query, and select relevant tables and columns.
        
        Args:
            message: The message to process
            
        Returns:
            The updated message with selected schema information
        """
        # Extract relevant information from the message
        db_id = message.get("db_id", "")
        
        # Support both 'query' and 'question' keys for flexibility
        query = message.get("query", "")
        if not query:
            query = message.get("question", "")
            # If query came from 'question', add it back as 'query' for consistency
            if query:
                message["query"] = query
                
        evidence = message.get("evidence", "")
        
        if not db_id or not query:
            logger.warning("Missing db_id or query in message")
            message["send_to"] = DECOMPOSER_NAME
            return message
        
        # Load database schema
        logger.info(f"Loading schema for {db_id}")
        schema_info = self.get_schema(db_id)
        
        if not schema_info or not schema_info.get("tables"):
            logger.warning(f"No schema information found for {db_id}")
            message["desc_str"] = f"Database {db_id} contains no tables."
            message["fk_str"] = ""
            message["send_to"] = DECOMPOSER_NAME
            return message
        
        # Format full schema descriptions
        desc_str, fk_str = self.format_schema(schema_info)
        
        # Now use the LLM to select relevant tables and columns based on the question
        selection_prompt = selector_template_ukr.format(
            question=query,
            db_id=db_id,
            desc_str=desc_str,
            fk_str=fk_str,
            evidence=evidence
        )
        
        # Call LLM to analyze the question and select relevant tables/columns
        selection_response = call_llm(
            model_name=self.model_name,
            messages=[
                {"role": "system", "content": "You are a database schema expert that helps identify relevant tables and columns needed to answer specific questions."},
                {"role": "user", "content": selection_prompt}
            ]
        )
        
        # Extract selected tables and columns from response
        selection_content = selection_response.get("content", "")
        
        try:
            # Look for JSON block in the response
            json_match = re.search(r'```json\s*(.*?)\s*```', selection_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                selection_data = json.loads(json_str)
            else:
                # Try to parse the entire content as JSON
                selection_data = parse_json(selection_content)
            
            # Create an annotated schema with selected tables and explanation
            selected_tables = selection_data.get("selected_tables", [])
            explanation = selection_data.get("explanation", "")
            
            # Filter schema to only include selected tables
            selected_schema = {"tables": {}, "foreign_keys": []}
            
            for table in selected_tables:
                if table in schema_info["tables"]:
                    selected_schema["tables"][table] = schema_info["tables"][table]
            
            # Include relevant foreign keys
            for fk in schema_info["foreign_keys"]:
                if (fk["source_table"] in selected_tables and 
                    fk["target_table"] in selected_tables):
                    selected_schema["foreign_keys"].append(fk)
            
            # Format selected schema
            selected_desc_str, selected_fk_str = self.format_schema(selected_schema)
            
            # Add selection info to the message
            message["desc_str"] = selected_desc_str
            message["fk_str"] = selected_fk_str
            message["selection_explanation"] = explanation
            
        except Exception as e:
            logger.warning(f"Error parsing selection response: {e}")
            # Fallback to full schema if parsing fails
            message["desc_str"] = desc_str
            message["fk_str"] = fk_str
        
        message["send_to"] = DECOMPOSER_NAME
        return message
    
    def get_schema(self, db_id: str) -> Dict[str, Any]:
        """
        Get schema information for a PostgreSQL database.
        
        Args:
            db_id: Database ID
            
        Returns:
            Dictionary with schema information
        """
        # Create a new connection to the database
        try:
            conn = psycopg2.connect(
                host=self.pg_host,
                port=self.pg_port,
                user=self.pg_user,
                password=self.pg_password,
                dbname=db_id
            )
            
            # Create cursor for executing queries
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = {"tables": {}}
            
            # Get columns for each table
            for table in tables:
                cursor.execute("""
                    SELECT column_name, data_type, 
                           is_nullable, column_default,
                           (SELECT EXISTS (
                               SELECT 1 FROM information_schema.table_constraints tc
                               INNER JOIN information_schema.constraint_column_usage ccu 
                               ON tc.constraint_name = ccu.constraint_name
                               WHERE tc.constraint_type = 'PRIMARY KEY' 
                               AND tc.table_name = c.table_name
                               AND ccu.column_name = c.column_name
                           )) as is_primary
                    FROM information_schema.columns c
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position;
                """, (table,))
                
                columns = []
                for col in cursor.fetchall():
                    column_name, data_type, is_nullable, default, is_primary = col
                    
                    # Get sample values for this column (up to 5)
                    try:
                        cursor.execute(f"""
                            SELECT "{column_name}" 
                            FROM "{table}" 
                            WHERE "{column_name}" IS NOT NULL 
                            LIMIT 5
                        """)
                        sample_values = [str(val[0]) for val in cursor.fetchall()]
                    except Exception as e:
                        # If error getting samples, provide empty list
                        sample_values = []
                    
                    columns.append({
                        "name": column_name,
                        "type": data_type,
                        "nullable": is_nullable == "YES",
                        "default": default,
                        "primary": is_primary,
                        "samples": sample_values
                    })
                
                schema_info["tables"][table] = columns
            
            # Get foreign keys
            cursor.execute("""
                SELECT
                    tc.table_name AS source_table, 
                    kcu.column_name AS source_column,
                    ccu.table_name AS target_table,
                    ccu.column_name AS target_column
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                  ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.column_name;
            """)
            
            foreign_keys = []
            for row in cursor.fetchall():
                source_table, source_column, target_table, target_column = row
                foreign_keys.append({
                    "source_table": source_table,
                    "source_column": source_column,
                    "target_table": target_table,
                    "target_column": target_column
                })
            
            schema_info["foreign_keys"] = foreign_keys
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Error getting schema for {db_id}: {e}")
            return {"tables": {}, "foreign_keys": []}
    
    def format_schema(self, schema_info: Dict[str, Any]) -> Tuple[str, str]:
        """
        Format schema information as a human-readable string.
        
        Args:
            schema_info: Dictionary with schema information
            
        Returns:
            Tuple of (desc_str, fk_str)
        """
        # Format tables and columns
        desc_parts = []
        
        for table_name, columns in schema_info["tables"].items():
            columns_str = []
            for col in columns:
                # Format type info with primary key if applicable
                type_info = col["type"]
                if col["primary"]:
                    type_info += " PRIMARY KEY"
                
                # Format sample values
                samples_str = ""
                if col["samples"]:
                    # Ensure samples are properly formatted for display
                    formatted_samples = []
                    for sample in col["samples"]:
                        # For string types, add quotes
                        if isinstance(sample, str) and not sample.isdigit():
                            formatted_samples.append(f"'{sample}'")
                        else:
                            formatted_samples.append(str(sample))
                    
                    samples_str = f". Value examples: [{', '.join(formatted_samples)}]"
                
                columns_str.append(f"({col['name']} {type_info}{samples_str})")
            
            # Format in a style similar to const.py
            desc_parts.append(f"# Table: {table_name}\n[")
            for i, col_str in enumerate(columns_str):
                if i < len(columns_str) - 1:
                    desc_parts.append(f"  {col_str},")
                else:
                    desc_parts.append(f"  {col_str}")
            desc_parts.append("]")
        
        desc_str = "\n".join(desc_parts)
        
        # Format foreign keys
        fk_parts = []
        for fk in schema_info["foreign_keys"]:
            fk_parts.append(
                f"{fk['source_table']}.{fk['source_column']} references "
                f"{fk['target_table']}.{fk['target_column']}"
            )
        
        fk_str = "\n".join(fk_parts)
        
        return desc_str, fk_str 