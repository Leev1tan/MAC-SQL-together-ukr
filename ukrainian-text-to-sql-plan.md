# Ukrainian Text-to-SQL Dataset Creation Plan

## Overview

This document outlines our plan to create a Ukrainian version of a text-to-SQL dataset based on either Spider or BIRD. The dataset will use PostgreSQL as its database engine and will be placed in `MAC-SQL/data/[dataset]-ukr/` following the project's folder structure.

## Project Timeline

| Phase | Description | Estimated Duration |
|-------|-------------|-------------------|
| 1 | Database Selection & Setup | 1-2 weeks |
| 2 | Dataset Translation & Augmentation | 2-3 weeks |
| 3 | Technical Implementation | 2-3 weeks |
| 4 | Integration & Testing | 1-2 weeks |
| 5 | Expansion to Full Scale | 8-10 weeks |

Total estimated time: 14-20 weeks

## Phase 1: Database Selection & Setup

### 1.1 Choose Source Dataset

**Options:**
- **BIRD**: Contains more complex and realistic queries, already has PostgreSQL examples in `minidev_postgresql/`
- **Spider**: Simpler structure but would need complete PostgreSQL migration

**Decision criteria:**
- Ease of adaptation to Ukrainian context
- Availability of PostgreSQL schema
- Query complexity and diversity
- Size and scope of required translation effort

**Tasks:**
- [x] Review BIRD's `minidev_postgresql/` structure
- [x] Review Spider's database schemas
- [x] Compare dataset characteristics
- [x] Make final selection

### 1.2 Database Schema Conversion

**For Spider option:**
- [ ] Convert all SQLite schemas to PostgreSQL syntax
- [ ] Handle SQLite-specific datatypes and functions
- [ ] Adapt foreign key constraints and indexes

**For BIRD option:**
- [x] Review existing PostgreSQL schemas
- [x] Identify necessary modifications

**Common tasks:**
- [x] Ukrainianize table and column names while preserving original semantics
- [x] Document schema changes in both languages
- [x] Ensure UTF-8 encoding compatibility

### 1.3 Environment Setup

- [x] Set up PostgreSQL instance (version 12 or newer)
- [x] Configure for Ukrainian language support (UTF-8)
- [x] Prepare import/export tools
- [x] Create empty database with appropriate configuration
- [ ] Set up backup system

## Phase 2: Dataset Translation & Augmentation

### 2.1 Content Selection

- [x] Select 30-50 diverse queries for initial implementation
- [x] Ensure coverage of different SQL features:
  - Basic SELECT statements
  - JOINs (INNER, LEFT, RIGHT)
  - Aggregation functions (COUNT, SUM, AVG)
  - GROUP BY and HAVING clauses
  - Subqueries and nested queries
  - Window functions (if applicable)
- [x] Create a balanced mix of simple, moderate, and challenging queries

### 2.2 Translation Approach

- [x] Translate database table/column names to Ukrainian
- [x] Translate natural language questions to Ukrainian
- [x] Adapt entity names to Ukrainian context where appropriate
- [x] Preserve SQL query structure with PostgreSQL syntax
- [x] Create translation guidelines document
- [x] Set up glossary for consistent terminology

### 2.3 Artificial Data Generation

- [x] Create 10-15 additional Ukrainian-specific examples
- [x] Incorporate Ukrainian cultural references (cities, organizations, names)
- [x] Generate synthetic data that maintains statistical properties
- [x] Ensure valid data relationships across tables
- [x] Document artificial data generation process

## Phase 3: Technical Implementation

### 3.1 Schema Definition

- [x] Create PostgreSQL CREATE TABLE statements with Ukrainian comments
- [x] Define appropriate primary/foreign keys and constraints
- [x] Add appropriate indexes for query optimization
- [x] Implement UTF-8 encoding for Ukrainian characters
- [x] Document schema with diagrams and explanations

### 3.2 Data Population

- [x] Generate INSERT statements with Ukrainian content
- [x] Ensure valid data relationships
- [x] Create enough rows for meaningful query evaluation (minimum 100 rows per table)
- [x] Validate data integrity
- [x] Create data loading scripts

### 3.3 Query Definition

- [x] Create gold standard SQL queries (PostgreSQL syntax)
- [x] Pair with Ukrainian natural language questions
- [x] Validate each query executes correctly
- [x] Document expected query results
- [x] Classify queries by difficulty level

## Phase 4: Integration & Testing

### 4.1 MAC-SQL Integration

- [x] Create folder structure in MAC-SQL/data/[dataset]-ukr/
- [x] Develop loading scripts compatible with existing framework
- [ ] Extend evaluation scripts to support Ukrainian text
- [x] Add configuration options for PostgreSQL connection
- [x] Create dataset metadata files

### 4.2 Validation

- [x] Manually verify all Ukrainian-SQL pairs
- [x] Test execution of all queries
- [ ] Validate metrics calculations (EM, EX, VES)
- [x] Run integration tests with MAC-SQL framework
- [ ] Review error cases and edge conditions

### 4.3 Documentation

- [x] Document dataset structure and creation process
- [x] Provide usage examples
- [x] Create statistics about dataset composition
- [x] Write guide for extending the dataset
- [x] Prepare final report with dataset characteristics

