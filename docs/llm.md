# Documentation for core/llm.py

This module serves as an alternative or fallback layer for interacting with Large Language Models (LLMs), primarily designed to use the OpenAI API if the main Together AI integration (`core/api.py`) is disabled or unavailable. It mirrors some of the functionality found in `core/api.py`, such as logging and safe API calls, but targets OpenAI's interface.

## Purpose

The main goal is to provide a consistent interface (`safe_call_llm`, `init_log_path`) for the rest of the application while allowing flexibility in the underlying LLM provider. It reads configuration from `core/api_config.py` to determine whether to delegate calls to `core.api` (for Together AI) or handle them using the OpenAI API.

## Configuration and Initialization

*   **Imports Configuration**: Imports settings like `USE_TOGETHER_AI`, `MODEL_NAME`, OpenAI credentials (implicitly used by the `openai` library) from `core.api_config`.
*   **Logging Setup**: Similar to `core/api.py`, it uses Python's `logging` and maintains global variables (`log_path`, `api_trace_json_path`, token counters) for logging API interactions.
*   **`init_log_path(my_log_path)`**: Identical purpose and function to the one in `core/api.py`. It initializes the paths for the text log file (`log_path`) and the JSON trace file (`api_trace_json_path`), creates the directory if needed, and resets token counters. This function *must* be called before logging to files will work.

## Key Functions

### 1. `api_func(prompt: str)`

*   **Purpose**: Selects and calls the appropriate LLM API based on the `USE_TOGETHER_AI` configuration flag.
*   **Functionality**:
    *   Checks `USE_TOGETHER_AI`. If `true`, it attempts to import `core.api` and calls `api.together_api_call(prompt)`. If the import fails, it logs a warning and proceeds to the OpenAI fallback.
    *   **OpenAI Fallback**: If `USE_TOGETHER_AI` is `false` or the Together API module import failed:
        *   Prints the OpenAI `MODEL_NAME` being used.
        *   Imports the `openai` library.
        *   Makes a call to `openai.ChatCompletion.create`. It handles a special case for local Llama models (setting API version to `None`, type to `open_ai`, key to `"EMPTY"`). For other models, it uses the configured engine name and temperature.
        *   Parses the response to extract the generated text, prompt tokens, and completion tokens.
        *   Returns the `text`, `prompt_token`, and `response_token`.
    *   Catches and logs errors during the OpenAI API call, then re-raises the exception.

### 2. `safe_call_llm(input_prompt, **kwargs) -> str`

*   **Purpose**: Provides a robust wrapper for calling the LLM (either Together AI via `core.api` or OpenAI via `api_func`) with retry logic and detailed logging. This is the main function intended for external use by agents.
*   **Functionality**:
    *   **Delegation Check**: First, checks `USE_TOGETHER_AI`. If `true`, it attempts to import `core.api` and directly calls and returns the result of `api.safe_call_llm(input_prompt, **kwargs)`. If the import fails, it logs a warning and proceeds with its own OpenAI implementation.
    *   **OpenAI Implementation**: If not using or unable to use the Together AI module:
        *   Uses a `for` loop (`MAX_TRY` = 5) for retries.
        *   Calls `api_func(input_prompt)` to get the response and token counts.
        *   **Logging**:
            *   If `log_path` is `None`, it prints a basic response and token count to the console.
            *   If `log_path` *is* set, it performs comprehensive logging similar to `core/api.py`:
                *   Appends the full prompt, response, and token counts to `log_path`.
                *   Constructs a `world_dict` containing the prompt, response, token counts, accumulated totals, and any additional `**kwargs` passed in.
                *   Appends this `world_dict` as a JSON string to the `api_trace_json_path` file.
                *   Tracks total prompt/response tokens globally.
        *   **Error Handling**: Catches exceptions during the `api_func` call, prints the error and retry attempt number, waits 20 seconds (`time.sleep(20)`), and continues the loop.
    *   **Failure**: If all `MAX_TRY` attempts fail, it raises a `ValueError`.
    *   **Return Value**: Returns the generated text response (`sys_response`) upon successful completion.

## Testing (`if __name__ == "__main__":`)

*   Includes a simple test that calls `safe_call_llm` with a basic question ("what is SQL?") and prints the result.

## Dependencies

*   `core.api_config`: Imports configuration constants.
*   `core.api` (Optional): Used for delegation if `USE_TOGETHER_AI` is true.
*   Standard libraries: `sys`, `json`, `time`, `os`, `logging`.
*   Third-party libraries: `openai` (required if `USE_TOGETHER_AI` is false or `core.api` import fails).
