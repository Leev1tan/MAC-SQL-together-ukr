# Implementation Plan for BIRD-UKR Evaluation

## Overview
This document outlines the implementation plan for adding support for the Ukrainian BIRD-UKR dataset evaluation to our existing framework. 

## Core Requirements
1. Support PostgreSQL database connections and SQL query execution
2. Handle Ukrainian language in questions and SQL (UTF-8 encoding)
3. Load BIRD-UKR dataset format (questions and database schemas)
4. Evaluate both Execution Accuracy (EX) and Exact Match (EM) metrics

## Implementation Steps

### Step 1: PostgreSQL Support
- Add PostgreSQL connection functionality using psycopg2
- Create connection pooling and management for multiple databases
- Implement SQL query execution with proper error handling for PostgreSQL

### Step 2: BIRD-UKR Dataset Loader
- Create a function to load questions from BIRD-UKR JSON files
- Parse database schema from tables.json
- Support path resolution for Ukrainian database names

### Step 3: Evaluation Metrics
- Adapt execution accuracy (EX) calculation for PostgreSQL 
- Update SQL normalization for exact match (EM) considering PostgreSQL syntax
- Ensure proper handling of Unicode characters in queries

### Step 4: Agent Integration
- Update test_macsql_agent.py to support BIRD-UKR dataset
- Create test_macsql_agent_bird_ukr.py script
- Ensure database information is properly passed to the agent

### Step 5: Output and Visualization
- Ensure results are saved in consistent format
- Add Ukrainian-specific metadata to results
- Update summary reporting to handle Ukrainian database and query information

## Requirements

### Software Requirements
- psycopg2 (or psycopg2-binary) for PostgreSQL connections
- PostgreSQL server (version 12 or higher recommended)

### Database Setup
- Instructions for importing BIRD-UKR databases into PostgreSQL
- Configuration file for database connection parameters

## Files to Create

1. `test_macsql_agent_bird_ukr.py` - Main script for BIRD-UKR evaluation
2. `utils/pg_connection.py` - PostgreSQL connection utilities
3. `utils/bird_ukr_loader.py` - Dataset loading functions for BIRD-UKR

## Files to Modify

1. `evaluation/evaluate_metrics.py` - Add PostgreSQL support
2. `run_bird_evaluation.py` - Add BIRD-UKR option
3. `.env.sample` - Add PostgreSQL connection variables 