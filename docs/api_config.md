# Documentation for core/api_config.py

This module handles the configuration settings for connecting to Large Language Model (LLM) APIs, primarily focusing on Together AI and offering OpenAI as a fallback. It centralizes the management of API keys, model names, and API endpoints, reading values primarily from environment variables or a `.env` file.

## Purpose

The main goal of this file is to provide a single source of truth for API credentials and model choices used throughout the application, particularly by the agents defined in `core/agents.py` (via `core.api` or `core.llm`). It allows for easy switching between different LLM providers and models without modifying the core agent logic.

## Configuration Loading

*   **`.env` File**: It uses the `python-dotenv` library to load environment variables from a `.env` file located in the project root. This is useful for development environments to keep sensitive keys out of the code. If `dotenv` is not installed, it gracefully skips this step and relies solely on system environment variables.
*   **Environment Variables**: It reads specific environment variables (e.g., `TOGETHER_API_KEY`, `OPENAI_API_KEY`, `TOGETHER_MODEL`) to get the necessary configuration values. Default values are provided if the environment variables are not set.

## Key Configurations

### Together AI

*   `TOGETHER_API_KEY`: Stores the API key for accessing Together AI services. Loaded from the `TOGETHER_API_KEY` environment variable. Defaults to an empty string.
*   `TOGETHER_MODEL`: Specifies the default model to use with Together AI. Loaded from the `TOGETHER_MODEL` environment variable. Defaults to `meta-llama/Llama-3.3-70B-Instruct-Turbo`.
*   `USE_TOGETHER_AI`: A boolean flag (derived from the `USE_TOGETHER_AI` environment variable, defaulting to `"true"`) that determines whether to use the Together AI configuration. If `true`, Together AI settings are prioritized.

### OpenAI (Fallback)

These settings are used only if `USE_TOGETHER_AI` is set to `false`.

*   `OPENAI_API_BASE`: The base URL for the OpenAI API endpoint (useful for Azure OpenAI or custom deployments). Loaded from `OPENAI_API_BASE`. Defaults to `"your_own_api_base"`.
*   `OPENAI_API_KEY`: The API key for OpenAI services. Loaded from `OPENAI_API_KEY`. Defaults to `"your_own_api_key"`.
*   **OpenAI Library Import**: If `USE_TOGETHER_AI` is false, it attempts to import the `openai` library and configure it for use (specifically setting it up for Azure with a preview API version). If the library isn't found, it prints a message indicating an alternative implementation might be used elsewhere.

### Model Selection

*   `MODEL_NAME`: This variable holds the name of the LLM that the application will primarily use. Its value is determined by the `USE_TOGETHER_AI` flag:
    *   If `USE_TOGETHER_AI` is `true`, `MODEL_NAME` is set to `TOGETHER_MODEL`.
    *   If `USE_TOGETHER_AI` is `false`, `MODEL_NAME` is set to the value of the `OPENAI_MODEL` environment variable (defaulting to `"gpt-4-1106-preview"`).
*   `ENGINE_OPENAI`, `ENGINE_TOGETHER`: Constants holding default model names for OpenAI and Together AI respectively, potentially for reference or specific use cases elsewhere.
*   **Commented-out Models**: The file contains several commented-out lines assigning different model names (like `CodeLlama-7b-hf`, `gpt-4-32k`, `gpt-35-turbo-16k`) to `MODEL_NAME`. These likely represent models that were previously used or considered.

## Usage

Other modules (like `core.api` or `core.llm`) would import variables from this `api_config.py` module (e.g., `from core.api_config import MODEL_NAME, TOGETHER_API_KEY`) to configure their API calls.
