"""
Agent Flow Visualization (DEPRECATED)

This module provides visualization capabilities for the agent communication flow.
It is kept for backward compatibility, all new code should use core.visualization directly.

WARNING: This module will emit a deprecation warning when imported.
"""

import os
import json
import warnings
from typing import Dict, Any, List, Optional
import logging

# Emit deprecation warning
warnings.warn(
    "core.agent_flow_viz is deprecated and will be removed in a future version. "
    "Please use core.visualization directly.",
    DeprecationWarning, stacklevel=2
)

# Import from new structure
from core.tracking import get_tracker
from core.visualization import visualize_agent_flow as _visualize_agent_flow

# Get tracker instance for backward compatibility
tracker = get_tracker()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def visualize_agent_flow(format_type: str = "html", output_path: Optional[str] = None):
    """
    Generate visualization of agent communication flow.
    
    This is a compatibility wrapper around the new visualization module.
    New code should use core.visualization.visualize_agent_flow directly.
    
    Args:
        format_type: Type of visualization (html, mermaid, json)
        output_path: Path to save the visualization file
        
    Returns:
        Path to saved visualization file
    """
    return _visualize_agent_flow(format_type=format_type, output_path=output_path)

# Expose only the visualize_agent_flow function
__all__ = ['visualize_agent_flow'] 