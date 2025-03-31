# Documentation for core/api.py

This module provides functions to interact with the Together AI Large Language Model (LLM) API. It handles constructing API requests, sending them, managing potential errors like rate limiting, and logging the interactions. It relies on configuration settings defined in `core/api_config.py` (implicitly, by reading environment variables potentially set by `api_config.py` or `.env`).

## Purpose

The primary goal is to offer a reliable way to send prompts to the configured Together AI model and receive generated text responses. It includes features like automatic retries with exponential backoff for transient errors (like rate limits) and detailed logging for debugging and tracking usage.

## Configuration and Initialization

*   **Environment Variables**: Reads `TOGETHER_API_KEY` and `TOGETHER_MODEL` from environment variables (potentially loaded from a `.env` file via `dotenv`). It prints checks for the key's existence and length, and the model name being used for debugging during startup.
*   **Logging Setup**: Uses Python's standard `logging` module. It defines global variables (`log_path`, `api_trace_json_path`) to store paths for log files.
*   **`init_log_path(my_log_path)`**: This function must be called externally to set up the logging paths. It initializes `log_path` (for detailed text logs) and `api_trace_json_path` (for structured JSON logs). It also resets token counters and creates the log directory if it doesn't exist.

## Key Functions

### 1. `together_api_call(prompt: str) -> Tuple[str, int, int]`

*   **Purpose**: Performs the direct HTTP POST request to the Together AI API endpoint (`https://api.together.xyz/v1/chat/completions`).
*   **Functionality**:
    *   Retrieves the API key and model name from the environment variables. Raises a `ValueError` if the API key is missing.
    *   Constructs the request payload including the model name, the user prompt (within a messages list), temperature (set to 0.1 for low randomness), and `max_tokens` (set to 4096).
    *   Sets the necessary `Authorization` (Bearer token) and `Content-Type` headers.
    *   Uses a `for` loop (`MAX_RETRIES` = 5) to handle retries.
    *   Sends the request using the `requests.post` method.
    *   **Error Handling**:
        *   Checks the HTTP status code. If it's `429` (Too Many Requests / Rate Limited), it logs a warning, waits for an exponentially increasing delay (`RETRY_DELAY * (2 ** attempt)`), and retries.
        *   If any other non-200 status code occurs, it logs an error and retries (unless it's the last attempt, then it raises an exception).
        *   Catches general exceptions during the request process, logs them, waits, and retries.
    *   **Response Parsing**: If the request is successful (status code 200), it parses the JSON response.
    *   **Return Value**: Returns a tuple containing:
        *   The generated text (`result["choices"][0]["message"]["content"]`).
        *   The number of tokens in the input prompt (`result["usage"]["prompt_tokens"]`).
        *   The number of tokens in the generated response (`result["usage"]["completion_tokens"]`).

### 2. `safe_call_llm(input_prompt: str, **kwargs) -> str`

*   **Purpose**: Acts as a robust wrapper around `together_api_call`. It incorporates the retry logic and handles detailed logging. This is likely the primary function intended to be called by other modules (like the agents in `core/agents.py`).
*   **Functionality**:
    *   Calls `together_api_call` within its own retry loop (`MAX_RETRIES`).
    *   **Token Tracking**: Accumulates the `prompt_token` and `response_token` counts returned by `together_api_call` into the global variables `total_prompt_tokens` and `total_response_tokens`.
    *   **Logging**:
        *   If `log_path` is not set (via `init_log_path`), it simply prints the response and token counts to the console.
        *   If `log_path` *is* set, it appends the full prompt, the response, and token counts to the file specified by `log_path`.
        *   If `api_trace_json_path` is *also* set, it creates a JSON object containing the prompt, response, token counts, total accumulated tokens, timestamp, model name, and any additional keyword arguments (`**kwargs`) passed to `safe_call_llm`. This JSON object is appended as a new line to the file specified by `api_trace_json_path`. This structured logging is useful for programmatic analysis.
    *   **Error Handling**: If `together_api_call` fails even after retries, `safe_call_llm` catches the exception, logs an error message indicating the failure after all attempts, waits (`RETRY_DELAY`), and continues the loop. If all attempts fail *within* `safe_call_llm`, it raises a final exception.
    *   **Return Value**: Returns the generated text response (`sys_response`) from the successful API call.

## Testing (`if __name__ == "__main__":`)

*   Contains a simple test case that calls `safe_call_llm` with a basic prompt ("Explain how a relational database works...") and prints the result. This allows the module to be run directly for a quick functionality check.

## Dependencies

*   Standard libraries: `os`, `json`, `time`, `logging`, `random`, `typing`
*   Third-party libraries: `requests`, `python-dotenv` (optional, for `.env` loading)
