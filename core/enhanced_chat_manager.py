"""
Enhanced Chat Manager for MAC-SQL with Together AI

This module provides an extended ChatManager that works with both BIRD and Spider datasets.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Check if we can import core components
try:
    from core.agents import Selector, Decomposer, Refiner
    from core.chat_manager import ChatManager
    from core.const import SYSTEM_NAME, DECOMPOSER_NAME
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    print("WARNING: Core MAC-SQL modules not found. Using fallbacks.")
    
    # Define minimal fallbacks if original not found
    class ChatManager:
        def __init__(self, *args, **kwargs):
            pass
    
    class Selector:
        def __init__(self, *args, **kwargs):
            pass
            
    class Decomposer:
        def __init__(self, *args, **kwargs):
            pass
            
    class Refiner:
        def __init__(self, *args, **kwargs):
            pass
            
    SYSTEM_NAME = "System"

# Check if we have BIRD extensions
try:
    from core.bird_extensions import EnhancedBirdSelector, EnhancedBirdRefiner
    HAS_BIRD_EXTENSIONS = True
except ImportError:
    HAS_BIRD_EXTENSIONS = False
    
# Check if we have Spider extensions
try:
    from core.spider_extensions import EnhancedSpiderSelector, EnhancedSpiderRefiner
    HAS_SPIDER_EXTENSIONS = True
except ImportError:
    HAS_SPIDER_EXTENSIONS = False

# Try to import the pretty debug utility
try:
    from core.debug_pretty import enable_pretty_debug, install_communication_hooks
    HAS_PRETTY_DEBUG = True
except ImportError:
    HAS_PRETTY_DEBUG = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/enhanced_chat_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class EnhancedChatManager(ChatManager):
    """
    Enhanced Chat Manager that supports both BIRD and Spider datasets.
    
    This manager creates appropriate agent instances based on the dataset type
    and orchestrates their interactions.
    """
    
    def __init__(self, data_path, tables_json_path, log_path, model_name, dataset_name, 
                 lazy_loading=False, use_enhanced_agents=True, debug_mode=False, pretty_output=True):
        """
        Initialize an EnhancedChatManager.
        
        Args:
            data_path: Path to the dataset
            tables_json_path: Path to the tables.json file
            log_path: Path to the log file
            model_name: Name of the model to use
            dataset_name: Name of the dataset (bird or spider)
            lazy_loading: Whether to use lazy loading
            use_enhanced_agents: Whether to use enhanced agents when available
            debug_mode: Whether to enable debug mode with verbose output
            pretty_output: Whether to enable pretty formatted output for agent communication
        """
        # Skip parent init and create our own setup
        self.data_path = data_path
        self.tables_json_path = tables_json_path
        self.log_path = log_path
        self.model_name = model_name
        self.dataset_name = dataset_name.lower() if dataset_name else ""
        self.lazy_loading = lazy_loading
        self.debug_mode = debug_mode  # Add debug_mode attribute
        self.pretty_output = pretty_output  # Add pretty_output attribute
        self.execution_trace = []  # For tracking agent interactions
        
        # Check for dataset-specific paths
        if self.dataset_name == 'spider':
            # Check if Spider data directory exists
            spider_paths = [
                os.path.join("MAC-SQL", "data", "spider", "database"),
                os.path.join("data", "spider", "database")
            ]
            
            for path in spider_paths:
                if os.path.exists(path):
                    logger.info(f"Found spider data directory at: {path}")
                    self.data_path = path
                    break
            
            # Check if Spider tables.json exists
            spider_tables_paths = [
                os.path.join("MAC-SQL", "data", "spider", "tables.json"),
                os.path.join("data", "spider", "tables.json")
            ]
            
            for path in spider_tables_paths:
                if os.path.exists(path):
                    logger.info(f"Found spider tables.json at: {path}")
                    self.tables_json_path = path
                    break
        
        # Create chat group with appropriate agents based on dataset
        logger.info(f"Initializing EnhancedChatManager with dataset: {dataset_name}")
        logger.info(f"Creating agents for dataset: {dataset_name}")
        
        self._create_agents(use_enhanced_agents)
        
        # Initialize logging
        from core import llm
        llm.init_log_path(log_path)
        
        # Enable pretty debug if requested
        if self.pretty_output and HAS_PRETTY_DEBUG:
            enable_pretty_debug()
            install_communication_hooks(self)
            logger.info("Pretty debug output enabled")
    
    def send(self, message: Dict[str, Any]):
        """
        Override the send method to enable debugging and pretty output
        
        Args:
            message: The message to send
            
        Returns:
            The processed message
        """
        # Extract relevant information for debugging
        from_agent = message.get('from', 'System')
        to_agent = message.get('send_to', 'Unknown')
        
        # Log key message transitions
        if self.debug_mode:
            logger.debug(f"Message: {from_agent} → {to_agent}")
            
            # Log key fields with schema/foreign key previews
            if 'desc_str' in message:
                preview = message['desc_str'][:100] + "..." if len(message['desc_str']) > 100 else message['desc_str']
                logger.debug(f"  desc_str: {preview}")
            
            if 'fk_str' in message:
                preview = message['fk_str'][:100] + "..." if len(message['fk_str']) > 100 else message['fk_str']
                logger.debug(f"  fk_str: {preview}")
                
            if 'final_sql' in message:
                preview = message['final_sql'][:100] + "..." if len(message['final_sql']) > 100 else message['final_sql']
                logger.debug(f"  final_sql: {preview}")
                
            if 'pred' in message:
                preview = message['pred'][:100] + "..." if len(message['pred']) > 100 else message['pred']
                logger.debug(f"  pred: {preview}")
        
        # Ensure 'from' field is set for tracking
        if 'from' not in message and len(self.chat_group) > 0:
            # Try to determine the sender based on current message
            for agent in self.chat_group:
                if hasattr(agent, 'name') and agent.name == from_agent:
                    message['from'] = agent.name
                    break
        
        # Call parent implementation to route the message
        return super().send(message)
        
    def _create_agents(self, use_enhanced_agents=True):
        """
        Create the appropriate agents based on the dataset.
        
        Args:
            use_enhanced_agents: Whether to use enhanced agents when available
        """
        # Available enhanced agents
        has_spider_extensions = False
        has_bird_extensions = False
        
        # Check for enhanced agent availability
        if use_enhanced_agents:
            try:
                from core.spider_extensions import EnhancedSpiderSelector, EnhancedSpiderRefiner
                has_spider_extensions = True
                logger.info("Using enhanced Spider agents")
            except ImportError:
                logger.info("Enhanced Spider agents not available")
            
            try:
                from core.bird_extensions import EnhancedBirdSelector, EnhancedBirdRefiner
                has_bird_extensions = True
                logger.info("Using enhanced BIRD agents")
            except ImportError:
                logger.info("Enhanced BIRD agents not available")
        
        # Create agents based on dataset type and enhanced agent availability
        if self.dataset_name == 'bird' and has_bird_extensions:
            from core.bird_extensions import EnhancedBirdSelector, EnhancedBirdRefiner
            self.chat_group = [
                EnhancedBirdSelector(
                    data_path=self.data_path,
                    tables_json_path=self.tables_json_path,
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                ),
                Decomposer(
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                ),
                EnhancedBirdRefiner(
                    data_path=self.data_path,
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                )
            ]
        elif self.dataset_name == 'spider' and has_spider_extensions:
            self.chat_group = [
                EnhancedSpiderSelector(
                    data_path=self.data_path,
                    tables_json_path=self.tables_json_path,
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                ),
                Decomposer(
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                ),
                EnhancedSpiderRefiner(
                    data_path=self.data_path,
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                )
            ]
        else:
            # Default agents
            self.chat_group = [
                Selector(
                    data_path=self.data_path,
                    tables_json_path=self.tables_json_path,
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                ),
                Decomposer(
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                ),
                Refiner(
                    data_path=self.data_path,
                    model_name=self.model_name,
                    dataset_name=self.dataset_name
                )
            ]
        
        # Log created agents for debugging
        for i, agent in enumerate(self.chat_group):
            logger.info(f"Agent {i} name: {agent.name}")
            logger.info(f"Agent {i} class: {agent.__class__.__name__}")
            logger.info(f"Agent {i} attributes: {dir(agent)}")
    
    def start(self, user_message: Dict[str, Any]):
        """
        Start the chat with a user message.
        
        Args:
            user_message: The user message to process, containing:
                - db_id: Database ID
                - query: Natural language query
                - evidence: Additional evidence (optional)
                - ground_truth: Ground truth SQL (optional)
        
        Returns:
            The processed message containing the final SQL query
        """
        # Add dataset-specific information to the message
        if self.dataset_name == 'spider':
            user_message['dataset_type'] = 'spider'
        elif self.dataset_name == 'bird':
            user_message['dataset_type'] = 'bird'
            
        # Add execution trace for debugging
        user_message['exec_trace'] = []
        
        # Debug info for Spider dataset
        if self.dataset_name == 'spider' and 'db_id' in user_message:
            logger.debug(f"Using Selector agent: {self.chat_group[0].name}")
            logger.debug(f"Using Decomposer agent: {self.chat_group[1].name}")
            logger.debug(f"Using Refiner agent: {self.chat_group[2].name}")
        
        # Call parent method to process the message through the agents
        super().start(user_message)
        
        # Post-process predictions based on dataset
        if 'pred' in user_message:
            # For Spider, attempt to fix column names
            if self.dataset_name == 'spider' and HAS_SPIDER_EXTENSIONS:
                try:
                    # Fix column names based on database
                    if 'db_id' in user_message:
                        from core.spider_extensions import fix_column_names
                        user_message['pred'] = fix_column_names(user_message['pred'], user_message['db_id'])
                except Exception as e:
                    logger.error(f"Error fixing column names: {e}")
        
        # Log final SQL
        if 'pred' in user_message:
            logger.info(f"Final SQL: {user_message['pred']}")
            # Log execution match if available
            if 'execution_match' in user_message:
                logger.info(f"Execution match: {user_message['execution_match']}")
        
        return user_message
    
    def _format_message_for_output(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the message for output, removing internal fields.
        
        Args:
            message: The message to format
            
        Returns:
            Formatted message
        """
        # Create a copy to avoid modifying the original
        output_message = message.copy()
        
        # Remove internal fields
        internal_fields = [
            'send_to', 'exec_trace', 'pruned', 'chosen_db_schem_dict',
            'extracted_schema', 'desc_str', 'fk_str'
        ]
        
        for field in internal_fields:
            if field in output_message:
                del output_message[field]
        
        return output_message

