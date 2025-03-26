"""
Agent Message Tracker

This module provides functionality for tracking messages between agents
in a structured way.
"""

import json
import logging
import uuid
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import copy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration class for tracker settings
class Config:
    """Configuration for message tracker"""
    
    def __init__(self):
        self.enabled = True
        self.auto_visualize = False
        self.clear_on_start = True
        self.display_format = "mermaid"  # html, mermaid, json
        self.track_raw_messages = True  # Track full message content

class MessageTracker:
    """
    Tracks messages between agents
    
    This class provides functionality to track and store messages
    exchanged between agents in a multi-agent system.
    """
    
    def __init__(self):
        self.messages = []
        self.config = Config()
        self.session_id = None
        self.start_time = None
    
    def start_session(self):
        """Start a new tracking session"""
        self.session_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        logger.info(f"Started new agent flow tracking session: {self.session_id}")
    
    def track_message(self, sender: str, recipient: str, 
                      message_data: Optional[Union[Dict[str, Any], str]] = None, 
                      message_type: str = "unknown"):
        """
        Track a message between agents
        
        Args:
            sender: Agent sending the message
            recipient: Agent receiving the message
            message_data: The message content (optional)
            message_type: Type of message (received, sent, initial, final)
            
        Returns:
            ID of the tracked message
        """
        if not self.config.enabled:
            return None
            
        # Generate a unique ID for this message
        message_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Create base message record
        message = {
            "id": message_id,
            "timestamp": timestamp,
            "sender": sender,
            "recipient": recipient,
            "type": message_type
        }
        
        # Add message data if provided and tracking is enabled
        if message_data and self.config.track_raw_messages:
            try:
                # Import serialization utilities if available
                try:
                    from core.utils.serialization import safe_serialize_message
                    message["data"] = safe_serialize_message(message_data)
                except ImportError:
                    # Fall back to basic serialization
                    if isinstance(message_data, dict):
                        message["data"] = {k: v for k, v in message_data.items() 
                                         if k not in ["agent_instance", "trace_history"]}
                    else:
                        message["data"] = message_data
            except Exception as e:
                logger.warning(f"Failed to serialize message data: {str(e)}")
                message["data"] = str(message_data)
        
        # Store the message
        self.messages.append(message)

        # Log for debugging
        logger.debug(f"Tracked message: {sender} → {recipient} ({message_type})")
        
        return message_id
    
    def get_messages(self):
        """Get all tracked messages"""
        return self.messages
    
    def clear(self):
        """Clear all tracked messages"""
        self.messages = []
        logger.debug("Cleared all tracked messages")
        
    def to_json(self):
        """Convert tracked messages to JSON"""
        return json.dumps({
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "messages": self.messages
        })
    
    def save_to_file(self, filepath: str):
        """
        Save tracked messages to a file
        
        Args:
            filepath: Path to save the messages
        
        Returns:
            Path to the saved file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
            
        logger.info(f"Saved {len(self.messages)} messages to {filepath}")
        return filepath

# Create a global tracker instance
_TRACKER = None

def get_tracker():
    """
    Get the global tracker instance or initialize it if not exists
    
    Returns:
        The tracker instance
    """
    global _TRACKER
    if _TRACKER is None:
        _TRACKER = initialize_tracker()
    return _TRACKER

def initialize_tracker():
    """
    Initialize the message tracker with default configuration
    
    Returns:
        The initialized tracker instance
    """
    global _TRACKER
    
    # Create tracker if it doesn't exist
    if _TRACKER is None:
        _TRACKER = MessageTracker()
        
    # Start a new session if needed
    if _TRACKER.session_id is None:
        _TRACKER.start_session()
        
    return _TRACKER

def clear_flow():
    """Clear the current message flow"""
    tracker = get_tracker()
    if tracker:
        tracker.clear()
        logger.debug("Cleared message flow")

# Exports
__all__ = [
    'MessageTracker',
    'Config',
    'get_tracker',
    'initialize_tracker',
    'clear_flow'
] 