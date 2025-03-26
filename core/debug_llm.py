"""
Debug helper module for monitoring LLM API calls and agent communication
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMDebugger:
    """Debug and trace utility for LLM API calls"""
    
    def __init__(self, debug_mode: bool = False, log_dir: str = "logs/debug"):
        self.debug_mode = debug_mode
        self.log_dir = log_dir
        self.trace_history = []
        
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def enable_debug_mode(self, enable: bool = True):
        """Enable or disable debug mode"""
        self.debug_mode = enable
        logger.info(f"Debug mode {'enabled' if enable else 'disabled'}")
    
    def log_api_call(self, agent_name: str, prompt: str, response: str, metadata: Dict[str, Any] = None) -> None:
        """
        Log an API call to the LLM
        
        Args:
            agent_name: Name of the agent making the call
            prompt: Prompt sent to the LLM
            response: Response from the LLM
            metadata: Additional metadata about the call
        """
        if not self.debug_mode:
            return
        
        # Prepare log entry
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {}
        }
        
        # Add to trace history
        self.trace_history.append(log_entry)
        
        # Write to log file
        log_file = os.path.join(self.log_dir, f"llm_debug_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Also log to console in debug mode
        logger.debug(f"LLM Call: {agent_name}")
        logger.debug(f"Prompt: {prompt[:100]}...")
        logger.debug(f"Response: {response[:100]}...")
    
    def make_serializable(self, obj):
        """
        Make an object safely serializable for JSON.
        
        Args:
            obj: The object to make serializable
            
        Returns:
            A serializable version of the object
        """
        if obj is None:
            return None
        
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        
        if isinstance(obj, list):
            return [self.make_serializable(item) for item in obj]
        
        if isinstance(obj, dict):
            # Create a new dict with safe values
            result = {}
            for k, v in obj.items():
                # Skip fields starting with underscore (private)
                if isinstance(k, str) and k.startswith('_'):
                    continue
                
                # Skip trace fields which might cause circular references
                if k in ['exec_trace', 'trace_history', 'trace_enabled']:
                    continue
                
                try:
                    # Try to serialize the key/value
                    json.dumps({k: v})
                    result[k] = v
                except (TypeError, OverflowError, ValueError):
                    # If not serializable, convert or skip
                    if isinstance(v, dict):
                        result[k] = self.make_serializable(v)
                    else:
                        # Convert complex objects to string
                        try:
                            result[k] = str(v)[:100] + "..." if len(str(v)) > 100 else str(v)
                        except:
                            result[k] = f"<Unserializable: {type(v).__name__}>"
            
            return result
        
        # For other types, convert to string
        return str(obj)

    def log_agent_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]) -> None:
        """
        Log a message passed between agents
        
        Args:
            from_agent: Agent sending the message
            to_agent: Agent receiving the message
            message: The message content
        """
        if not self.debug_mode:
            return
        
        # Prepare log entry
        timestamp = datetime.now().isoformat()
        
        # Make message safely serializable
        safe_message = self.make_serializable(message)
        
        log_entry = {
            "timestamp": timestamp,
            "type": "agent_message",
            "from": from_agent,
            "to": to_agent,
            "message": safe_message
        }
        
        # Add to trace history - but use the safe version
        self.trace_history.append(log_entry)
        
        # Write to log file
        log_file = os.path.join(self.log_dir, f"agent_debug_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Log key fields to console
        logger.debug(f"Message: {from_agent} → {to_agent}")
        for key in ["desc_str", "fk_str", "pred", "final_sql"]:
            if key in message:
                value = message[key]
                if isinstance(value, str) and len(value) > 100:
                    logger.debug(f"  {key}: {value[:100]}...")
                else:
                    logger.debug(f"  {key}: {value}")
    
    def dump_trace(self, output_file: str = None) -> Dict[str, Any]:
        """
        Dump the trace history to a file and return it
        
        Args:
            output_file: File to write the trace to
            
        Returns:
            Full trace history
        """
        if not self.trace_history:
            return {"status": "empty", "trace": []}
        
        trace = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "trace": self.trace_history
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(trace, f, indent=2)
        
        return trace


# Global debugger instance
debugger = LLMDebugger(debug_mode=os.getenv("DEBUG_LLM", "false").lower() == "true")

def configure_from_env():
    """Configure debugging from environment variables"""
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
    debug_llm = os.getenv("DEBUG_LLM", "false").lower() == "true"
    
    if debug_mode or debug_llm:
        debugger.enable_debug_mode(True)
        logger.setLevel(logging.DEBUG)
        
        # Set up console handler for debug logs
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        logger.debug("Debug mode enabled from environment variables")
    
    return debug_mode or debug_llm

def patch_llm_functions():
    """
    Patch the LLM functions to add debugging
    """
    try:
        from core import llm
        original_safe_call_llm = llm.safe_call_llm
        
        def patched_safe_call_llm(prompt, **kwargs):
            """Patched version of safe_call_llm that logs calls"""
            agent_name = "unknown"
            # Try to extract agent name from call stack or context
            if 'context' in kwargs:
                agent_name = kwargs.get('context', {}).get('agent', 'unknown')
            
            # Call original function
            response = original_safe_call_llm(prompt, **kwargs)
            
            # Log the call
            debugger.log_api_call(agent_name, prompt, response, kwargs)
            
            return response
        
        # Apply the patch
        llm.safe_call_llm = patched_safe_call_llm
        logger.info("Successfully patched safe_call_llm for debugging")
        
        return True
    except Exception as e:
        logger.error(f"Failed to patch LLM functions: {e}")
        return False

# Automatically configure from environment when module is imported
is_debug_enabled = configure_from_env() 