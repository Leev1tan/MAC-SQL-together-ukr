"""
Agent Tracking Hooks

This module provides functions for hooking into agent methods
to track the message flow between agents.
"""

import logging
import copy
from functools import partial
from typing import Any, Callable, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import utilities
try:
    from core.utils.serialization import safe_serialize_message
except ImportError:
    # Fallback implementation if module not available
    def safe_serialize_message(message):
        """Simple fallback serialization"""
        if isinstance(message, dict):
            return {k: v for k, v in message.items() 
                   if k not in ["agent_instance", "trace_history"]}
        return message

# Keep track of the initial message ID to avoid circular references
initial_message_id = None

def hooked_chat_single_round(original_function: Callable, 
                            agent_name: str, 
                            agent_class: str,
                            agent_instance: Any, 
                            *args, **kwargs) -> Dict[str, Any]:
    """
    Wrapper that tracks messages going into and out of chat_single_round
    
    Args:
        original_function: The original function being wrapped
        agent_name: Name of the agent
        agent_class: Class name of the agent
        agent_instance: The agent instance
        args, kwargs: Arguments to the original function
        
    Returns:
        The result from the original function
    """
    # Get message tracker
    from core.tracking.message_tracker import get_tracker
    tracker = get_tracker()
    
    # Get the input message before it's modified
    input_message = args[0] if args else kwargs.get("message")
    
    if input_message is None:
        logger.warning(f"No input message found for {agent_name}")
    else:
        # Make a deep copy to avoid modifying the original
        try:
            input_message_copy = copy.deepcopy(input_message)
        except Exception as e:
            logger.warning(f"Failed to copy input message: {str(e)}")
            input_message_copy = {k: v for k, v in input_message.items() 
                                if k not in ["agent_instance", "trace_history"]}
        
        # Get sender from message or use "unknown"
        # Ensure sender is properly set
        sender = input_message_copy.get("from", "System")
        if sender == "unknown" or not sender:
            # Try to infer sender from previous step
            if "previous_agent" in input_message_copy:
                sender = input_message_copy["previous_agent"]
            # Add standard agent flow inference logic
            elif agent_name == "Selector":
                sender = "User"
            elif agent_name == "Decomposer":
                sender = "Selector"
            elif agent_name == "Refiner":
                sender = "Decomposer"
            
        # Ensure recipient is properly set
        input_message_copy["send_to"] = agent_name
        
        # Track the input message (received by this agent)
        if tracker.config.track_raw_messages:
            # Get safe serializable version of the message
            safe_message = safe_serialize_message(input_message_copy)
            
            # Add the data we need for proper visualization
            if "query" in safe_message and isinstance(safe_message["query"], dict):
                safe_message["question"] = safe_message["query"].get("question", "")
            elif "question" in safe_message:
                # Keep the question as is
                pass
            elif "query" in safe_message and isinstance(safe_message["query"], str):
                safe_message["question"] = safe_message["query"]
            
            # Explicitly add agent-specific metadata for visualization
            safe_message["agent_role"] = agent_name
            safe_message["previous_agent"] = sender
                
            # Track the message
            tracker.track_message(
                sender=sender,
                recipient=agent_name,
                message_data=safe_message,
                message_type="received"
            )
            logger.debug(f"Tracked incoming message: {sender} → {agent_name}")
    
    # Call the original function
    result = original_function(*args, **kwargs)
    
    # Track the outgoing message if we have one
    if result is not None:
        # Deep copy to avoid modifying the original
        try:
            result_copy = copy.deepcopy(result)
        except Exception as e:
            logger.warning(f"Failed to copy result: {str(e)}")
            result_copy = {k: v for k, v in result.items() 
                          if k not in ["agent_instance", "trace_history"]}
        
        # Set the sender in the outgoing message
        result_copy["from"] = agent_name
        result_copy["previous_agent"] = agent_name
        
        # Get the recipient from the message
        recipient = result_copy.get("send_to", "unknown")
        
        # If recipient is unknown, infer the next agent in the standard flow
        if recipient == "unknown" or not recipient:
            # Try to infer next agent based on standard flow
            if agent_name == "Selector":
                recipient = "Decomposer"
            elif agent_name == "Decomposer":
                recipient = "Refiner"
            elif agent_name == "Refiner":
                recipient = "System"
            elif agent_name == "System":
                recipient = "User"
            result_copy["send_to"] = recipient
        
        # Track the output message (sent by this agent)
        if tracker.config.track_raw_messages:
            # Get safe serializable version of the message
            safe_result = safe_serialize_message(result_copy)
            
            # Preserve important fields for visualization
            if "query" in input_message and isinstance(input_message["query"], dict):
                safe_result["question"] = input_message["query"].get("question", "")
            elif "question" in input_message:
                safe_result["question"] = input_message["question"]
                
            # Ensure schema information is preserved
            if "desc_str" in input_message:
                safe_result["desc_str"] = input_message["desc_str"]
            if "fk_str" in input_message:
                safe_result["fk_str"] = input_message["fk_str"]
            
            # Add explicit agent chain metadata
            safe_result["agent_role"] = agent_name
            safe_result["next_agent"] = recipient
            
            # Add a readable message_type for better visualization
            message_type = f"{agent_name.lower()}_to_{recipient.lower()}" 
            
            # Track the message
            tracker.track_message(
                sender=agent_name,
                recipient=recipient,
                message_data=safe_result,
                message_type=message_type
            )
            logger.debug(f"Tracked outgoing message: {agent_name} → {recipient}")
    
    return result

