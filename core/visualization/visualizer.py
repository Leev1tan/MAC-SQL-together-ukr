"""
Agent Communication Flow Visualizer

This module provides functions for visualizing agent communication flow
in various formats (text, HTML, Mermaid, JSON).
"""

import logging
import os
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import formatters - update imports to match new function names
from core.visualization.formatter import (
    format_simple_text,
    format_table_text,
    format_agent_flow_html,
    generate_mermaid,
    generate_json
)

def print_agent_flow(format_type: str = "simple") -> None:
    """
    Print a summary of the agent communication flow to console
    
    Args:
        format_type: Type of format to display ("simple", "table")
    """
    # Get message tracker
    from core.tracking.message_tracker import get_tracker
    tracker = get_tracker()
    
    if not tracker:
        logger.warning("No tracker available, nothing to display")
        return
        
    if not tracker.config.enabled:
        logger.warning("Agent flow tracking is disabled")
        return
        
    # Get messages
    messages = tracker.get_messages()
    
    if not messages:
        logger.warning("No messages to display")
        return
        
    logger.info(f"Displaying {len(messages)} messages in {format_type} format")
    
    # Format and print based on type
    if format_type == "table":
        formatted = format_table_text(messages)
    else:
        formatted = format_simple_text(messages)
        
    # Print to console
    print(formatted)

def visualize_agent_flow(format_type="html", output_path=None):
    """
    Visualize the agent flow from the message tracker
    
    Args:
        format_type: Format to use (html, json, mermaid)
        output_path: Path to save the visualization
        
    Returns:
        Path to the generated visualization file
    """
    # Import the message tracker
    from core.tracking.message_tracker import get_tracker
    
    # Get the message tracker
    tracker = get_tracker()
    
    # Get messages from the tracker
    messages = tracker.get_messages()
    
    # Log the visualization
    logger.info(f"Visualizing agent flow in {format_type} format")
    logger.info(f"Visualizing {len(messages)} messages")
    
    # Generate visualization based on format
    if format_type == "html":
        # Import the updated HTML formatter
        from core.visualization.formatter import format_agent_flow_html
        
        # Generate HTML visualization
        if not output_path:
            output_path = "output/agent_flow.html"
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        # Generate HTML visualization using the updated function
        result = format_agent_flow_html(messages, output_path=output_path)
        
        return result
        
    elif format_type == "json":
        from core.visualization.formatter import generate_json
        
        # Generate JSON visualization
        if not output_path:
            output_path = "output/agent_flow.json"
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        # Generate JSON visualization
        result = generate_json(messages, output_path)
        
        return result
        
    elif format_type == "mermaid":
        from core.visualization.formatter import generate_mermaid
        
        # Generate Mermaid visualization
        if not output_path:
            output_path = "output/agent_flow.mmd"
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        # Generate Mermaid visualization
        result = generate_mermaid(messages, output_path)
        
        return result
        
    else:
        logger.error(f"Unknown format type: {format_type}")
        return None

def visualize_agent_flow_wrapper(messages: List[Dict[str, Any]], 
                               format_type: str = "html", 
                               output_path: Optional[str] = None) -> Optional[str]:
    """
    Visualize a list of messages directly without using the tracker
    
    This is useful for generating visualizations from externally tracked messages
    or from a previously saved message log.
    
    Args:
        messages: List of message dictionaries
        format_type: Type of visualization to generate (html, json, mermaid)
        output_path: Path to save the visualization
        
    Returns:
        The path to the saved visualization
    """
    logger.info(f"Visualizing {len(messages)} messages in {format_type} format")
    
    # Generate visualization based on format
    if format_type == 'html':
        from core.visualization.formatter import format_agent_flow_html
        return format_agent_flow_html(messages, output_path=output_path)
    elif format_type == 'json':
        return generate_json(messages, output_path)
    elif format_type == 'mermaid':
        return generate_mermaid(messages, output_path)
    else:
        logger.warning(f"Unsupported visualization format: {format_type}")
        return None
    
# Exports
__all__ = [
    'print_agent_flow',
    'visualize_agent_flow',
    'visualize_agent_flow_wrapper'
] 