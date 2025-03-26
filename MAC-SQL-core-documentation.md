# MAC-SQL Core Code Documentation

## Overview

The `core/` directory contains the main implementation of the Multi-Agent Collaborative Text-to-SQL framework. This framework consists of three specialized agents (Selector, Decomposer, and Refiner) that collaborate to translate natural language questions into SQL queries.

## Key Components

### 1. `api_config.py`
Configuration file for API integration:
- Supports both Together AI and OpenAI models
- Loads configuration from .env file using dotenv
- Defines the model name to be used (e.g., Meta-Llama-3.1-70B-Instruct or GPT-4)
- Handles environment variables and API configuration

### 2. `llm.py`
Manages interactions with the language model API:
- `init_log_path()`: Initializes logging for API calls
- `api_func()`: Core function for making API calls to either Together AI or OpenAI
- `safe_call_llm()`: Wrapper that handles retries, logging, and token tracking
- Tracks token usage and handles errors with automatic retries

### 3. `chat_manager.py`
Orchestrates the communication between agents:
- `ChatManager` class: Central controller for agent communication
- `__init__()`: Initializes agents and sets up the environment
- `ping_network()`: Verifies API connectivity 
- `_chat_single_round()`: Manages a single round of communication
- `start()`: Begins the agent conversation flow
- Handles message routing between agents

### 4. `agents.py`
Implements the three specialized agents:

#### BaseAgent (Abstract Base Class)
- Provides the foundation for all agent types
- Defines the required `talk()` interface method

#### Selector Agent
- Purpose: Analyzes database schema and selects relevant tables/columns
- Key methods:
  - `init_db2jsons()`: Parses database schema information
  - `_get_column_attributes()`: Extracts column metadata
  - `_get_unique_column_values_str()`: Gets sample values for columns
  - `_load_single_db_info()`: Processes database structure
  - `_get_db_desc_str()`: Generates database description
  - `_prune()`: Filters schema to relevant parts
  - `talk()`: Entry point for receiving messages

#### Decomposer Agent
- Purpose: Breaks down complex questions and solves them using Chain-of-Thought
- Key methods:
  - `talk()`: Processes messages and generates an initial SQL query

#### Refiner Agent
- Purpose: Executes and validates SQL queries, refining as needed
- Key methods:
  - `_execute_sql()`: Runs SQL against database
  - `_is_need_refine()`: Checks if query needs improvement
  - `_refine()`: Improves SQL based on execution results
  - `talk()`: Handles message processing and refinement

### 5. `const.py`
Contains constant values and prompt templates:
- Agent names and descriptions
- Maximum conversation rounds
- Detailed prompt templates for each agent
- SQL validation rules

### 6. `utils.py`
Provides utility functions:
- JSON parsing and handling
- SQL string manipulation
- Database information extraction
- Date validation and formatting

## Communication Flow

1. The `ChatManager` initializes all three agents
2. User query enters the system through the `start()` method
3. The `Selector` analyzes the database and selects relevant schema
4. The `Decomposer` breaks down the question and generates an initial SQL query
5. The `Refiner` executes and validates the SQL, making refinements if needed
6. The final SQL result is returned to the user

## Design Philosophy

The framework leverages a multi-agent approach to handle Text-to-SQL translation by:
1. Dividing the complex task into specialized subtasks
2. Using Chain-of-Thought reasoning for complex query understanding
3. Employing a refinement process that includes execution validation
4. Supporting schema pruning for handling large database schemas

This modular design allows each agent to focus on its specific task while collaborating to produce accurate SQL translations.

## Together AI Integration

MAC-SQL now supports Together AI's large language models as an alternative to OpenAI models:

### Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your Together AI API key:
   ```
   TOGETHER_API_KEY=your_api_key_here
   TOGETHER_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
   USE_TOGETHER_AI=true
   ```

3. Alternatively, run the setup script for a guided setup:
   ```
   python setup_together.py
   ```

### Supported Models

Several Together AI models are supported, including:
- Meta-Llama-3.3-70B-Instruct (recommended)
- Meta-Llama-3.1-8B-Instruct
- Mixtral-8x7B-Instruct-v0.1

### Configuration Options

In the `.env` file:
- `TOGETHER_API_KEY`: Your Together AI API key
- `TOGETHER_MODEL`: The model identifier 
- `USE_TOGETHER_AI`: Set to "true" to use Together AI (or "false" to use OpenAI) 