def hooked_start(original_function: Callable, 
                agent_name: str, 
                agent_class: str,
                agent_instance: Any, 
                *args, **kwargs) -> Dict[str, Any]:
    """
    Wrapper that tracks the start method of an agent
    
    Args:
        original_function: The original function being wrapped
        agent_name: Name of the agent
        agent_class: Class name of the agent
        agent_instance: The agent instance
        args, kwargs: Arguments to the original function
        
    Returns:
        The result from the original function
    """
    global initial_message_id
    
    # Get message tracker
    from core.tracking.message_tracker import get_tracker
    tracker = get_tracker()
    
    # Clear tracker if configured
    if tracker.config.clear_on_start:
        logger.debug(f"Clearing message tracker on start for {agent_name}")
        tracker.clear()
    
    # Get the input message if available
    input_message = args[0] if args else kwargs.get("message", {})
    
    if not isinstance(input_message, dict):
        input_message = {"query": str(input_message)}
    
    # Track the initial message
    if tracker.config.track_raw_messages:
        # Create a serializable version
        try:
            safe_message = safe_serialize_message(input_message)
        except Exception as e:
            logger.warning(f"Failed to serialize start message: {str(e)}")
            safe_message = {"query": str(input_message.get("query", ""))}
        
        # Add a reference to record this as initial message
        safe_message["is_initial"] = True
        safe_message["agent_flow_start"] = True
        
        # Add explicit agent metadata
        safe_message["first_agent"] = agent_name
        
        # Track as initial message
        initial_message_id = tracker.track_message(
            sender="User",
            recipient=agent_name,
            message_data=safe_message,
            message_type="initial"
        )
        logger.debug(f"Tracked initial message with ID: {initial_message_id}")
    
    # Call the original function
    result = original_function(*args, **kwargs)
    
    # Track the final result if available
    if result is not None and tracker.config.track_raw_messages:
        # Create a serializable version
        try:
            safe_result = safe_serialize_message(result)
        except Exception as e:
            logger.warning(f"Failed to serialize result: {str(e)}")
            safe_result = {"result": str(result)}
        
        # Add reference to initial message
        if initial_message_id:
            safe_result["initial_message_id"] = initial_message_id
            
        # Mark as final result
        safe_result["is_final"] = True
        safe_result["agent_flow_end"] = True
        
        # Add explicit agent metadata
        safe_result["last_agent"] = agent_name
        
        # Track as final message
        tracker.track_message(
            sender=agent_name,
            recipient="User",
            message_data=safe_result,
            message_type="final"
        )
        logger.debug(f"Tracked final result message: {agent_name} → User")
    
    return result

def install_tracking_hooks(chat_manager):
    """
    Install tracking hooks on a chat manager's agents
    
    Args:
        chat_manager: The chat manager to install hooks on
    """
    if not hasattr(chat_manager, 'chat_group') or not chat_manager.chat_group:
        logger.warning("Chat manager has no chat_group, cannot install hooks")
        return
    
    # Install hooks on each agent
    for agent in chat_manager.chat_group:
        if hasattr(agent, 'name'):
            agent_name = agent.name
            agent_class = agent.__class__.__name__
            patch_agent_for_tracking(agent, agent_name, agent_class)
            logger.info(f"Installed tracking hooks on agent: {agent_name} ({agent_class})")
        else:
            logger.warning(f"Agent {agent} has no name attribute")
    
    logger.info(f"Installed tracking hooks on {len(chat_manager.chat_group)} agents")

def patch_agent_for_tracking(agent: Any, agent_name: str, agent_class: str) -> None:
    """
    Patch methods of an agent instance to track their calls
    
    Args:
        agent: Agent instance
        agent_name: Name of the agent
        agent_class: Class of the agent
    """
    # Get message tracker
    from core.tracking.message_tracker import get_tracker
    tracker = get_tracker()
    
    logger.debug(f"Patching agent {agent_name} ({agent_class}) for tracking")
    
    # Only track if we have a valid tracker
    if not tracker:
        logger.warning("No tracker available, skipping agent patching")
        return
    
    # Patch the start method if it exists
    if hasattr(agent, 'start'):
        original_start = agent.start
        
        # Create a partial function with agent-specific details
        agent_start_wrapper = partial(
            hooked_start, 
            original_start, 
            agent_name, 
            agent_class,
            agent
        )
        
        # Replace the method
        agent.start = agent_start_wrapper
        logger.debug(f"Patched start method for {agent_name}")
    
    # Patch the chat_single_round method if it exists
    if hasattr(agent, '_chat_single_round'):
        original_chat = agent._chat_single_round
        
        # Create a partial function with agent-specific details
        agent_chat_wrapper = partial(
            hooked_chat_single_round, 
            original_chat, 
            agent_name, 
            agent_class,
            agent
        )
        
        # Replace the method
        agent._chat_single_round = agent_chat_wrapper
        logger.debug(f"Patched _chat_single_round method for {agent_name}")
        
    # Patch the talk method if it exists (sometimes used instead of _chat_single_round)
    if hasattr(agent, 'talk') and agent.talk.__name__ != 'agent_chat_wrapper':
        original_talk = agent.talk
        
        # Create a partial function with agent-specific details
        agent_talk_wrapper = partial(
            hooked_chat_single_round, 
            original_talk, 
            agent_name, 
            agent_class,
            agent
        )
        
        # Replace the method
        agent.talk = agent_talk_wrapper
        logger.debug(f"Patched talk method for {agent_name}")

# Exports
__all__ = [
    'patch_agent_for_tracking',
    'install_tracking_hooks',
    'hooked_chat_single_round',
    'hooked_start'
] 