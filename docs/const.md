# Documentation for core/const.py

This module centralizes constant values and multi-line string templates used across the MAC-SQL application, particularly by the agents (`Selector`, `Decomposer`, `Refiner`) and the `ChatManager`.

## Purpose

The main purpose is to avoid hardcoding values and large text blocks directly within the logic of other modules. This makes the codebase cleaner, easier to maintain, and allows for simpler modification of prompts or configuration values in one central location.

## Key Constants

*   **`MAX_ROUND`**: Defines the maximum number of times the `ChatManager` loop will iterate before terminating, acting as a safeguard against infinite loops (Default: 3).
*   **Engine Names**:
    *   `ENGINE_GPT4`, `ENGINE_GPT4_32K`: Constants holding specific OpenAI model names (likely historical or for reference).
    *   `ENGINE_TOGETHER`: Default model name for Together AI (`meta-llama/Llama-3.3-70B-Instruct-Turbo`).
*   **Agent Names**:
    *   `SELECTOR_NAME`: 'Selector'
    *   `DECOMPOSER_NAME`: 'Decomposer'
    *   `REFINER_NAME`: 'Refiner'
    *   `SYSTEM_NAME`: 'System' (Used to signal the end of the chat flow in `ChatManager`).

## Prompt Templates

These are multi-line f-strings used to construct the prompts sent to the LLM by different agents. They include placeholders (like `{db_id}`, `{query}`, `{desc_str}`) that are filled in dynamically at runtime.

*   **`selector_template`**:
    *   **Agent**: `Selector`
    *   **Purpose**: Instructs the LLM to act as a DBA, analyze a schema (`desc_str`, `fk_str`), user query (`query`), and evidence (`evidence`), and decide which tables/columns are relevant. It specifies output requirements (JSON format, keep/drop logic, column limits). Includes a detailed few-shot example.
*   **`decompose_template_bird`**:
    *   **Agent**: `Decomposer`
    *   **Purpose**: Specific template for the BIRD dataset. Instructs the LLM to decompose the `query` into sub-questions based on the schema (`desc_str`, `fk_str`) and `evidence`, generating SQL for each step. It emphasizes constraints for generating valid and efficient SQLite. Includes two detailed few-shot examples demonstrating the decomposition process.
*   **`decompose_template_spider`**:
    *   **Agent**: `Decomposer`
    *   **Purpose**: Similar to the BIRD template but designed for the Spider dataset. It omits the `evidence` placeholder as Spider typically doesn't use it. Instructs the LLM to decompose the `query` into sub-questions based on the schema (`desc_str`, `fk_str`) and generate SQL, following specific constraints. It does *not* include few-shot examples within this specific template string (unlike the BIRD one), suggesting a potentially zero-shot approach or that examples might be prepended dynamically.
*   **`oneshot_template_1` / `oneshot_template_2`**:
    *   **Agent**: Likely `Decomposer` (based on content).
    *   **Purpose**: Appear to be alternative few-shot templates for the decomposition task, similar to `decompose_template_bird`. They include slightly different example structures (one example per template). These might be used for experimentation or specific scenarios.
*   **`zeroshot_template`**:
    *   **Agent**: Likely `Decomposer`.
    *   **Purpose**: Provides instructions for generating SQL directly from the query, schema, and evidence *without* explicitly asking for step-by-step decomposition in the prompt structure itself (though the constraints still apply).
*   **`refiner_template`**:
    *   **Agent**: `Refiner`
    *   **Purpose**: Used when an SQL query executed by the `Refiner` results in an error. It provides the LLM with the original `query`, `evidence`, schema (`desc_str`, `fk_str`), the failed SQL (`sql`), and the specific error details (`sqlite_error`, `exception_class`). It instructs the LLM to fix the "old SQL" based on the error and provide the "correct SQL".
