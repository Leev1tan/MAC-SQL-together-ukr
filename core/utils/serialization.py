"""
Serialization Utilities

This module provides utility functions for serializing complex data structures
to prevent circular references and make objects JSON-serializable.
"""

import logging
import json
import copy
from typing import Any, Dict, List, Union, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_serializable(obj: Any, 
                     visited: Optional[List[int]] = None, 
                     max_depth: int = 5,
                     current_depth: int = 0) -> Any:
    """
    Convert an object to a JSON serializable form, handling circular references
    
    Args:
        obj: The object to convert
        visited: List of object IDs already visited (to prevent circular references)
        max_depth: Maximum depth to traverse
        current_depth: Current traversal depth
        
    Returns:
        A JSON serializable version of the object
    """
    # Initialize visited set on first call
    if visited is None:
        visited = []
        
    # Check for max depth to prevent infinite recursion
    if current_depth > max_depth:
        return "[Max depth exceeded]"
        
    # Handle None
    if obj is None:
        return None
        
    # Handle basic types that are already serializable
    if isinstance(obj, (str, int, float, bool)):
        return obj
        
    # Check for circular references
    obj_id = id(obj)
    if obj_id in visited:
        return "[Circular reference]"
        
    # Add this object to visited set
    visited.append(obj_id)
    
    try:
        # Handle lists and tuples
        if isinstance(obj, (list, tuple)):
            return [make_serializable(item, visited, max_depth, current_depth + 1) 
                   for item in obj]
            
        # Handle dictionaries
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                # Skip known problematic keys
                if k in ["agent_instance", "trace_history", "_callback", "_parent"]:
                    continue
                    
                # Convert key to string if needed
                k_str = str(k) if not isinstance(k, (str, int, float, bool)) else k
                
                # Serialize the value
                result[k_str] = make_serializable(v, visited, max_depth, current_depth + 1)
                
            return result
            
        # Handle other objects by getting their __dict__ or string representation
        if hasattr(obj, "__dict__"):
            return make_serializable(obj.__dict__, visited, max_depth, current_depth + 1)
            
        # Try to convert to string if all else fails
        return str(obj)
        
    except Exception as e:
        logger.warning(f"Error serializing object: {str(e)}")
        return f"[Serialization error: {str(e)}]"
    finally:
        # Remove this object from visited set when done
        visited.remove(obj_id)
        
def safe_serialize_message(message: Any) -> Dict[str, Any]:
    """
    Safely serialize a message for tracking
    
    Args:
        message: The message to serialize
        
    Returns:
        A serializable version of the message
    """
    try:
        # Make a deep copy to avoid modifying the original
        message_copy = copy.deepcopy(message)
        
        # Convert to serializable form
        serialized = make_serializable(message_copy)
        
        # Return result, ensuring it's a dictionary
        if isinstance(serialized, dict):
            return serialized
        else:
            return {"data": serialized}
            
    except Exception as e:
        logger.warning(f"Failed to serialize message: {str(e)}")
        return {"error": f"Serialization failed: {str(e)}"}
        
def test_serialization():
    """Test the serialization functions with circular references"""
    # Create objects with circular references
    obj1 = {"name": "Object 1"}
    obj2 = {"name": "Object 2", "ref": obj1}
    obj1["ref"] = obj2
    
    # Try to serialize
    serialized = make_serializable(obj1)
    
    # Print result
    print(json.dumps(serialized, indent=2))
    return serialized

# Exports
__all__ = [
    'make_serializable',
    'safe_serialize_message'
] 