def run_with_agents(dataset_path, db_path, tables_path, num_samples=5, dataset_type='bird'):
    """
    Run evaluation using agent-based architecture
    
    Args:
        dataset_path: Path to dataset file
        db_path: Path to database directory
        tables_path: Path to tables.json file
        num_samples: Number of samples to evaluate
        dataset_type: 'bird' or 'spider'
    
    Returns:
        Evaluation results
    """
    # Create logging directory
    os.makedirs("logs", exist_ok=True)
    
    # Load queries based on dataset type
    if dataset_type == 'bird':
        try:
            from core.bird_extensions import load_bird_subset
            queries = load_bird_subset(dataset_path, num_samples=num_samples)
        except ImportError:
            logger.error("Could not load BIRD subset - module not found")
            return []
    elif dataset_type == 'spider':
        try:
            from core.spider_extensions import load_spider_subset
            queries = load_spider_subset(dataset_path, num_samples=num_samples)
        except ImportError:
            logger.error("Could not load Spider subset - module not found")
            return []
    else:
        logger.error(f"Unsupported dataset type: {dataset_type}")
        return []
    
    # Set up the model name (default from environment variable)
    model_name = os.getenv("TOGETHER_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct")
    
    # Initialize chat manager
    manager = EnhancedChatManager(
        data_path=db_path,
        tables_json_path=tables_path,
        log_path=f"logs/{dataset_type}_agent_test.log",
        model_name=model_name,
        dataset_name=dataset_type
    )
    
    # Process queries through agent framework
    results = []
    for i, query in enumerate(queries):
        logger.info(f"Processing query {i+1}/{len(queries)}")
        
        # Create message for chat manager
        message = {
            'db_id': query.get('db_id', ''),
            'query': query.get('question', ''),
            'evidence': query.get('evidence', ''),
            'extracted_schema': {},
            'ground_truth': query.get('SQL', ''),
            'difficulty': query.get('difficulty', 'unknown'),
            'send_to': "Selector"  # Start with the Selector agent
        }
        
        # Process through agents
        manager.start(message)
        
        # Store result
        result = {
            'db_id': query.get('db_id', ''),
            'question': query.get('question', ''),
            'gold_sql': query.get('SQL', ''),
            'predicted_sql': message.get('pred', ''),
            'execution_match': message.get('execution_match', False)
        }
        results.append(result)
        
        # Log the result
        match_status = "✓" if result['execution_match'] else "✗"
        logger.info(f"Result: {match_status} Execution Match")
    
    return results 