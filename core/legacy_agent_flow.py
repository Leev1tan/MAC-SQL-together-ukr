"""
LEGACY Agent Communication Flow

DEPRECATED: This module provides backward compatibility for agent flow tracking.
All new code should import from the new module structure instead:
- For tracking: import from core.tracking
- For visualization: import from core.visualization

This module will be removed in a future version.
"""

import logging
from typing import Dict, Any

# Import from new structure
from core.tracking import (
    MessageTracker,
    get_tracker,
    initialize_tracker,
    clear_flow,
    install_tracker,
    patch_agent_for_tracking
)

from core.visualization import (
    visualize_agent_flow,
    print_agent_flow
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Make sure we have a tracker instance for backward compatibility
tracker = get_tracker()

# Backward compatibility aliases
def track_agent_step(agent_name: str, action: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
    """
    Track a single agent communication step using the global tracker.
    
    This function is kept for backward compatibility.
    New code should use core.tracking.message_tracker directly.
    
    Args:
        agent_name: Name of the agent
        action: Action performed by the agent
        input_data: Input data for the agent
        output_data: Output data from the agent
    """
    # Get the tracker instance
    message_tracker = get_tracker()
    
    # Determine the source and destination
    from_agent = input_data.get('from', 'User')
    to_agent = output_data.get('send_to', 'System')
    
    # Track the message
    message_tracker.track_message(
        sender=from_agent,
        recipient=to_agent,
        message_data={**input_data, **output_data},
        message_type=action
    )
    
    logger.debug(f"Tracked agent step: {agent_name}")

# Backward compatibility for old function names
install_flow_tracker = install_tracker

# Export all for backward compatibility
__all__ = [
    'MessageTracker',
    'tracker',
    'get_tracker',
    'initialize_tracker',
    'clear_flow',
    'track_agent_step',
    'install_tracker',
    'install_flow_tracker',
    'print_agent_flow',
    'visualize_agent_flow'
] 