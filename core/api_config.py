import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
try:
    load_dotenv()
except ImportError:
    print("dotenv module not found, using environment variables as is")

# Together AI configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo")
USE_TOGETHER_AI = os.getenv("USE_TOGETHER_AI", "true").lower() == "true"

# OpenAI configuration - Used as fallback if Together AI is not enabled
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "your_own_api_base")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_own_api_key")

# Import OpenAI library if needed
if not USE_TOGETHER_AI:
    try:
        import openai
        openai.api_type = "azure"
        openai.api_base = OPENAI_API_BASE
        openai.api_version = "2023-07-01-preview"
        openai.api_key = OPENAI_API_KEY
    except ImportError:
        print("OpenAI module not found. Will use alternative implementation.")

# Default model names
if USE_TOGETHER_AI:
    MODEL_NAME = TOGETHER_MODEL
else:
    MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4-1106-preview")

# Constants for engine names
ENGINE_OPENAI = "gpt-4-1106-preview"
ENGINE_TOGETHER = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# MODEL_NAME = 'gpt-4-1106-preview' # 128k 版本
# MODEL_NAME = 'CodeLlama-7b-hf'
# MODEL_NAME = 'gpt-4-32k' # 0613版本
# MODEL_NAME = 'gpt-4' # 0613版本
# MODEL_NAME = 'gpt-35-turbo-16k' # 0613版本