## Phase 5: Expansion to Full Scale

### 5.1 Database Proliferation

- [x] Create expansion plan for multiple domains
- [ ] Develop 7+ new databases:
  - Medical System (Hospital)
  - Library
  - E-commerce Store
  - Restaurant
  - Travel Agency
  - Airline
  - Sports Club
- [ ] Design comprehensive schemas for each domain
- [ ] Create realistic table relationships

### 5.2 Data Generation

- [ ] Generate synthetic data for all domains (100+ records per table)
- [ ] Ensure statistical realism in generated data
- [ ] Add Ukrainian-specific content and context
- [ ] Validate data integrity across all databases

### 5.3 Query Expansion

- [ ] Create 150-200 diverse SQL queries across all domains
- [ ] Balance query complexity (30% simple, 40% medium, 30% complex)
- [ ] Include advanced SQL features (window functions, recursive queries)
- [ ] Pair all queries with natural language questions in Ukrainian

### 5.4 Integration & Documentation

- [ ] Integrate all databases with MAC-SQL
- [ ] Update documentation for full-scale dataset
- [ ] Provide comprehensive statistics on dataset composition
- [ ] Create benchmarks for model evaluation

## Dataset Structure

```
MAC-SQL/data/[dataset]-ukr/
├── README.md                   # Dataset documentation
├── database/                   # PostgreSQL database files
│   ├── [db_name]/              # Individual database directories
│   │   ├── schema.sql          # Database schema definition
│   │   └── data.sql            # Data population scripts
├── dev.json                    # Development set queries
├── tables.json                 # Table information
├── train.json                  # Training set queries (if applicable)
└── utils/                      # Utility scripts
    ├── load_data.py            # Data loading scripts
    └── postgresql_utils.py     # PostgreSQL-specific utilities
```

## Query Format Example

```json
{
  "db_id": "університет",
  "query": "SELECT с.назва, COUNT(к.ід) as кількість_курсів FROM студенти с JOIN курси к ON с.ід = к.студент_ід GROUP BY с.назва ORDER BY кількість_курсів DESC LIMIT 5",
  "question": "Покажи мені п'ять студентів, які записалися на найбільшу кількість курсів.",
  "question_en": "Show me the five students who have enrolled in the most courses.",
  "difficulty": "medium"
}
```

## Expansion Domains and Tables

### 1. Medical System (лікарня)

**Tables**:
- Doctors (лікарі)
- Patients (пацієнти)
- Diagnoses (діагнози)
- Departments (відділення)
- Prescriptions (призначення)
- Medications (ліки)
- Hospital Rooms (палати)
- Hospitalizations (госпіталізації)

### 2. Library (бібліотека)

**Tables**:
- Books (книги)
- Authors (автори)
- Genres (жанри)
- Readers (читачі)
- Loans (видачі)
- Fines (штрафи)
- Reviews (відгуки)

### 3. E-commerce (інтернет_магазин)

**Tables**:
- Products (товари)
- Categories (категорії)
- Customers (клієнти)
- Orders (замовлення)
- Order Details (деталі_замовлення)
- Discounts (знижки)
- Reviews (відгуки_товарів)
- Shipments (доставки)

### 4. Restaurant (ресторан)

**Tables**:
- Dishes (страви)
- Categories (категорії_страв)
- Orders (замовлення)
- Order Details (деталі_замовлення)
- Tables (столики)
- Staff (працівники)
- Reservations (резервації)
- Ingredients (інгредієнти)
- Recipes (рецепти)

### 5-7. Additional domains include Travel Agency, Airline, and Sports Club

## Implementation Timeline

| Stage | Description | Duration |
|-------|-------------|----------|
| 1 | Hospital & Library Implementation | 2 weeks |
| 2 | E-commerce & Restaurant Implementation | 2 weeks |
| 3 | Travel Agency & Airline Implementation | 2 weeks |
| 4 | Sports Club & University Extension | 2 weeks |
| 5 | Integration & Testing | 1 week |

## Evaluation Metrics

The Ukrainian dataset will support the same evaluation metrics as the original MAC-SQL:

1. **Exact Match Accuracy (EM)**: Compares SQL query structure clause-by-clause against the reference query (components must match but not values).

2. **Execution Accuracy (EX)**: The proportion of queries that produce identical execution results compared to ground truth.

3. **Valid Efficiency Score (VES)**: Measures query efficiency by comparing execution time of the model-generated queries against reference queries.

## Resources Required

1. **Technical Resources**:
   - PostgreSQL server (v12+)
   - MAC-SQL framework
   - Python environment for processing scripts
   - Data generation tools

2. **Human Resources**:
   - Ukrainian language expertise for translation
   - SQL/PostgreSQL developer for schema adaptation
   - Data engineer for data generation
   - Tester for validation

## Conclusion

This plan provides a comprehensive roadmap for creating a Ukrainian text-to-SQL dataset on PostgreSQL, first with a pilot implementation based on a university schema, then expanding to a full-scale dataset comparable to mini-BIRD or Spider. By following this structured approach, we will create a valuable resource for evaluating and improving text-to-SQL models for Ukrainian language applications. 