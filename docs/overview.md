# Overview of the /core Directory

This document provides a high-level overview of the components within the `/core` directory of the MAC-SQL project. The primary goal of this directory is to implement the core logic for converting natural language questions into executable SQL queries using a multi-agent Large Language Model (LLM) based approach.

## Core Concept: Multi-Agent Pipeline

The system operates using a pipeline of specialized agents, each responsible for a specific part of the text-to-SQL process. A central `ChatManager` orchestrates the flow of information between these agents. The standard flow is:

`User Input` -> `ChatManager` -> `Selector` -> `Decomposer` -> `Refiner` -> `ChatManager` -> `Final Output`

## Workflow Steps

1.  **Initialization:** The process starts when a `ChatManager` (or `EnhancedChatManager`) instance is created and its `start()` method is called with a user message containing the database ID (`db_id`), the natural language query (`query`), and optionally, evidence or ground truth SQL.
2.  **Configuration:** API settings are loaded from `core/api_config.py` (using environment variables or a `.env` file) to determine which LLM backend (Together AI or OpenAI) and model to use. Logging is initialized via functions in `core/api.py` or `core/llm.py`.
3.  **Selector Agent (`core/agents.py` or extensions):**
    *   Receives the initial message.
    *   Loads the relevant database schema information, potentially using `core/utils.py` and information from `tables.json` or directly from the SQLite database file.
    *   **(Optional Pruning):** If the schema is large and pruning is enabled, it may call the LLM (via `core/llm.py` or `core/api.py` using a template from `core/const.py`) to identify the most relevant tables and columns.
    *   Formats the potentially pruned schema (`desc_str`) and foreign key information (`fk_str`).
    *   Updates the message and forwards it to the `Decomposer`.
4.  **Decomposer Agent (`core/agents.py`):**
    *   Receives the message with the query and schema information.
    *   Constructs a prompt (using templates from `core/const.py`) instructing the LLM to generate the SQL query based on the provided context. For datasets like BIRD, it might use templates that encourage step-by-step decomposition.
    *   Calls the LLM (via `core/llm.py` or `core/api.py`).
    *   Parses the SQL query from the LLM's response (using `core/utils.py`).
    *   Adds the generated SQL (`final_sql` or `pred`) to the message and forwards it to the `Refiner`.
5.  **Refiner Agent (`core/agents.py` or extensions):**
    *   Receives the message with the generated SQL.
    *   Connects to the target SQLite database (using `sqlite3`, path constructed likely using `data_path` from config).
    *   Executes the SQL query. It includes error handling and a timeout (`func_timeout`).
    *   **(Optional Refinement):** If the execution fails (syntax error, runtime error) or returns potentially invalid results (e.g., empty set, `None` values depending on dataset), it constructs a new prompt (using templates from `core/const.py`) including the error details and asks the LLM (via `core/llm.py` or `core/api.py`) to fix the query. The process may loop back to execute the refined query.
    *   Once the query executes successfully (or refinement fails after max retries), it finalizes the predicted SQL (`pred`) in the message.
    *   Sets the message destination to `SYSTEM_NAME` to signal completion.
6.  **Completion:** The `ChatManager` receives the message flagged for `SYSTEM_NAME`, stops the loop, and the final message dictionary (containing the `pred` field with the SQL) is available.

## Key Modules in `/core`

*   **`api_config.py`**: Central configuration for LLM API keys, model names (Together AI, OpenAI), and base URLs. Reads from environment variables / `.env`.
*   **`api.py`**: Contains the specific implementation for interacting with the **Together AI API**, including the `together_api_call` function and a `safe_call_llm` wrapper with logging and retry logic.
*   **`llm.py`**: Provides a generic LLM interaction layer. It includes an `api_func` that delegates to `core.api.together_api_call` if `USE_TOGETHER_AI` is true, or falls back to using the `openai` library. It also has its own `safe_call_llm` which either delegates to `core.api.safe_call_llm` or uses its OpenAI implementation. Both `api.py` and `llm.py` share similar logging initialization (`init_log_path`).
*   **`const.py`**: Stores shared constants (like `MAX_ROUND`, agent names) and, crucially, the large multi-line **prompt templates** used by the agents when communicating with the LLM.
*   **`utils.py`**: A collection of helper functions for various tasks: parsing JSON/SQL, validating data (dates, emails), file I/O (loading/saving JSON, JSONL, TXT), interacting with SQLite schemas (`PRAGMA table_info`), extracting table/column info, and formatting schemas.
*   **`agents.py`**: Defines the `BaseAgent` abstract class and the core implementations of the `Selector`, `Decomposer`, and `Refiner` agents, forming the backbone of the pipeline.
*   **`chat_manager.py`**: Implements the `ChatManager` class that orchestrates the flow of messages between the agents defined in `agents.py`, manages the overall loop, and handles termination.

## Extensibility and Variations

*   **Dataset Extensions (`bird_extensions.py`, `spider_extensions.py`, `spider_extensions_fixed.py`):** These provide specialized `Selector` and `Refiner` agents inheriting from the base ones in `agents.py`. They contain logic tailored to the specific schemas, error patterns, or data characteristics of the BIRD and Spider datasets. Note that there appear to be two versions for Spider (`spider_extensions.py` and `spider_extensions_fixed.py`), suggesting one might be preferred or experimental.
*   **`enhanced_chat_manager.py`**: An alternative orchestrator that inherits from `ChatManager`. It can dynamically load and use the dataset-specific agents from the extension modules if they are available and requested.
*   **`macsql_together_adapter.py`**: Appears to be another layer for interacting with Together AI, focusing heavily on rate limiting. Its necessity might be limited if `core/api.py` handles this sufficiently.

## Supporting Modules

*   **Debugging (`debug_llm.py`, `debug_pretty.py`):** Optional utilities for logging detailed LLM interactions and visualizing agent communication flow during development. Not required for core functionality.
*   **Deprecated (`agent_flow*.py`, `legacy_agent_flow.py`):** Older, deprecated modules for tracking agent flow, likely superseded by newer mechanisms (potentially `core.tracking` and `core.visualization`, though these weren't reviewed). Should probably be removed.

This overview should provide a solid understanding of how the different pieces in the `/core` directory fit together to power the MAC-SQL text-to-SQL engine.
