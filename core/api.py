"""
Together AI API Functions for MAC-SQL
"""

import os
import json
import requests
import time
import logging
import random
from typing import Dict, Any, List, Tuple

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    print("Loading .env file from current directory...")
    load_dotenv()
    print("Loaded .env file successfully")
except ImportError:
    print("dotenv module not found, using environment variables as is")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
# Remove these global reads/prints - they happen too early
# TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo")

# Print environment variable values for debugging
# print(f"API Key (exists): {'Yes' if TOGETHER_API_KEY else 'No'}")
# print(f"API Key (length): {len(TOGETHER_API_KEY)} characters")
# print(f"Model: {TOGETHER_MODEL}")

# Initialize tracking variables for logging
total_prompt_tokens = 0
total_response_tokens = 0
log_path = None
api_trace_json_path = None

# Rate limiting parameters
MAX_RETRIES = 20  # Increased from 5 to 20 for more resilience
RETRY_DELAY = 5  # seconds
MAX_BACKOFF = 120  # Maximum delay in seconds (cap the exponential backoff)

def init_log_path(my_log_path):
    """Initialize log path for API call logging"""
    global log_path
    global api_trace_json_path
    global total_prompt_tokens
    global total_response_tokens
    
    log_path = my_log_path
    total_prompt_tokens = 0
    total_response_tokens = 0
    
    # Create log directory if needed
    if log_path:
        log_dir = os.path.dirname(log_path)
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up API trace log file
        api_trace_json_path = os.path.join(log_dir, 'api_trace.json')

def together_api_call(prompt: str) -> Tuple[str, int, int]:
    """
    Call Together AI API to generate a response
    
    Args:
        prompt: The prompt to send to the API
        
    Returns:
        Tuple of (response text, prompt tokens, completion tokens)
    """
    # Read API Key and Model directly from environment *inside* the function
    # This ensures it picks up changes from .env or arguments
    api_key = os.getenv("TOGETHER_API_KEY", "")
    default_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo" # Define default here
    model = os.getenv("TOGETHER_MODEL", default_model)
    
    # Check if API key is available
    if not api_key:
        raise ValueError("Together API key not found. Set TOGETHER_API_KEY environment variable.")
    
    # Log model being used
    logger.info(f"\nUsing Together AI model: {model}\n") # Log the currently resolved model
    
    # Prepare API request
    api_url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096
    }
    
    # Make API request with retry logic
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(api_url, headers=headers, json=data)
            
            # Check for rate limiting
            if response.status_code == 429:
                wait_time = min(RETRY_DELAY * (2 ** attempt), MAX_BACKOFF)  # Exponential backoff with cap
                logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry.")
                time.sleep(wait_time)
                continue
                
            # Check for other errors
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                raise Exception(f"API error: {response.status_code} - {response.text}")
            
            # Parse response
            result = response.json()
            
            # Extract text and token counts
            text = result["choices"][0]["message"]["content"].strip()
            prompt_tokens = result["usage"]["prompt_tokens"]
            completion_tokens = result["usage"]["completion_tokens"]
            
            return text, prompt_tokens, completion_tokens
            
        except Exception as e:
            logger.error(f"Error calling Together API: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise

def safe_call_llm(input_prompt: str, **kwargs) -> str:
    """
    Safe wrapper for LLM API call with logging
    
    Args:
        input_prompt: The prompt to send to the LLM
        **kwargs: Additional context for logging
        
    Returns:
        Generated response text
    """
    global total_prompt_tokens
    global total_response_tokens
    global log_path
    global api_trace_json_path
    global TOGETHER_MODEL
    
    # Try to make the API call with retries
    for attempt in range(MAX_RETRIES):
        try:
            # Make API call
            sys_response, prompt_token, response_token = together_api_call(input_prompt)
            
            # Track token usage for rate limiting
            total_prompt_tokens += prompt_token
            total_response_tokens += response_token
            
            # Log the results based on logging configuration
            if log_path is None:
                # Just print to console if no log path set
                print(f"\nResponse: \n{sys_response}")
                print(f"\nTokens (prompt/response): {prompt_token}/{response_token}\n")
            else:
                # Full logging to file
                with open(log_path, 'a+', encoding='utf8') as log_fp:
                    print('\n' + f'*'*20 +'\n', file=log_fp)
                    print(input_prompt, file=log_fp)
                    print('\n' + f'='*20 +'\n', file=log_fp)
                    print(sys_response, file=log_fp)
                    print(f'\nTokens (prompt/response): {prompt_token}/{response_token}\n', file=log_fp)
                
                # Also log to API trace JSON if available
                if api_trace_json_path:
                    # Get current model name (environment variable might have changed)
                    current_model = os.getenv("TOGETHER_MODEL", TOGETHER_MODEL)
                    
                    # Create trace entry with all context
                    trace_entry = {
                        "prompt": input_prompt.strip(),
                        "response": sys_response.strip(),
                        "prompt_tokens": prompt_token,
                        "response_tokens": response_token, 
                        "total_prompt_tokens": total_prompt_tokens,
                        "total_response_tokens": total_response_tokens,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "model": current_model
                    }
                    
                    # Add any additional context from kwargs
                    for k, v in kwargs.items():
                        trace_entry[k] = v
                    
                    # Write to trace file
                    with open(api_trace_json_path, 'a+', encoding='utf8') as trace_fp:
                        trace_fp.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
            
            # Return the response
            return sys_response
            
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            # Get current model for error message
            current_model = os.getenv("TOGETHER_MODEL", TOGETHER_MODEL)
            print(f"Request {current_model} failed. Try {attempt+1} of {MAX_RETRIES}. Sleeping {RETRY_DELAY} seconds.")
            time.sleep(RETRY_DELAY)
    
    # If all retries failed
    error_msg = f"Failed to call LLM API after {MAX_RETRIES} attempts"
    logger.error(error_msg)
    raise Exception(error_msg)

def call_llm(model_name: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Call the LLM with a structured message list.
    
    Args:
        model_name: The name of the model to use
        messages: List of message dictionaries with role and content
        
    Returns:
        Dictionary with response content
    """
    # Format the messages into a prompt for our current API implementation
    if not messages:
        return {"content": ""}
    
    # For now, we'll just use the last user message as the prompt
    # This is a simplification - a proper implementation would format all messages
    user_messages = [m for m in messages if m["role"] == "user"]
    if not user_messages:
        return {"content": ""}
    
    prompt = user_messages[-1]["content"]
    
    # Call the LLM
    response_text = safe_call_llm(prompt)
    
    # Return a structured response
    return {
        "content": response_text,
        "model": model_name
    }

if __name__ == "__main__":
    # Test the API
    response = safe_call_llm("Explain how a relational database works in one paragraph.")
    print(f"Test response: {response}") 