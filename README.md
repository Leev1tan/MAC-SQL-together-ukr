# MAC-SQL with Together AI

This repository contains an implementation of MAC-SQL (Multi-Agent Collaboration for SQL) using Together AI's API for text-to-SQL generation.

## Overview

MAC-SQL represents a significant advancement in text-to-SQL generation through its innovative multi-agent collaboration framework. The system consists of three specialized intelligent agents working together to tackle different aspects of the text-to-SQL challenge:

1. **Selector Agent**: Analyzes and prunes database schemas to focus only on relevant tables and columns.

2. **Decomposer Agent**: Breaks down complex queries into manageable sub-queries using Chain-of-Thought (CoT) reasoning.

3. **Refiner Agent**: Validates generated SQL by executing it against the actual database, analyzing error messages, and correcting mistakes.

This implementation integrates Together AI's powerful LLMs with the MAC-SQL framework to generate accurate SQL queries for both BIRD and Spider datasets.

## Features

- **Together AI Integration**: Uses Together AI's API to power the generation of SQL queries
- **Multi-Agent Architecture**: Leverages the three-agent architecture of MAC-SQL
- **Dataset Support**: Works with both BIRD and Spider datasets
- **Execution-based Evaluation**: Validates SQL queries by comparing execution results
- **Enhanced Schema Handling**: Special optimizations for different dataset formats

## Getting Started

### Prerequisites

- Python 3.8+
- Together AI API key
- BIRD and/or Spider datasets

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/MAC-SQL.git
   cd MAC-SQL
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Together AI API key:
   ```
   TOGETHER_API_KEY=your_together_api_key_here
   TOGETHER_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct
   ```

### Dataset Setup

#### BIRD Dataset

1. Download the BIRD dataset from [the official source](https://bird-bench.github.io/)
2. Extract it to `MAC-SQL/data/bird/`
3. Ensure the following files/directories exist:
   - `MAC-SQL/data/bird/MINIDEV/mini_dev_sqlite.json`
   - `MAC-SQL/data/bird/MINIDEV/dev_databases/`
   - `MAC-SQL/data/bird/MINIDEV/tables.json` (may need to be copied from `dev_tables.json`)

#### Spider Dataset

1. Download the Spider dataset from [the official source](https://yale-lily.github.io/spider)
2. Extract it to `MAC-SQL/data/spider/`
3. Ensure the following files/directories exist:
   - `MAC-SQL/data/spider/dev.json`
   - `MAC-SQL/data/spider/database/`
   - `MAC-SQL/data/spider/tables.json`

## Usage

### Testing with BIRD Dataset

You can run a test on the BIRD dataset using the following command:

```bash
python test_macsql_agent_bird.py --samples 5
```

For interactive testing with a single query:

```bash
python test_macsql_agent_bird.py --single
```

To compare the agent-based approach with the pipeline approach:

```bash
python test_macsql_agent_bird.py --compare
```

### Testing with Spider Dataset

Similarly, you can run tests on the Spider dataset:

```bash
python test_macsql_agent_spider.py --samples 5
```

For interactive testing with a single query:

```bash
python test_macsql_agent_spider.py --single
```

To compare approaches:

```bash
python test_macsql_agent_spider.py --compare
```

## Components

### Core Components

- `core/macsql_together_adapter.py`: Bridge between Together AI's API and MAC-SQL
- `core/enhanced_chat_manager.py`: Extended chat manager with support for multiple datasets
- `core/bird_extensions.py`: Enhanced agents for the BIRD dataset
- `core/spider_extensions.py`: Enhanced agents for the Spider dataset

### Test Scripts

- `test_macsql_agent_bird.py`: Test script for the BIRD dataset
- `test_macsql_agent_spider.py`: Test script for the Spider dataset

## Implementation Details

### Agent Architecture

The implementation uses three specialized agents:

1. **Selector Agent**: 
   - Loads and analyzes database schemas
   - Prunes irrelevant tables and columns
   - Produces a focused schema for the next agent

2. **Decomposer Agent**:
   - Receives the pruned schema and natural language query
   - Breaks down complex queries into logical steps
   - Generates intermediate SQL representations

3. **Refiner Agent**:
   - Validates the generated SQL
   - Executes it against the database
   - Corrects errors and optimizes the query

### Together AI Integration

The `TogetherAIAdapter` class provides:
- Configuration for Together AI API calls
- Specialized prompt formatting for different agents
- Error handling and retry logic

### Dataset-Specific Optimizations

- **BIRD**:
  - Enhanced schema loading for BIRD's specific format
  - Special handling for evidence text
  - Column name fixing for execution

- **Spider**:
  - Specialized format for Spider's schema
  - Table alias and column name fixing
  - Special error analysis for common Spider issues

## Benchmark Results

(Insert your benchmark results here after running tests)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The original MAC-SQL paper and implementation by (Authors)
- Together AI for providing the LLM API
- BIRD and Spider dataset creators 