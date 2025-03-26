"""
Together AI Adapter for MAC-SQL

This module provides the adapter to connect MAC-SQL with Together AI API.
"""

import os
import json
import requests
import time
import random
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Rate limiting parameters
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 1  # seconds
MAX_RETRY_DELAY = 16  # seconds
RATE_LIMIT_CODES = [429, 500, 503]  # Common rate limit status codes

# Set default rate limits
DEFAULT_CALLS_PER_MINUTE = 45
DEFAULT_CALLS_PER_SECOND = 4

def configure_together_rate_limits(max_calls_per_minute: int = DEFAULT_CALLS_PER_MINUTE, 
                                   max_calls_per_second: int = DEFAULT_CALLS_PER_SECOND):
    """
    Configure rate limits for Together AI API calls.
    
    Args:
        max_calls_per_minute: Maximum calls per minute
        max_calls_per_second: Maximum calls per second
    """
    logger.info(f"Configured rate limits: {max_calls_per_minute} RPM, {max_calls_per_second} RPS")
    
    # Set environment variables for rate limits
    os.environ["TOGETHER_MAX_CALLS_PER_MINUTE"] = str(max_calls_per_minute)
    os.environ["TOGETHER_MAX_CALLS_PER_SECOND"] = str(max_calls_per_second)

def patch_api_func(model_name: Optional[str] = None):
    """
    Patch the API function to use Together AI.
    
    Args:
        model_name: Model name to use with Together AI
    """
    try:
        from core import llm
        from core.llm import api_func
        from core.api import together_api_call
        
        # Set model name
        if model_name:
            os.environ["TOGETHER_MODEL"] = model_name
        
        # Set the API function to use Together AI
        llm.api_func = together_api_call
        
        logger.info("Successfully patched api_func to use Together AI")
    except ImportError:
        logger.error("Failed to patch api_func - modules not found")

