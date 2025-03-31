# Documentation for core/chat_manager.py

This module defines the `ChatManager` class, which orchestrates the interaction between different agents (`Selector`, `Decomposer`, `Refiner`) to process a user's natural language query into an SQL query. It manages the flow of information, handles initialization, and provides debugging capabilities.

## Purpose

The `ChatManager` acts as the central coordinator for the text-to-SQL pipeline. It takes a user query, passes it through the sequence of agents, ensures each agent performs its task, and manages the overall conversation flow, including error handling and termination conditions.

## Initialization (`__init__`)

*   **Parameters**: Takes paths for data (`data_path`), table definitions (`tables_json_path`), logging (`log_path`), the LLM `model_name`, the `dataset_name`, and flags for `lazy` loading (for the `Selector`), `without_selector` mode, and `debug_mode`.
*   **Network Check**: Calls `ping_network()` to ensure connectivity to the LLM API before proceeding.
*   **Agent Setup**: Instantiates the `Selector`, `Decomposer`, and `Refiner` agents, passing necessary configurations to each. Stores these agents in the `self.chat_group` list.
*   **Logging Initialization**: Calls the `INIT_LOG__PATH_FUNC` (imported from `core.api` or `core.llm`) to set up the logging file path provided during initialization.
*   **Debugger Check**: Checks if `core.debug_llm` is available and sets `HAS_DEBUGGER` flag accordingly.
*   **Execution Trace**: Initializes `self.execution_trace` as an empty list to store interaction details if enabled.

## Key Methods

### 1. `ping_network(self)`

*   **Purpose**: To verify that the application can successfully communicate with the configured LLM API.
*   **Functionality**: Makes a simple test call (`LLM_API_FUC("Hello world!")`) to the LLM. If it fails, it raises an exception indicating a network issue.

### 2. `_chat_single_round(self, message: dict)`

*   **Purpose**: Manages the processing of a message by a single agent within the `chat_group`.
*   **Functionality**:
    *   Iterates through the `chat_group`.
    *   Checks if the `message['send_to']` field matches the current `agent.name`.
    *   **Debugging/Tracing**:
        *   If `debug_mode` is true, prints debug information before and after the agent's `talk` method is called, showing who the message is going to, previews of schema/FK strings, and which fields changed.
        *   If `trace_enabled` is true in the message, records a detailed entry in `self.execution_trace` including the agent name, input message state, and output state (next agent, changed fields, and optionally LLM prompt/response if `HAS_DEBUGGER` is true).
        *   If `HAS_DEBUGGER` is true, uses `debugger.log_agent_message` to log the interaction.
    *   Calls the `agent.talk(message)` method, which modifies the `message` dictionary in place (updating `send_to`, adding results like `desc_str`, `final_sql`, etc.).

### 3. `start(self, user_message: dict)`

*   **Purpose**: The main entry point to begin processing a user query.
*   **Functionality**:
    *   Records the start time.
    *   Resets the `self.execution_trace`.
    *   Initializes the flow: Sets `user_message['send_to']` to `SELECTOR_NAME` if it's initially `SYSTEM_NAME`.
    *   Enters a loop that runs for a maximum of `MAX_ROUND` (defined in `core/const.py`, typically 3).
    *   Inside the loop:
        *   Calls `_chat_single_round(user_message)` to process the message with the appropriate agent.
        *   Checks if `user_message['send_to']` is now `SYSTEM_NAME`. If so, the process is complete (either successfully generated SQL or failed definitively), and the loop breaks.
    *   Records the end time and prints the total execution duration.

## Testing (`if __name__ == "__main__":`)

*   Includes a basic test case that:
    *   Instantiates `ChatManager` with sample paths and settings for the 'spider' dataset.
    *   Creates a sample `user_message` dictionary containing a DB ID, query, etc.
    *   Calls `test_manager.start(msg)` to run the pipeline.
    *   Prints the final state of the `msg` dictionary and the predicted SQL (`msg['pred']`).

## Dependencies

*   `core.agents`: Imports `Selector`, `Decomposer`, `Refiner`.
*   `core.const`: Imports constants like `MAX_ROUND`, agent names (`SELECTOR_NAME`, etc.), `SYSTEM_NAME`.
*   `core.api` / `core.llm`: Imports `safe_call_llm` and `init_log_path`.
*   `core.debug_llm` (Optional): Imports `debugger` if available.
*   Standard libraries: `time`, `pprint`.
