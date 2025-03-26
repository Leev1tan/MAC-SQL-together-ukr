"""
Agent Tracking Package

This package provides functionality for tracking agent communications
in multi-agent systems.
"""

# Import core tracking components
from core.tracking.message_tracker import (
    MessageTracker,
    get_tracker,
    initialize_tracker,
    clear_flow
)

# Import agent hooks
from core.tracking.hooks import (
    install_tracker,
    patch_agent_for_tracking
)

# Define public interface
__all__ = [
    'MessageTracker',
    'get_tracker',
    'initialize_tracker',
    'clear_flow',
    'install_tracker',
    'patch_agent_for_tracking'
] 