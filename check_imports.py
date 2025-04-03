#!/usr/bin/env python
"""
Verify that the BIRD-UKR extensions can be imported properly.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path if needed
parent_dir = os.path.dirname(os.path.abspath(__file__))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    logger.info(f"Added {parent_dir} to sys.path")

def test_imports():
    """Test importing all our custom modules."""
    
    modules_to_test = [
        "utils.pg_selector", 
        "utils.bird_ukr_loader", 
        "utils.pg_connection",
        "utils.bird_ukr_tables_adapter",
        "core.bird_ukr_extensions",
        "core.enhanced_chat_manager"
    ]
    
    logger.info("Testing imports...")
    
    for module_name in modules_to_test:
        try:
            logger.info(f"Trying to import {module_name}...")
            module = __import__(module_name, fromlist=["*"])
            logger.info(f"✓ Successfully imported {module_name}")
            
            # For core.bird_ukr_extensions, check if load_bird_ukr_extensions exists
            if module_name == "core.bird_ukr_extensions":
                if hasattr(module, "load_bird_ukr_extensions"):
                    logger.info("✓ Found load_bird_ukr_extensions function")
                else:
                    logger.error("✗ load_bird_ukr_extensions function not found")
                    
        except ImportError as e:
            logger.error(f"✗ Failed to import {module_name}: {e}")
    
    # Check specific imports for enhanced_chat_manager
    try:
        from core.enhanced_chat_manager import EnhancedChatManager
        logger.info("✓ Successfully imported EnhancedChatManager")
        
        # Check if bird_ukr_extensions is imported
        import core.enhanced_chat_manager as ecm
        source_code = open(ecm.__file__, 'r').read()
        if "from core.bird_ukr_extensions import" in source_code:
            logger.info("✓ EnhancedChatManager imports bird_ukr_extensions")
        else:
            logger.warning("? EnhancedChatManager doesn't seem to import bird_ukr_extensions")
            
    except ImportError as e:
        logger.error(f"✗ Failed to import EnhancedChatManager: {e}")

if __name__ == "__main__":
    test_imports() 