class TogetherAIAdapter:
    """
    Adapter to integrate Together AI API with MAC-SQL.
    """
    
    # Track API calls to manage rate limits
    _last_call_time = 0
    _calls_in_minute = 0
    _max_calls_per_minute = 45  # Reduced from 50 to be more conservative
    _min_call_interval = 1.0 / 3  # Reduced to max 3 calls per second
    _call_history = []  # Keep track of recent calls for better rate control
    
    @classmethod
    def set_api_integration(cls, model_name: Optional[str] = None, 
                            max_calls_per_minute: int = DEFAULT_CALLS_PER_MINUTE, 
                            max_calls_per_second: int = DEFAULT_CALLS_PER_SECOND):
        """
        Set up the integration with Together AI.
        
        Args:
            model_name: Model name to use with Together AI
            max_calls_per_minute: Maximum calls per minute
            max_calls_per_second: Maximum calls per second
        """
        # Configure rate limits
        configure_together_rate_limits(max_calls_per_minute, max_calls_per_second)
        
        # Patch API function
        patch_api_func(model_name)
    
    @classmethod
    def call_api_with_backoff(cls, api_func, *args, **kwargs):
        """
        Call API with exponential backoff retry logic for rate limiting.
        
        Args:
            api_func: Function to call the API
            *args: Arguments to pass to api_func
            **kwargs: Keyword arguments to pass to api_func
            
        Returns:
            API response
        """
        # Clean up old call history (older than 1 minute)
        current_time = time.time()
        cls._call_history = [t for t in cls._call_history if current_time - t < 60]
        
        # Count calls in last minute
        calls_in_last_minute = len(cls._call_history)
        
        # Enforce minimum time between calls
        time_since_last_call = current_time - cls._last_call_time
        
        if time_since_last_call < cls._min_call_interval:
            sleep_time = cls._min_call_interval - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        # Preventative rate limit handling - if we're getting close to the limit,
        # add additional delay proportional to how close we are to the limit
        if calls_in_last_minute > cls._max_calls_per_minute * 0.8:  # If we're at 80% of our limit
            # Calculate dynamic delay based on how close to the limit we are
            limit_proximity = calls_in_last_minute / cls._max_calls_per_minute
            dynamic_delay = limit_proximity * 2.0  # Up to 2 seconds at maximum proximity
            
            logger.warning(f"Approaching rate limit ({calls_in_last_minute}/{cls._max_calls_per_minute} RPM), adding delay of {dynamic_delay:.2f}s")
            time.sleep(dynamic_delay)
            
            # If we're very close to the limit (>95%), add extra jitter delay to spread out requests
            if limit_proximity > 0.95:
                extra_jitter = random.uniform(1.0, 3.0)
                logger.warning(f"Critical rate limit proximity, adding extra delay of {extra_jitter:.2f}s")
                time.sleep(extra_jitter)
        
        # Implement exponential backoff with jitter
        retry_delay = INITIAL_RETRY_DELAY
        
        for retry in range(MAX_RETRIES):
            try:
                # Track call for rate limiting
                cls._last_call_time = time.time()
                cls._call_history.append(cls._last_call_time)
                
                response = api_func(*args, **kwargs)
                
                # Check if the response contains a rate limit error
                if isinstance(response, dict) and response.get("error"):
                    error_msg = str(response.get("error", "")).lower()
                    raw_response = str(response.get("raw_response", "")).lower()
                    
                    if "429" in error_msg or "rate limit" in error_msg or "429" in raw_response:
                        if retry < MAX_RETRIES - 1:
                            # Apply exponential backoff with jitter
                            jitter = random.uniform(0, retry_delay * 0.3)  # Increased jitter
                            sleep_time = retry_delay + jitter
                            
                            logger.warning(f"Rate limit response received, retrying in {sleep_time:.2f}s (attempt {retry+1}/{MAX_RETRIES})")
                            time.sleep(sleep_time)
                            
                            # Double the delay for 429s with more aggressive backoff
                            retry_delay = min(retry_delay * 3, MAX_RETRY_DELAY)
                            
                            # Reset call history to be more conservative by keeping only recent calls
                            current_time = time.time()
                            cls._call_history = [t for t in cls._call_history if current_time - t < 20]  # Only keep last 20 seconds
                            
                            continue  # Skip to next retry
                
                # If we get here, the response was successful or a non-rate-limit error
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if retry < MAX_RETRIES - 1 and (any(str(code) in error_msg for code in RATE_LIMIT_CODES) or "rate limit" in error_msg or "429" in error_msg):
                    # Apply exponential backoff with jitter
                    jitter = random.uniform(0, retry_delay * 0.3)  # Increased jitter
                    sleep_time = retry_delay + jitter
                    
                    # If it's specifically a 429 error, add extra delay
                    if "429" in error_msg:
                        sleep_time *= 2.5  # More aggressive delay for 429s
                    
                    logger.warning(f"Rate limit hit, retrying in {sleep_time:.2f}s (attempt {retry+1}/{MAX_RETRIES})")
                    time.sleep(sleep_time)
                    
                    # Increase delay for next retry with more aggressive backoff
                    retry_delay = min(retry_delay * 3, MAX_RETRY_DELAY)
                    
                    # Also reset call history to be more conservative
                    if "429" in error_msg:
                        current_time = time.time()
                        cls._call_history = [t for t in cls._call_history if current_time - t < 20]  # Only keep last 20 seconds
                else:
                    # Not a rate limit error or out of retries
                    logger.error(f"API call failed after {retry+1} attempts: {e}")
                    
                    # For 429 errors that we've run out of retries for, return a structured error
                    if "429" in error_msg or "rate limit" in error_msg:
                        return {
                            "error": f"API error 429: Rate limit exceeded",
                            "raw_response": str(e),
                            "status": 429
                        }
                    
                    # For other errors
                    return {
                        "error": f"API error: {str(e)}",
                        "raw_response": str(e)
                    }
        
        # This should not be reached but just in case
        return {
            "error": f"API call failed after {MAX_RETRIES} attempts",
            "raw_response": "Multiple retries exhausted"
        }
    
    @staticmethod
    def format_messages_for_together(messages: List[Dict[str, str]]) -> str:
        """
        Format chat messages for Together AI API.
        
        Args:
            messages: List of message dictionaries with role and content
            
        Returns:
            Formatted prompt string
        """
        formatted_prompt = ""
        
        for message in messages:
            role = message.get("role", "").lower()
            content = message.get("content", "")
            
            if role == "system":
                # System message as initial context
                formatted_prompt += f"{content}\n\n"
            elif role == "user":
                # User messages
                formatted_prompt += f"Human: {content}\n\n"
            elif role == "assistant":
                # Assistant messages
                formatted_prompt += f"Assistant: {content}\n\n"
            else:
                # Other roles (ignore or handle as needed)
                pass
        
        # Add final assistant prompt
        formatted_prompt += "Assistant: "
        
        return formatted_prompt
    
    @staticmethod
    def format_agent_prompt(agent_type: str, content: str) -> List[Dict[str, str]]:
        """
        Format prompt for a specific agent type.
        
        Args:
            agent_type: Type of agent ("selector", "decomposer", "refiner")
            content: Content for the prompt
            
        Returns:
            List of message dictionaries
        """
        system_prompts = {
            "selector": """You are an expert database schema analyzer. Your task is to analyze a database schema and a natural language query to identify which tables and columns are relevant for answering the query. Focus only on the parts of the schema that would be needed to write a SQL query for the question.""",
            
            "decomposer": """You are an expert SQL developer with a specialty in breaking down complex queries into logical steps. Your task is to take a natural language question and a database schema, then generate a SQL query that answers the question correctly. Think step-by-step and explain your reasoning as you develop the query.""",
            
            "refiner": """You are an expert SQL query optimizer and debugger. Your task is to analyze and refine SQL queries to ensure they are correct, efficient, and properly answer the given question. If a query has execution errors, you should fix them. If the query executes but produces incorrect results, you should correct it."""
        }
        
        # Get the appropriate system prompt
        system_prompt = system_prompts.get(
            agent_type.lower(), 
            "You are an AI assistant helping with database queries."
        )
        
        # Create message list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
        
        return messages 