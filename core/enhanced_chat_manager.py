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
    from core.const import SYSTEM_NAME, DECOMPOSER_NAME, SELECTOR_NAME, REFINER_NAME
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

# Add these imports at the top of the file, after other imports
from core.const_ukr import SELECTOR_NAME, DECOMPOSER_NAME, REFINER_NAME, SYSTEM_NAME

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
        
        # Initialize chat_group that will hold our agents
        self.chat_group = []
        
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
        Create the agents for the specified dataset.
        Returns:
            The list of created agents.
        """
        # Log that we're creating agents
        logger.info(f"Creating agents for dataset: {self.dataset_name}")
        
        # Try to load the spider extensions
        try:
            from core.spider_extensions import load_spider_selector
            has_spider_extensions = True
            logger.info("Using enhanced Spider agents")
        except ImportError:
            has_spider_extensions = False
            logger.info("Spider extensions not available, using base agents")
            
        # Try to load the BIRD extensions
        try:
            from core.bird_extensions import load_bird_selector
            has_bird_extensions = True
            logger.info("Using enhanced BIRD agents")
        except ImportError:
            has_bird_extensions = False
            logger.info("BIRD extensions not available, using base agents")
            
        # Try to load the BIRD-UKR extensions
        try:
            from core.bird_ukr_extensions import load_bird_ukr_extensions
            has_bird_ukr_extensions = True
            logger.info("Using BIRD-UKR PostgreSQL agents")
        except ImportError:
            has_bird_ukr_extensions = False
            logger.info("BIRD-UKR extensions not available")
        
        # Dataset-specific agent creation
        if self.dataset_name == "bird-ukr" and has_bird_ukr_extensions:
            # Use the BIRD-UKR PostgreSQL agents
            from core.bird_ukr_extensions import load_bird_ukr_extensions
            agent_dict = load_bird_ukr_extensions(
                data_path=self.data_path,
                model_name=self.model_name,
                tables_json_path=self.tables_json_path
            )
            # Convert to a list that matches the expected format
            agents = [agent_dict[name] for name in [SELECTOR_NAME, DECOMPOSER_NAME, REFINER_NAME]]
        elif self.dataset_name == "bird" and has_bird_extensions:
            # Use the BIRD-specific agents
            from core.bird_extensions import load_bird_selector, load_bird_refiner
            
            # Create selector
            selector = load_bird_selector(
                data_path=self.data_path,
                tables_json_path=self.tables_json_path,
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            # Create decomposer
            decomposer = Decomposer(
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            # Create refiner
            refiner = load_bird_refiner(
                data_path=self.data_path,
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            agents = [selector, decomposer, refiner]
            
        elif self.dataset_name == "spider" and has_spider_extensions:
            # Use the Spider-specific agents
            from core.spider_extensions import load_spider_selector, load_spider_refiner
            
            # Create selector
            selector = load_spider_selector(
                data_path=self.data_path,
                tables_json_path=self.tables_json_path,
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            # Create decomposer
            decomposer = Decomposer(
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            # Create refiner
            refiner = load_spider_refiner(
                data_path=self.data_path,
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            agents = [selector, decomposer, refiner]
        else:
            # Use the default agents
            logger.info("Using default agents")
            
            # Create the selector with the without_selector flag
            selector = Selector(
                data_path=self.data_path, 
                tables_json_path=self.tables_json_path,
                model_name=self.model_name,
                dataset_name=self.dataset_name, 
                without_selector=getattr(self, 'without_selector', False)  # Use default value if attribute doesn't exist
            )
            
            # Create the decomposer
            decomposer = Decomposer(
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            # Create the refiner
            refiner = Refiner(
                data_path=self.data_path,
                model_name=self.model_name,
                dataset_name=self.dataset_name
            )
            
            agents = [selector, decomposer, refiner]
        
        # Set the agent names correctly
        agents[0].name = SELECTOR_NAME
        agents[1].name = DECOMPOSER_NAME
        agents[2].name = REFINER_NAME
        
        # Debug: Print out the agent names and classes
        for i, agent in enumerate(agents):
            logger.info(f"Agent {i} name: {agent.name}")
            logger.info(f"Agent {i} class: {agent.__class__.__name__}")
            attrs = dir(agent)
            logger.info(f"Agent {i} attributes: {attrs}")
        
        # Set the chat_group attribute to the created agents
        self.chat_group = agents
        
        return agents
    
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
        
        # Check if we have a parent implementation of start() to call
        if HAS_CORE:
            # Call parent method to process the message through the agents
            super().start(user_message)
        else:
            # Custom implementation when the parent class doesn't have a start method
            # Basic implementation to route the message through agents
            logger.info("Using custom start implementation (no parent method available)")
            current_message = user_message.copy()
            
            # Initial routing to the first agent (selector)
            if 'send_to' not in current_message and len(self.chat_group) > 0:
                current_message['send_to'] = self.chat_group[0].name
                
            # Process through agents until we get a final result
            max_rounds = 10  # Prevent infinite loops
            rounds = 0
            
            while rounds < max_rounds:
                rounds += 1
                logger.info(f"Processing round {rounds}")
                
                # Determine which agent should process this message
                target_agent_name = current_message.get('send_to')
                if not target_agent_name:
                    break
                    
                # Find the target agent
                target_agent = None
                for agent in self.chat_group:
                    if agent.name == target_agent_name:
                        target_agent = agent
                        break
                        
                if not target_agent:
                    logger.error(f"Agent {target_agent_name} not found")
                    break
                    
                # Process the message with the target agent
                logger.info(f"Sending message to {target_agent_name}")
                try:
                    # If the agent has a process_message method, use it
                    if hasattr(target_agent, 'process_message'):
                        response = target_agent.process_message(current_message)
                        current_message.update(response)
                    else:
                        # Otherwise, rely on the chat manager to route the message
                        logger.info(f"Agent {target_agent_name} doesn't have process_message method")
                        break
                        
                    # Check if we've reached the end of the chain
                    if 'final_sql' in current_message:
                        user_message['pred'] = current_message.get('final_sql')
                        break
                        
                    # Check if we need to continue to another agent
                    if 'send_to' in current_message and current_message['send_to'] != target_agent_name:
                        logger.info(f"Message forwarded to {current_message['send_to']}")
                        continue
                    else:
                        # No further routing
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing message with agent {target_agent_name}: {e}")
                    break
                    
            # Update the original message with results
            if 'final_sql' in current_message:
                user_message['pred'] = current_message.get('final_sql')
        
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