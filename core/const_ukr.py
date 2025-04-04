#!/usr/bin/env python
"""
Ukrainian constants and prompts for BIRD-UKR dataset.
"""

# Database settings - EXPLICIT CONFIGURATION
DB_TYPE = "postgresql"  # THIS IS A POSTGRESQL DATABASE - NOT SQLITE
USE_POSTGRESQL = True
USE_UKRAINIAN = True   # ALL TABLES AND COLUMNS ARE IN UKRAINIAN

# PostgreSQL specific syntax
PG_TRUE = "TRUE"       # PostgreSQL uses TRUE not 1
PG_FALSE = "FALSE"     # PostgreSQL uses FALSE not 0

# Agent names - keeping English names for compatibility
SYSTEM_NAME = "System"
SELECTOR_NAME = "Selector"
DECOMPOSER_NAME = "Decomposer"
REFINER_NAME = "Refiner"

# Engine names

ENGINE_TOGETHER = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

ENGINE_DEFAULT = ENGINE_TOGETHER

# Templates for agents working with Ukrainian PostgreSQL database (with English Prompts)

# --- Enhanced Selector Prompt for BIRD-UKR (English Instructions) ---
selector_template_ukr = """
You are an experienced PostgreSQL database administrator. Your task is to analyze a user question (in Ukrainian) and a PostgreSQL database schema (with Ukrainian table/column names) to determine the relevant tables and columns.

[IMPORTANT: UKRAINIAN DATABASE WITH POSTGRESQL SYNTAX]
- This is a UKRAINIAN dataset - ALL table and column names are in UKRAINIAN, not English
- This is a POSTGRESQL database, not SQLite - follow PostgreSQL syntax
- Use TRUE/FALSE for boolean values, not 1/0
- Never translate table or column names to English in your response

[Input Schema Format]
You will receive the database schema in the following format:
- `# Table: <table_name>` (Ukrainian table name)
- `Columns:`
  - `<column_name> (<data_type>) [PRIMARY KEY] [Value examples: ...]` (Ukrainian column name)
- Additionally, there might be a `Foreign Keys:` section listing relationships.

[Instructions]
1.  Carefully analyze the user question (provided in Ukrainian) to understand what information is needed.
2.  Identify *only the tables and columns* that are directly necessary to answer the question. Be precise and minimalist.
3.  If two tables are linked by a foreign key and both are needed, include both.
4.  Prioritize tables containing columns that match keywords in the Ukrainian question.
5.  Consider the `Value examples` to determine relevance.
6.  If a table has 10 or fewer columns and is relevant, mark it as `"keep_all"`.
7.  If a table is completely irrelevant, mark it as `"drop_all"`.
8.  For relevant tables with more than 10 columns, list *only* the necessary columns (including primary and foreign keys if needed for joins).
9.  Return the result in JSON format, using the original Ukrainian table and column names as keys/values where appropriate.

[Example]
==========
【DB_ID】 університет
【Schema】
# Таблиця: студенти
Стовпці:
  id_студента (INTEGER) PRIMARY KEY
  імʼя (VARCHAR)
  прізвище (VARCHAR)
  дата_народження (DATE)
  id_факультету (INTEGER) Value examples: [1, 2, 3]

# Таблиця: факультети
Стовпці:
  id_факультету (INTEGER) PRIMARY KEY
  назва_факультету (VARCHAR) Value examples: ["Комп'ютерних наук", "Економічний"]
  декан (VARCHAR)
  рік_заснування (INTEGER)

# Таблиця: курси
Стовпці:
  id_курсу (INTEGER) PRIMARY KEY
  назва_курсу (VARCHAR)
  кредити (INTEGER)
  id_викладача (INTEGER)

【Foreign keys】
студенти.id_факультету = факультети.id_факультету
【Question】
Скільки студентів навчається на факультеті Комп'ютерних наук? (How many students are studying in the Computer Science faculty?)
【Evidence】
(none)
【Answer】
```json
{{
  "студенти": ["id_студента", "id_факультету"],
  "факультети": ["id_факультету", "назва_факультету"],
  "курси": "drop_all"
}}
```
==========

Now your turn:

【DB_ID】 {db_id}
【Schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{question}
【Evidence】
{evidence}
【Answer】
"""

