#!/usr/bin/env python
"""
Ukrainian constants and prompts for BIRD-UKR dataset.
"""

# Agent names - keeping English names for compatibility
SYSTEM_NAME = "System"
SELECTOR_NAME = "Selector"
DECOMPOSER_NAME = "Decomposer"
REFINER_NAME = "Refiner"

# Engine names

ENGINE_TOGETHER = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

ENGINE_DEFAULT = ENGINE_TOGETHER

# Templates for agents working with Ukrainian PostgreSQL database
selector_template_ukr = """
As an experienced database administrator, your task is to analyze a user question and a PostgreSQL database schema to provide relevant information. The database schema consists of tables in Ukrainian language, each containing multiple columns with sample values. Your goal is to identify the relevant tables and columns based on the user's question in Ukrainian.

Important: This is a PostgreSQL database with Ukrainian table and column names. All tables already exist. The schema includes sample values to help you understand the data.

【DB_ID】 {db_id}
【Schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{question}
【Evidence】
{evidence}

[Instructions]
1. Carefully analyze the user question to understand what information is being requested.
2. Identify only the most relevant tables needed to answer the question - be precise and minimal.
3. If two tables are connected by a foreign key and both are needed, include both.
4. Prioritize tables containing columns that match keywords in the question.
5. Consider sample values in columns to determine relevance.

[Requirements]
1. Select only the tables that are directly needed to answer the question.
2. If the question involves aggregation, ensure you include tables with relevant numeric columns.
3. If the question mentions specific entities (e.g., people, dates, locations), include tables with those entities.
4. If the question asks for a comparison, include tables with comparable attributes.
5. Use the foreign key information to understand relationships between tables.

Return your answer in a valid JSON format with these fields:
- selected_tables: An array of table names that are relevant
- explanation: Detailed explanation of why these tables were selected, including which columns are most relevant
"""

decomposer_template_ukr = """
Given a PostgreSQL 【Database schema】 with Ukrainian table and column names, and a 【Question】 in Ukrainian, you need to decompose the question into logical steps and generate a valid PostgreSQL query.

Important constraints:
- All tables already exist - DO NOT include any CREATE TABLE or INSERT statements
- ONLY write SELECT queries for data retrieval
- Use double quotes (") for Ukrainian identifiers when needed, not backticks (`)
- Use standard PostgreSQL functions and syntax for dates, strings, and aggregations
- When writing queries, be precise and only select the columns actually needed

【Database schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{query}
【Evidence】
{evidence}

Decompose the question into logical steps, considering the sample values in the schema to understand the data. Then generate a single SQL query that follows PostgreSQL syntax to answer the question."""

refiner_template_ukr = """
You are given a PostgreSQL database schema with Ukrainian table and column names, a question in Ukrainian, and a SQL query with an error. Your task is to fix the SQL query.

Important: This is a PostgreSQL database where tables already exist - DO NOT include any CREATE TABLE or INSERT statements in your response.

【Database schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{query}
【Evidence】
{evidence}

SQL query with error:
```sql
{sql}
```

PostgreSQL error message:
```
{sqlite_error}
```

Please analyze the error and provide a corrected SQL query that follows PostgreSQL syntax.

Common issues to check:
1. Identifier quoting - PostgreSQL uses double quotes for Ukrainian identifiers, not backticks
2. Character encoding - Ensure proper handling of Ukrainian characters in string literals
3. PostgreSQL-specific syntax for functions, operators, and aggregations
4. Case sensitivity - PostgreSQL identifiers are case-sensitive when quoted

Write only the corrected SELECT query. Do not include any table creation or data insertion statements."""

# Keep the English versions available as well
selector_template = selector_template_ukr
decomposer_template = decomposer_template_ukr
refiner_template = refiner_template_ukr 