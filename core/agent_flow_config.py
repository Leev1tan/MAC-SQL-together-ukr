"""
Agent Flow Tracker Configuration

This module provides configuration options for the agent flow tracking system.
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentFlowConfig:
    """
    Configuration options for agent flow tracking.
    
    This class provides a centralized way to configure the behavior of the
    agent flow tracking system.
    """
    
    def __init__(self):
        """Initialize default configuration values."""
        # General tracking options
        self.enabled = True
        self.log_level = logging.INFO
        self.track_raw_messages = False  # Whether to store complete message contents
        
        # Display options
        self.display_format = "table"  # "table", "json", "mermaid"
        self.table_max_width = 120
        self.table_col_sql_length = 60
        self.show_sql_in_table = True
        
        # Visualization options
        self.visualization_format = "html"  # "html", "json", "mermaid"
        self.visualization_output_dir = "output"
        self.auto_visualize = False  # Whether to automatically generate visualizations
        
        # Storage options
        self.save_to_file = True
        self.output_file = "output/agent_flow.json"
        self.clear_on_start = True
        
        # Load from environment variables if present
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration values from environment variables."""
        # General tracking options
        if "AGENT_FLOW_ENABLED" in os.environ:
            self.enabled = os.environ["AGENT_FLOW_ENABLED"].lower() in ("true", "1", "yes")
        
        if "AGENT_FLOW_LOG_LEVEL" in os.environ:
            level = os.environ["AGENT_FLOW_LOG_LEVEL"].upper()
            if hasattr(logging, level):
                self.log_level = getattr(logging, level)
        
        if "AGENT_FLOW_TRACK_RAW" in os.environ:
            self.track_raw_messages = os.environ["AGENT_FLOW_TRACK_RAW"].lower() in ("true", "1", "yes")
        
        # Display options
        if "AGENT_FLOW_DISPLAY_FORMAT" in os.environ:
            self.display_format = os.environ["AGENT_FLOW_DISPLAY_FORMAT"].lower()
        
        if "AGENT_FLOW_TABLE_MAX_WIDTH" in os.environ:
            try:
                self.table_max_width = int(os.environ["AGENT_FLOW_TABLE_MAX_WIDTH"])
            except ValueError:
                pass
        
        if "AGENT_FLOW_TABLE_SQL_LENGTH" in os.environ:
            try:
                self.table_col_sql_length = int(os.environ["AGENT_FLOW_TABLE_SQL_LENGTH"])
            except ValueError:
                pass
        
        if "AGENT_FLOW_SHOW_SQL" in os.environ:
            self.show_sql_in_table = os.environ["AGENT_FLOW_SHOW_SQL"].lower() in ("true", "1", "yes")
        
        # Visualization options
        if "AGENT_FLOW_VIZ_FORMAT" in os.environ:
            self.visualization_format = os.environ["AGENT_FLOW_VIZ_FORMAT"].lower()
        
        if "AGENT_FLOW_VIZ_DIR" in os.environ:
            self.visualization_output_dir = os.environ["AGENT_FLOW_VIZ_DIR"]
        
        if "AGENT_FLOW_AUTO_VIZ" in os.environ:
            self.auto_visualize = os.environ["AGENT_FLOW_AUTO_VIZ"].lower() in ("true", "1", "yes")
        
        # Storage options
        if "AGENT_FLOW_SAVE_TO_FILE" in os.environ:
            self.save_to_file = os.environ["AGENT_FLOW_SAVE_TO_FILE"].lower() in ("true", "1", "yes")
        
        if "AGENT_FLOW_OUTPUT_FILE" in os.environ:
            self.output_file = os.environ["AGENT_FLOW_OUTPUT_FILE"]
        
        if "AGENT_FLOW_CLEAR_ON_START" in os.environ:
            self.clear_on_start = os.environ["AGENT_FLOW_CLEAR_ON_START"].lower() in ("true", "1", "yes")
    
    def update(self, **kwargs):
        """
        Update configuration values.
        
        Args:
            **kwargs: Configuration options to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration option: {key}")
    
    @property
    def visualization_output_path(self):
        """Get the full path for visualization output."""
        if not os.path.exists(self.visualization_output_dir):
            os.makedirs(self.visualization_output_dir, exist_ok=True)
        
        if self.visualization_format == "html":
            return os.path.join(self.visualization_output_dir, "agent_flow.html")
        elif self.visualization_format == "json":
            return os.path.join(self.visualization_output_dir, "agent_flow.json")
        elif self.visualization_format == "mermaid":
            return os.path.join(self.visualization_output_dir, "agent_flow.md")
        else:
            return os.path.join(self.visualization_output_dir, f"agent_flow.{self.visualization_format}")

# Create a global configuration instance
config = AgentFlowConfig() 