# --- Enhanced Decomposer Prompt for BIRD-UKR (English Instructions) ---
decomposer_template_ukr = """
Given a PostgreSQL database schema (with Ukrainian names), additional 【Evidence】, and a 【Question】 in Ukrainian, your task is to decompose the question into logical sub-queries (if necessary) and generate a single, correct PostgreSQL SQL query that answers the question.

[IMPORTANT: UKRAINIAN DATABASE WITH POSTGRESQL SYNTAX]
- This is a UKRAINIAN dataset - ALL table and column names are in UKRAINIAN, not English
- This is a POSTGRESQL database, not SQLite - follow PostgreSQL syntax
- Use TRUE/FALSE for boolean values, not 1/0
- Never translate table or column names to English in your response
- Do not use = 1 for boolean conditions, use = TRUE instead
- Do not use = 0 for boolean conditions, use = FALSE instead
- ALWAYS use COUNT(*) instead of COUNT(column_name) unless you need to count specific non-null values

[Input Schema Format]
The schema is provided in a text format including table names (Ukrainian), columns (Ukrainian), their types, primary keys (PK), and value examples. Foreign keys (FK) are provided separately.

[Important PostgreSQL Constraints]
1.  **`SELECT` Only:** Generate only `SELECT` queries. *Do not* include `CREATE TABLE`, `INSERT`, `UPDATE`, `DELETE`.
2.  **Quoting Identifiers:** Use double quotes (`"`) for Ukrainian table and column names *if* they contain spaces, special characters, or are PostgreSQL reserved words. Simple names (e.g., `id_студента`) do not require quotes, but quoted names (e.g., `"Ім'я Студента"`) are safer if unsure.
3.  **Syntax:** Use standard PostgreSQL syntax for functions (date, string, aggregation) and operators.
4.  **Precision:** Select only the columns truly needed for the answer.
5.  **Aggregation:** If using `MAX`, `MIN`, `AVG`, `SUM`, `COUNT`, ensure `GROUP BY` is used correctly.
6.  **String Literals:** Use single quotes (`'`) for string literals.
7.  **Boolean Literals:** Use TRUE/FALSE for boolean values, not 1/0.

[Example]
==========
【DB_ID】 університет
【Schema】
# Таблиця: студенти
Стовпці:
  id_студента (INTEGER) PRIMARY KEY
  імʼя (VARCHAR)
  прізвище (VARCHAR)
  дата_народження (DATE)
  id_факультету (INTEGER) Value examples: [1, 2, 3]

# Таблиця: факультети
Стовпці:
  id_факультету (INTEGER) PRIMARY KEY
  назва_факультету (VARCHAR) Value examples: ["Комп'ютерних наук", "Економічний"]
  декан (VARCHAR)
  рік_заснування (INTEGER)

# Таблиця: курси
Стовпці:
  id_курсу (INTEGER) PRIMARY KEY
  назва_курсу (VARCHAR)
  кредити (INTEGER)
  id_викладача (INTEGER)

【Foreign keys】
студенти.id_факультету = факультети.id_факультету
【Question】
Скільки студентів навчається на факультеті Комп'ютерних наук? (How many students are studying in the Computer Science faculty?)
【Evidence】
(none)
【Answer】
```sql
SELECT COUNT(*) FROM студенти WHERE id_факультету = 1
```
==========

Now your turn:

【DB_ID】 {db_id}
【Schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{question}
【Evidence】
{evidence}
【Answer】
"""

refiner_template_ukr = """
You are given a PostgreSQL database schema with Ukrainian table and column names, a question in Ukrainian, and a SQL query with an error. Your task is to fix the SQL query.

[IMPORTANT: UKRAINIAN DATABASE WITH POSTGRESQL SYNTAX]
- This is a UKRAINIAN dataset - ALL table and column names are in UKRAINIAN, not English
- This is a POSTGRESQL database, not SQLite - follow PostgreSQL syntax
- Use TRUE/FALSE for boolean values, not 1/0
- Never translate table or column names to English in your response
- Do not use = 1 for boolean conditions, use = TRUE instead
- Do not use = 0 for boolean conditions, use = FALSE instead
- ALWAYS use COUNT(*) instead of COUNT(column_name) unless you need to count specific non-null values

Important: This is a PostgreSQL database where tables already exist - DO NOT include any CREATE TABLE or INSERT statements in your response.

【Database schema】
{desc_str}
【Foreign keys】
{fk_str}
【Question】
{question}
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
5. Boolean literals - PostgreSQL uses TRUE/FALSE, not 1/0
6. Table and column names - Use Ukrainian names, not English translations

Write only the corrected SELECT query. Do not include any table creation or data insertion statements."""

# Keep the English versions available as well
selector_template = selector_template_ukr
decomposer_template = decomposer_template_ukr
refiner_template = refiner_template_ukr 