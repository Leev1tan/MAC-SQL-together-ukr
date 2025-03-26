#!/usr/bin/env python
"""
Test script for MAC-SQL with Together AI using the agent-based architecture on the Spider dataset.
"""

import os
import sys
import json
import argparse
import logging
import sqlite3
from pathlib import Path
import random
from pprint import pprint
from dotenv import load_dotenv
from core.enhanced_chat_manager import EnhancedChatManager
from core.macsql_together_adapter import TogetherAIAdapter, patch_api_func, configure_together_rate_limits
from core.spider_extensions import load_spider_subset, execute_and_compare_queries
from core.const import ENGINE_TOGETHER
from typing import List, Dict, Any, Optional
import copy
import types
from datetime import datetime

# Add imports for agent flow tracking and visualization
try:
    from core.tracking import install_tracker, get_tracker, clear_flow, MessageTracker
    from core.visualization import visualize_agent_flow, print_agent_flow
    # Try to import serialization utilities
    try:
        from core.utils.serialization import safe_serialize_message
    except ImportError:
        # Define a fallback serialization function
        def safe_serialize_message(message):
            """Create a safe copy of the message without circular references."""
            if message is None:
                return {}
            
            if isinstance(message, dict):
                # Make a copy so we don't modify the original
                result = {}
                for k, v in message.items():
                    if k not in ["agent_instance", "trace_history"]:
                        if v is None:
                            result[k] = None
                        elif isinstance(v, (str, int, float, bool)):
                            result[k] = v
                        elif isinstance(v, (list, dict)):
                            # Convert complex objects to strings
                            try:
                                import json
                                result[k] = json.dumps(v)
                            except:
                                result[k] = str(v)
                        else:
                            # Other objects just convert to string
                            result[k] = str(v)
                return result
            return str(message)
    
    # Make sure we have a tracker instance
    flow_tracker = get_tracker()
    HAS_AGENT_FLOW = True
except ImportError:
    HAS_AGENT_FLOW = False
    
    # Create a simple mock tracker for fallback
    class MockTracker:
        def __init__(self):
            self.messages = []
            self.current_session_id = None
            
        def get_messages(self):
            return self.messages
            
        def clear(self):
            self.messages = []
            
        def track_message(self, **kwargs):
            msg = kwargs
            self.messages.append(msg)
            return "mock-id"
            
    flow_tracker = MockTracker()
    
    def install_tracker(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    def install_flow_tracker(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    def print_agent_flow(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    def visualize_agent_flow(*args, **kwargs):
        print("Agent flow visualization not available.")
    
    def clear_flow(*args, **kwargs):
        print("Agent flow tracking not available.")
        
    # Define a thorough fallback serialization function
    def safe_serialize_message(message):
        """Create a safe copy of the message without circular references."""
        if message is None:
            return {}
            
        if isinstance(message, dict):
            # Make a copy so we don't modify the original
            result = {}
            for k, v in message.items():
                if k not in ["agent_instance", "trace_history"]:
                    if v is None:
                        result[k] = None
                    elif isinstance(v, (str, int, float, bool)):
                        result[k] = v
                    elif isinstance(v, (list, dict)):
                        # Convert complex objects to strings
                        try:
                            import json
                            result[k] = json.dumps(v)
                        except:
                            result[k] = str(v)
                    else:
                        # Other objects just convert to string
                        result[k] = str(v)
            return result
        return str(message)

# Try to import pretty debug utilities
try:
    from core.debug_pretty import Colors, print_agent_header, print_schema_preview, print_sql
    HAS_PRETTY_DEBUG = True
except ImportError:
    HAS_PRETTY_DEBUG = False
    # Define fallback color class
    class Colors:
        PURPLE = ''
        BLUE = ''
        CYAN = ''
        GREEN = ''
        YELLOW = ''
        RED = ''
        BOLD = ''
        UNDERLINE = ''
        END = ''

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", ENGINE_TOGETHER)

def find_spider_data():
    """Find the Spider dataset directory."""
    # First check environment variable
    env_path = os.getenv("SPIDER_PATH")
    if env_path and os.path.exists(env_path):
        logger.info(f"Found Spider data directory from environment variable: {env_path}")
        return str(env_path)
    
    # If no environment variable, check standard locations
    possible_paths = [
        Path("data/spider"),
        Path("MAC-SQL/data/spider"),
        Path("../MAC-SQL/data/spider"),
        Path("./data/spider"),
        Path("./MAC-SQL/data/spider")
    ]
    
    for path in possible_paths:
        if path.exists():
            # Verify dataset files and database directory
            dataset_files_exist = (
                (path / "dev.json").exists() or 
                (path / "train_spider.json").exists()
            )
            db_dir_exists = (path / "database").exists()
            
            if dataset_files_exist and db_dir_exists:
                logger.info(f"Found Spider data directory at: {path}")
                return str(path)
    
    raise FileNotFoundError("Spider dataset directory not found. Please place it in data/spider or MAC-SQL/data/spider or set the SPIDER_PATH environment variable.")

def get_spider_db_path(spider_path: str) -> str:
    """Returns the path to the database directory within the Spider dataset"""
    return os.path.join(spider_path, "database")

def load_spider_queries(path, num_samples=5):
    """Load a subset of Spider queries."""
    # Determine which file to load from
    dev_path = os.path.join(path, "dev.json")
    
    try:
        with open(dev_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading Spider queries: {e}")
        raise
    
    # Select random samples if needed
    if num_samples and num_samples < len(data):
        samples = random.sample(data, num_samples)
    else:
        samples = data
    
    return samples

def print_db_tables(db_id, db_path):
    """Print the actual database tables for a given database."""
    try:
        # Make sure db_path points to the database directory
        if not os.path.basename(db_path) == "database":
            db_path = os.path.join(db_path, "database")
        
        # Find database file
        db_file = os.path.join(db_path, db_id, f"{db_id}.sqlite")
        if not os.path.exists(db_file):
            logger.error(f"Database file not found: {db_file}")
            print(f"  Error: Database file '{db_file}' not found")
            return
        
        if HAS_PRETTY_DEBUG:
            print(f"\n{Colors.BOLD}{Colors.GREEN}DATABASE SCHEMA: {db_id}{Colors.END}")
        else:
            print(f"\nActual tables in {db_id}:")
        
        # Connect to database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            if HAS_PRETTY_DEBUG:
                print(f"  {Colors.BOLD}{Colors.CYAN}- {table_name}{Colors.END}")
            else:
                print(f"  - {table_name}")
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                # col format: (cid, name, type, notnull, dflt_value, pk)
                col_name = col[1]
                col_type = col[2]
                if HAS_PRETTY_DEBUG:
                    print(f"    {Colors.YELLOW}• {col_name} ({col_type}){Colors.END}")
                else:
                    print(f"    • {col_name} ({col_type})")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error querying database tables: {e}")
        print(f"  Error retrieving tables: {str(e)}")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5, help="Number of samples to test")
    parser.add_argument("--show-llm", action="store_true", help="Show LLM responses")
    parser.add_argument("--visualize", action="store_true", help="Visualize agent communication")
    parser.add_argument("--full-trace", action="store_true", help="Show full trace of agent communication")
    parser.add_argument("--viz-format", type=str, default="html", choices=["html", "json", "mermaid"], 
                        help="Visualization format")
    parser.add_argument("--viz-output", type=str, default=None, 
                        help="Path to save visualization output")
    parser.add_argument("--compare", action="store_true", help="Compare with pipeline approach")
    return parser.parse_args()

def test_single_query(db_id, question, gold_sql=None, args=None):
    """Test a single query with the agent-based approach."""
    global flow_tracker, schema_data, reasoning_data

    # Set defaults
    spider_path = os.getenv("MAC_SQL_SPIDER_PATH", "MAC-SQL/data/spider")
    visualize = args.visualize if args else False
    viz_format = args.viz_format if args and hasattr(args, 'viz_format') else "html"
    viz_output = args.viz_output if args and hasattr(args, 'viz_output') else None
    full_trace = args.full_trace if args and hasattr(args, 'full_trace') else False
    
    # Initialize tracking variables
    schema_data = None
    reasoning_data = None

    # Check if we have the agent flow tracking
    try:
        import core.tracking.message_tracker
        HAS_AGENT_FLOW = True
    except (ImportError, ModuleNotFoundError):
        HAS_AGENT_FLOW = False
        if visualize:
            logger.error("Agent flow tracking is not available")
            visualize = False

    # Find Spider data path
    spider_path = find_spider_data()
    
    # Print database tables for debugging
    print_db_tables(db_id, spider_path)
    
    # Initialize or clear the flow tracker
    if HAS_AGENT_FLOW:
        try:
            from core.tracking.message_tracker import MessageTracker, initialize_tracker
            # Re-initialize tracker to ensure it's available
            flow_tracker = initialize_tracker()
            flow_tracker.clear()
            logger.info("Initialized message tracker for agent flow visualization")
        except Exception as e:
            logger.error(f"Error initializing tracker: {e}")
            flow_tracker = None
    else:
        flow_tracker = None
        logger.warning("Agent flow tracking not available")
    
    # Create a message object for the agent
    message = {
        'db_id': db_id,
        'query': question,
        'spider_path': spider_path,
        'from': 'User',
        'send_to': 'Selector'
    }
    
    # Process the message through the agent pipeline
    print(f"\n\n[USER] {question}")
    
    # Set up the chat manager
    show_llm_responses = args.debug if args and hasattr(args, 'debug') else False
    
    # Set up tables path and database path
    db_path = os.path.join(spider_path, "database")
    tables_json_path = os.path.join(spider_path, "tables.json")
    
    # Create the chat manager with debug_mode enabled
    log_path = args.log_path if hasattr(args, 'log_path') else None
    
    chat_manager = EnhancedChatManager(
        data_path=db_path,
        tables_json_path=tables_json_path,
        model_name=TOGETHER_MODEL,
        dataset_name="spider",
        debug_mode=True,
        log_path=log_path
    )
    
    # Print info about agents
    for i, agent in enumerate(chat_manager.chat_group):
        print(f"Agent {i}: {agent.name} ({agent.__class__.__name__})")
    
    # Install agent flow tracker if visualization or full trace is enabled
    if HAS_AGENT_FLOW and (visualize or full_trace):
        try:
            # Import and explicitly init tracker
            from core.tracking.message_tracker import initialize_tracker, get_tracker
            flow_tracker = initialize_tracker()
            flow_tracker.clear()
            
            # Try importing hooks module for better tracking
            try:
                from core.tracking.hooks import install_tracking_hooks
                # Install hooks on chat manager
                install_tracking_hooks(chat_manager)
                logger.info("✅ Installed tracking hooks on all agents")
            except (ImportError, AttributeError):
                # Fall back to legacy tracking
                try:
                    from core.tracking import install_tracker
                    install_tracker(chat_manager)
                    logger.info("✅ Installed legacy message tracking")
                except (ImportError, AttributeError):
                    logger.warning("⚠️ Could not install any tracking hooks, visualization may be limited")
            
            # Enable debug logging for agent flow
            logging.getLogger("core.tracking").setLevel(logging.DEBUG)
            
            # Track the initial user message
            flow_tracker.track_message(
                sender="User",
                recipient="Selector",
                message_data=safe_serialize_message(message),
                message_type="initial_query"
            )
            logger.info(f"✅ Tracked initial message: User → Selector")
            logger.info(f"Tracker has {len(flow_tracker.get_messages())} messages")
            
            # Keep track of the original _chat_single_round method
            original_chat_single_round = chat_manager._chat_single_round
            
            # Store for special fields we want to track
            schema_data = None
            reasoning_data = None
            
            # Define a new chat_single_round that tracks messages
            def tracked_chat_single_round(self, message):
                """
                Monkey patched version of _chat_single_round that tracks agent transitions
                """
                global schema_data, reasoning_data
                
                try:
                    # Determine if message is a dict or an object with attributes
                    is_dict = isinstance(message, dict)
                    
                    # Save original destination and sender - handle both object and dict formats
                    if is_dict:
                        original_to = message.get('to', None)
                        original_from = message.get('from', None)
                    else:
                        # For object access
                        original_to = getattr(message, 'to', None)
                        original_from = getattr(message, 'from', getattr(message, 'sender', None))
                        
                    # Log the message tracking
                    logger.debug(f"Tracking message from {original_from} to {original_to}")
                    
                    # Save message state before processing
                    if is_dict:
                        pre_message = copy.deepcopy(message)
                    else:
                        # For object access, convert to dict if possible
                        pre_message = copy.deepcopy(message.to_dict() if hasattr(message, 'to_dict') else vars(message))
                    
                    # Call the original method directly using the original reference
                    try:
                        original_chat_single_round(message)  # Don't pass self, the method is already bound
                    except Exception as e:
                        logger.error(f"Error in _chat_single_round: {e}")
                        raise e
                    
                    # Save message state after processing
                    if is_dict:
                        post_message = copy.deepcopy(message)
                    else:
                        # For object access, convert to dict if possible
                        post_message = copy.deepcopy(message.to_dict() if hasattr(message, 'to_dict') else vars(message))
                    
                    # Identify the agent's contribution based on changes
                    contribution = {}
                    
                    # Extract fields safely with a helper function
                    def get_field(msg, field):
                        if isinstance(msg, dict):
                            return msg.get(field)
                        return getattr(msg, field, None)
                    
                    # Capture special data for tracking
                    if original_to == "Selector" and not schema_data:
                        # Remember schema data for visualization
                        post_desc = get_field(post_message, 'desc_str')
                        if post_desc:
                            schema_data = {
                                'desc_str': post_desc,
                                'db_id': get_field(post_message, 'db_id', ''),
                                'agent': original_to,
                                'timestamp': datetime.now().isoformat()
                            }
                    elif original_to == "Decomposer" and not reasoning_data:
                        # Remember reasoning data for visualization
                        reasoning = None
                        for field in ['reasoning', 'rationale', 'chain_of_thought', 'explanation']:
                            if field in post_message:
                                reasoning = get_field(post_message, field)
                                if reasoning:
                                    break
                        
                        if not reasoning and 'message' in post_message:
                            reasoning = get_field(post_message, 'message')
                        
                        if reasoning:
                            reasoning_data = {
                                'reasoning': reasoning,
                                'final_sql': get_field(post_message, 'final_sql', ''),
                                'agent': original_to,
                                'timestamp': datetime.now().isoformat()
                            }
                    
                    # Depending on which agent processed this message, track what changed
                    if original_to == "Selector":
                        # Selector contributions (typically db_id, desc_str)
                        pre_desc = get_field(pre_message, 'desc_str')
                        post_desc = get_field(post_message, 'desc_str')
                        if post_desc and post_desc != pre_desc:
                            contribution['desc_str'] = post_desc
                            
                    elif original_to == "Decomposer":
                        # Decomposer contributions (typically final_sql)
                        pre_sql = get_field(pre_message, 'final_sql')
                        post_sql = get_field(post_message, 'final_sql')
                        if post_sql and post_sql != pre_sql:
                            contribution['final_sql'] = post_sql
                        
                        pre_qa = get_field(pre_message, 'qa_pairs')
                        post_qa = get_field(post_message, 'qa_pairs')
                        if post_qa and post_qa != pre_qa:
                            contribution['qa_pairs'] = post_qa
                            
                    elif original_to == "Refiner":
                        # Refiner contributions
                        pre_sql = get_field(pre_message, 'final_sql')
                        post_sql = get_field(post_message, 'final_sql')
                        if post_sql and post_sql != pre_sql:
                            contribution['refined_sql'] = post_sql
                        
                        pre_pred = get_field(pre_message, 'pred')
                        post_pred = get_field(post_message, 'pred')
                        if post_pred and post_pred != pre_pred:
                            contribution['pred'] = post_pred
                        
                        pre_fixed = get_field(pre_message, 'fixed')
                        post_fixed = get_field(post_message, 'fixed')
                        if post_fixed and post_fixed != pre_fixed:
                            contribution['fixed'] = post_fixed
                            
                    elif original_to == "System":
                        # System contributions (typically execution_match)
                        pre_match = get_field(pre_message, 'execution_match')
                        post_match = get_field(post_message, 'execution_match')
                        if post_match is not None and post_match != pre_match:
                            contribution['execution_match'] = post_match
                    
                    # Store the agent's contribution in the message safely
                    if is_dict:
                        message['agent_contribution'] = contribution
                        message['agent_role'] = original_to
                    else:
                        setattr(message, 'agent_contribution', contribution)
                        setattr(message, 'agent_role', original_to)
                    
                    # Track transitions if flow tracker is available
                    if 'flow_tracker' in globals() and flow_tracker is not None:
                        try:
                            # Create safe message version for tracking with full content
                            safe_message = {
                                'msg_type': get_field(message, 'msg_type') or 'unknown',
                                'contribution': contribution,
                                'role': original_to
                            }
                            
                            # Include the most important fields based on agent type
                            if original_to == "Selector":
                                # Include schema description - capture the full schema
                                safe_message['desc_str'] = get_field(post_message, 'desc_str')
                                safe_message['db_id'] = get_field(post_message, 'db_id')
                                # Also capture any schema selections or pruning decisions
                                if 'schema_selections' in post_message:
                                    safe_message['schema_selections'] = get_field(post_message, 'schema_selections')
                                # Capture the full message for better visualization
                                for key in post_message:
                                    if key not in safe_message and key not in ['agent_instance', 'trace_history']:
                                        safe_message[key] = get_field(post_message, key)
                            
                            elif original_to == "Decomposer":
                                # Include SQL, reasoning process and chain-of-thought
                                safe_message['final_sql'] = get_field(post_message, 'final_sql')
                                # Include original query for context
                                if 'query' in post_message:
                                    safe_message['query'] = get_field(post_message, 'query')
                                else:
                                    safe_message['query'] = get_field(post_message, 'original_query')
                                # Try to capture reasoning if available in various forms
                                for reasoning_field in ['reasoning', 'rationale', 'chain_of_thought', 'explanation', 'subquestions', 'steps', 'qa_pairs']:
                                    if reasoning_field in post_message:
                                        safe_message[reasoning_field] = get_field(post_message, reasoning_field)
                                # Capture the message from LLM if available
                                if 'message' in post_message:
                                    safe_message['llm_response'] = get_field(post_message, 'message')
                                # Capture the full message content for better visualization
                                for key in post_message:
                                    if key not in safe_message and key not in ['agent_instance', 'trace_history']:
                                        safe_message[key] = get_field(post_message, key)
                            
                            elif original_to == "Refiner":
                                # Include refined SQL and changes
                                safe_message['pred'] = get_field(post_message, 'pred')
                                safe_message['final_sql'] = get_field(post_message, 'final_sql')
                                safe_message['fixed'] = get_field(post_message, 'fixed')
                                safe_message['try_times'] = get_field(post_message, 'try_times')
                                # Also capture any reasoning about SQL refinements
                                if 'refinement_explanation' in post_message:
                                    safe_message['refinement_explanation'] = get_field(post_message, 'refinement_explanation')
                                # Capture the LLM response if available
                                if 'message' in post_message:
                                    safe_message['llm_response'] = get_field(post_message, 'message')
                            
                            elif original_to == "System":
                                # Include execution match and other system details
                                safe_message['execution_match'] = get_field(post_message, 'execution_match')
                                # Include gold SQL for comparison
                                if 'gold' in post_message:
                                    safe_message['gold'] = get_field(post_message, 'gold')
                                # Capture execution results if available
                                if 'execution_results' in post_message:
                                    safe_message['execution_results'] = get_field(post_message, 'execution_results')
                            
                            elif original_to == "User":
                                # Include original query
                                safe_message['query'] = get_field(post_message, 'query')
                            
                            # Keep the original query for context in all messages
                            if 'query' in post_message:
                                safe_message['original_query'] = get_field(post_message, 'query')
                            
                            # Add debug trackers to understand content being captured
                            logger.debug(f"Agent {original_to} contribution keys: {list(contribution.keys())}")
                            logger.debug(f"Safe message keys: {list(safe_message.keys())}")
                            
                            # Determine the next agent in the chain for tracking
                            next_agent = None
                            if 'send_to' in post_message and post_message['send_to'] != original_to:
                                next_agent = post_message['send_to'] 
                            
                            # Always track the transition based on original_to
                            # This ensures we capture all agent processing, even if
                            # the agent doesn't change the message destination
                            if original_to == "Selector":
                                message_type = "selector_processed"
                                flow_tracker.track_message(original_to, next_agent or "Decomposer", safe_message, message_type)
                                logger.debug(f"Tracked: {original_to} processed message (selector_processed)")
                                
                            elif original_to == "Decomposer":
                                message_type = "decomposer_processed"
                                flow_tracker.track_message(original_to, next_agent or "Refiner", safe_message, message_type)
                                logger.debug(f"Tracked: {original_to} processed message (decomposer_processed)")
                                
                            elif original_to == "Refiner":
                                message_type = "refiner_processed"
                                flow_tracker.track_message(original_to, next_agent or "System", safe_message, message_type)
                                logger.debug(f"Tracked: {original_to} processed message (refiner_processed)")
                                
                            elif original_to == "System":
                                message_type = "system_processed"
                                flow_tracker.track_message(original_to, next_agent or "User", safe_message, message_type)
                                logger.debug(f"Tracked: {original_to} processed message (system_processed)")
                            
                        except Exception as e:
                            logger.error(f"Error creating safe message: {e}")
                except Exception as e:
                    logger.error(f"Error in tracked_chat_single_round: {e}")
                    logger.exception(e)
            
            # Replace the original method with our tracked version
            chat_manager._chat_single_round = types.MethodType(tracked_chat_single_round, chat_manager)
        except Exception as e:
            logger.error(f"Error setting up flow tracker: {e}")
            flow_tracker = None
    else:
        # Skip tracking if not visualizing
        logger.info("Skipping message tracking (visualization disabled)")
    
    # Make sure the message has the right format
    chat_manager._chat_single_round(message)
    
    # Print the final SQL query
    print("\n[FINAL SQL]")
    print(message.get('pred', '') if 'pred' in message else message.get('final_sql', 'No SQL generated'))
    
    # Check for execution match
    if gold_sql:
        message['execution_match'] = check_exec_match(
            spider_path, db_id, message.get('pred', ''), gold_sql
        )
        print(f"\n[EXECUTION MATCH] {message.get('execution_match', False)}")
    
    # Track the final result if visualization is enabled
    if HAS_AGENT_FLOW and visualize:
        flow_tracker.track_message(
            sender="System",
            recipient="User",
            message_data={
                "final_sql": message.get('pred', '') or message.get('final_sql', ''),
                "execution_match": message.get('execution_match', False),
                "gold_sql": gold_sql
            },
            message_type="final_result"
        )
    
    # Visualize agent flow if requested
    if args and args.visualize:
        try:
            # Get visualization format and output path
            viz_format = getattr(args, 'viz_format', 'html')
            
            # Create a default output path if none provided
            if not hasattr(args, 'viz_output') or not args.viz_output:
                # Create a consistent filename based on db_id and current time
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                viz_output = f"output/agent_flow_{db_id}.{viz_format}"
            else:
                viz_output = args.viz_output
            
            # Ensure output directory exists
            viz_dir = os.path.dirname(viz_output)
            if viz_dir:
                os.makedirs(viz_dir, exist_ok=True)
            
            # Debug tracker state
            logger.info(f"Tracker has {len(flow_tracker.get_messages())} messages")
            
            # Get messages directly from tracker
            messages = flow_tracker.get_messages()
            
            # Add db_id to messages if needed
            for msg in messages:
                if isinstance(msg.get('data', {}), dict) and 'db_id' not in msg['data'] and db_id:
                    msg['data']['db_id'] = db_id
            
            # Generate visualization using our wrapper that handles trackers properly
            viz_path = visualize_agent_flow_wrapper(messages=messages, format_type=viz_format, output_path=viz_output)
            if viz_path:
                print(f"Agent flow visualization saved to: {viz_path}")
            else:
                print("Failed to generate agent flow visualization")
        except Exception as e:
            print(f"Error visualizing agent flow: {e}")
            import traceback
            traceback.print_exc()
    
    # Prepare the result dictionary
    result = {
        'db_id': db_id,
        'question': question,
        'gold_sql': gold_sql,
        'pred_sql': message.get('pred', ''),
        'execution_match': message.get('execution_match', False)
    }
    
    return result

def check_exec_match(spider_path, db_id, pred_sql, gold_sql):
    """Check if the predicted SQL matches the gold SQL by execution."""
    try:
        db_dir = os.path.join(spider_path, "database", db_id)
        db_path = os.path.join(db_dir, f"{db_id}.sqlite")
        
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return False
            
        # Use execute_and_compare_queries from spider_extensions
        match = execute_and_compare_queries(pred_sql, gold_sql, db_id, os.path.join(spider_path, "database"))
        return match
    except Exception as e:
        logger.error(f"Error checking execution match: {e}")
        return False

# Update the log_agent_messages function to use safe serialization
def log_agent_messages(message):
    """Log messages exchanged between agents for visualization."""
    from_agent = message.get('from', 'Unknown')
    to_agent = message.get('send_to', 'Unknown')
    
    if from_agent and to_agent:
        logger.debug(f"Message from {from_agent} to {to_agent}")
        
        # Create a safe copy of the message for tracking
        safe_message = safe_serialize_message(message)
        
        # Only track if we're not already tracking via the _chat_single_round hook
        # This function is now primarily for backward compatibility or direct logging
        if HAS_AGENT_FLOW and not hasattr(message, "_tracked"):
            # Mark as tracked so we don't duplicate
            message._tracked = True
            
            # Determine the message type based on agent transition
            message_type = "agent_message"
            
            # Track specific transitions
            if from_agent == 'Selector' and to_agent == 'Decomposer':
                message_type = "selector_to_decomposer"
                logger.info(f"⭐ SELECTOR → DECOMPOSER message captured")
            elif from_agent == 'Decomposer' and to_agent == 'Refiner':
                message_type = "decomposer_to_refiner"
                logger.info(f"⭐ DECOMPOSER → REFINER message captured")
            elif from_agent == 'Refiner' and to_agent == 'System':
                message_type = "refiner_to_system"
                logger.info(f"⭐ REFINER → SYSTEM message captured")
            
            # Track the message
            try:
                # Track this message exchange in the flow tracker
                flow_tracker.track_message(
                    sender=from_agent,
                    recipient=to_agent,
                    message_data=safe_message,
                    message_type=message_type
                )
                logger.debug(f"Manually tracked message: {from_agent} → {to_agent} ({message_type})")
            except Exception as e:
                logger.error(f"Failed to track message: {e}")

def test_agent_subset(
    spider_path: str,
    num_samples: int = 5,
    visualize: bool = False,
    log_level: str = "INFO"
):
    """Run tests for a subset of the Spider dataset."""
    # Set up logging
    logging.getLogger().setLevel(log_level)
    
    # Make sure the output directory exists
    os.makedirs("output", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Try to import evaluate_metrics if available
    try:
        import evaluate_metrics
        has_metrics = True
        logger.info("Evaluation metrics module loaded successfully")
    except ImportError:
        has_metrics = False
        logger.warning("Evaluate metrics module not found. Advanced metrics will be disabled.")
    
    # Get the database path
    db_path = get_spider_db_path(spider_path)
    
    # Load subset of Spider queries
    queries = load_spider_queries(spider_path, num_samples)
    
    # Initialize Together API adapter - no arguments version
    try:
        adapter = TogetherAIAdapter()
        logger.info(f"Initialized TogetherAIAdapter")
    except Exception as e:
        logger.warning(f"Error initializing TogetherAIAdapter: {e}")
    
    # Configure rate limits
    configure_together_rate_limits()
    
    # Apply patching to work with Together API
    patch_api_func()
    
    # Enable pretty debug output if available
    if HAS_PRETTY_DEBUG:
        print("🌟 Pretty debug output enabled")
        print("Agent communication will be displayed in a more readable format")
    
    # Initialize agent flow tracking if available
    if HAS_AGENT_FLOW and visualize:
        install_tracker(track_all_agents=True)
        print("✅ Installed tracking hooks")
        logger.info("Pretty debug output enabled")
    
    # Initialize results list
    results = []
    
    # Create lists to store data for metrics evaluation
    pred_queries = []
    gold_queries = []
    db_ids = []
    
    # Process each query
    for i, query_data in enumerate(queries):
        query_text = query_data.get("question", "")
        db_id = query_data.get("db_id", "")
        gold_sql = query_data.get("query", "")
        
        # Store query info for metrics evaluation
        pred_queries.append(None)  # Will be filled after processing
        gold_queries.append(gold_sql)
        db_ids.append(db_id)
        
        print("\n" + "-" * 50)
        print(f"Processing query {i+1}/{len(queries)}: {db_id}")
        print("-" * 50 + "\n")
        
        # Print database schema
        print_db_tables(db_id, db_path)
        
        # If using agent flow tracking, clear previous session
        if HAS_AGENT_FLOW and visualize:
            clear_flow()
            flow_tracker.clear()
            logger.info("Initialized message tracker for agent flow visualization")
        
        # Track user message if using visualization
        if HAS_AGENT_FLOW and visualize:
            flow_tracker.track_message(
                sender="User",
                recipient="Selector",
                content=query_text,
                message_type="initial_query"
            )
            logger.info("✅ Tracked initial message: User → Selector")
            logger.info(f"Tracker has {len(flow_tracker.get_messages())} messages")
        
        # Print query
        print(f"\n[USER] {query_text}")
        
        # Initialize Enhanced Chat Manager with the correct parameters
        chat_manager = EnhancedChatManager(
            data_path=db_path,
            tables_json_path=os.path.join(spider_path, "tables.json"),
            log_path=os.path.join("logs", "agent_test.log"),
            model_name=TOGETHER_MODEL,
            dataset_name="spider",
            debug_mode=True,
            pretty_output=True
        )
        
        # Print agent info
        agent_names = [agent.name for agent in chat_manager.chat_group]
        agent_classes = [agent.__class__.__name__ for agent in chat_manager.chat_group]
        
        for j, (name, cls) in enumerate(zip(agent_names, agent_classes)):
            print(f"Agent {j}: {name} ({cls})")
        
        # If using agent flow tracking, install hooks
        if HAS_AGENT_FLOW and visualize:
            from core.tracking.hooks import install_hooks_on_agents
            hooks_installed = install_hooks_on_agents(chat_manager.chat_group, flow_tracker)
            logger.info(f"✅ Installed tracking hooks on all agents")
            logger.info(f"Tracker has {len(flow_tracker.get_messages())} messages")
        
        # Process query
        try:
            # Create a message object for the agent
            message = {
                'db_id': db_id,
                'query': query_text,
                'from': 'User',
                'send_to': 'Selector'
            }
            
            # Process the message through the chat manager
            chat_manager._chat_single_round(message)
            
            # Extract the SQL from the message
            pred_sql = message.get('pred', '') or message.get('final_sql', '')
            
            # Update the pred_queries list with the predicted SQL
            pred_queries[queries.index(query_data)] = pred_sql
            
            # Print result
            print("\n[FINAL SQL]")
            if HAS_PRETTY_DEBUG:
                print_sql(pred_sql)
            else:
                print(pred_sql)
            
            # Use execute_and_compare_queries from spider_extensions
            match = execute_and_compare_queries(pred_sql, gold_sql, db_id, db_path)
            
            execution_match = match[0]
            exec_results = match[1]
            
            # Print match result
            print(f"\n[EXECUTION MATCH] {match}")
            
            # Create result item
            result_item = {
                "db_id": db_id,
                "question": query_text,
                "predicted_sql": pred_sql,
                "gold_sql": gold_sql,
                "execution_match": execution_match,
                "execution_results": {
                    "pred_result": str(exec_results.get("pred_result", [])),
                    "gold_result": str(exec_results.get("gold_result", [])),
                }
            }
            
            results.append(result_item)
            
            # Save visualization if enabled
            if HAS_AGENT_FLOW and visualize:
                try:
                    html_path = f"output/agent_flow_{db_id}.html"
                    visualize_agent_flow(
                        flow_tracker.get_messages(),
                        output_file=html_path,
                        format="html"
                    )
                    print(f"Agent flow visualization saved to: {html_path}")
                except Exception as e:
                    logger.error(f"Error creating visualization: {e}")
            
            # Print execution match result
            match_symbol = "✓" if execution_match else "✗"
            print(f"Result: {match_symbol} Execution Match")
            print(f"Gold SQL: {gold_sql}")
            print(f"Predicted SQL: {pred_sql}")
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            result_item = {
                "db_id": db_id,
                "question": query_text,
                "predicted_sql": "ERROR",
                "gold_sql": gold_sql,
                "execution_match": False,
                "error": str(e)
            }
            results.append(result_item)
            pred_queries[queries.index(query_data)] = "ERROR"
            
            # Set default values for execution_match and pred_sql for error case
            execution_match = False
            pred_sql = "ERROR"
            
            # Print execution match result for error case
            print(f"Result: ✗ Execution Match (Error)")
            print(f"Gold SQL: {gold_sql}")
            print(f"Predicted SQL: ERROR")
    
    # Calculate advanced metrics if evaluate_metrics is available
    if has_metrics:
        try:
            metrics = evaluate_metrics.evaluate_queries(
                pred_queries=pred_queries,
                gold_queries=gold_queries,
                db_ids=db_ids,
                db_dir=db_path,
                tables_json_path=os.path.join(spider_path, "tables.json")
            )
            
            print("\n=== Advanced Metrics ===")
            print(f"Exact Match (EM): {metrics['exact_match']*100:.2f}%")
            print(f"Execution Accuracy (EX): {metrics['execution_accuracy']*100:.2f}%")
            print(f"Valid Efficiency Score (VES): {metrics['valid_efficiency_score']:.2f}")
            
            # Add metrics to each result
            for i, result in enumerate(results):
                result["metrics"] = {
                    "exact_match": metrics.get("exact_match", 0),
                    "execution_accuracy": metrics.get("execution_accuracy", 0),
                    "valid_efficiency_score": metrics.get("valid_efficiency_score", 0)
                }
                
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            # Log detailed stack trace for debugging
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
    
    # Save results
    results_file = "output/spider_agent_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {results_file}")
    
    return results

def compare_approaches(num_samples=5):
    """
    Compare agent-based approach with pipeline approach for Spider dataset.
    
    Args:
        num_samples: Number of samples to test
        
    Returns:
        Comparison results
    """
    # Create output directory if it doesn't exist
    Path("output").mkdir(exist_ok=True)
    
    # Run agent-based approach
    print("Running agent-based approach for Spider...")
    agent_results = test_agent_subset(num_samples, "output/spider_agent_results.json")
    
    # Run pipeline approach (if available)
    pipeline_results = None
    try:
        # Import run_with_together (assuming it has a run_spider_test function)
        from run_with_together import run_spider_test
        
        print("\nRunning pipeline approach for Spider...")
        pipeline_results = run_spider_test(num_samples)
        
        # Save pipeline results
        with open("output/spider_pipeline_results.json", 'w') as f:
            json.dump(pipeline_results, f, indent=2)
        
        # Calculate pipeline accuracy
        pipeline_matches = sum(1 for r in pipeline_results['results'] if r['execution_match'])
        pipeline_accuracy = pipeline_matches / len(pipeline_results['results']) if pipeline_results['results'] else 0
        
        print(f"\nPipeline Execution Accuracy: {pipeline_accuracy:.2%} ({pipeline_matches}/{len(pipeline_results['results'])})")
        
        # Compare results
        agent_matches = sum(1 for r in agent_results if r['execution_match'])
        agent_accuracy = agent_matches / len(agent_results) if agent_results else 0
        
        print("\nComparison:")
        print(f"Agent-based Accuracy: {agent_accuracy:.2%}")
        print(f"Pipeline Accuracy: {pipeline_accuracy:.2%}")
        print(f"Difference: {agent_accuracy - pipeline_accuracy:.2%}")
        
        return {
            'agent_accuracy': agent_accuracy,
            'pipeline_accuracy': pipeline_accuracy,
            'difference': agent_accuracy - pipeline_accuracy
        }
    
    except (ImportError, AttributeError) as e:
        print(f"\nError: {e}")
        print("Pipeline approach comparison not available. Only agent-based results will be shown.")
        return None

def main():
    """Main function."""
    args = parse_args()
    
    try:
        # Configure logging
        logging.getLogger("core.agent_flow").setLevel(logging.DEBUG)
        logging.getLogger("core.agent_flow_viz").setLevel(logging.DEBUG)
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        # Find Spider dataset
        spider_path = find_spider_data()
        
        # Run test with agent-based approach
        agent_results = test_agent_subset(
            spider_path=spider_path, 
            num_samples=args.samples,
            visualize=args.visualize,
            log_level=logging.INFO
        )
        
        # Compare with pipeline approach if requested
        if args.compare and HAS_RUN_WITH_TOGETHER:
            print("\nRunning pipeline approach for comparison...")
            # Implementation of pipeline comparison would go here
            print("Pipeline approach comparison not available yet.")
        
    except Exception as e:
        logger.error(f"Error running test: {e}", exc_info=True)
        raise

def visualize_agent_flow_wrapper(messages=None, format_type="html", output_path=None):
    """Visualizes the current agent flow using the specified format."""
    try:
        # Check if we have a proper flow tracker
        if flow_tracker is None:
            logger.warning("No flow tracker available to visualize.")
            return None
        
        # Get messages either from parameter or from tracker
        if messages is None:
            messages = flow_tracker.get_messages()
        
        # Check if we have messages to visualize
        if not messages or len(messages) == 0:
            logger.warning("No messages to visualize.")
            return None
        
        # Make sure we have at least the system agents (more than just User->System)
        agent_senders = set(msg.get('sender', '') for msg in messages if msg.get('sender') not in ['User', 'System', ''])
        if not agent_senders:
            logger.warning("No agent messages found to visualize, only User/System messages.")
        
        logger.info(f"Visualizing {len(messages)} messages in {format_type} format")
        logger.info(f"Agent senders found: {', '.join(agent_senders)}")
        
        # Determine output path if not provided
        if not output_path:
            # Use a consistent filename based on db_id if available
            db_id = None
            for msg in messages:
                if isinstance(msg.get('data', {}), dict) and 'db_id' in msg.get('data', {}):
                    db_id = msg['data']['db_id']
                    break
            
            if db_id:
                output_path = f"output/agent_flow_{db_id}.{format_type}"
            else:
                # Use a timestamp if db_id not available
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output/agent_flow_{timestamp}.{format_type}"
            
        # Make sure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Call appropriate visualization method
        if format_type == "html":
            # Import from core.visualization if available
            try:
                from core.visualization.formatter import format_agent_flow_html
                result = format_agent_flow_html(messages, output_path=output_path, title="MAC-SQL Agent Flow")
                logger.info(f"HTML visualization saved to {output_path}")
                return output_path
            except ImportError:
                # Create a custom HTML output
                from core.visualization.visualizer import visualize_agent_flow
                result = visualize_agent_flow(format_type="html", output_path=output_path)
                return result
        elif format_type == "json":
            from core.visualization.visualizer import visualize_agent_flow
            result = visualize_agent_flow(format_type="json", output_path=output_path)
            return result
        elif format_type == "mermaid":
            from core.visualization.visualizer import visualize_agent_flow
            result = visualize_agent_flow(format_type="mermaid", output_path=output_path)
            return result
        else:
            logger.error(f"Unsupported format: {format_type}")
            return None
        
    except Exception as e:
        logger.error(f"Error during visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Replace the imported function with our wrapper if needed
if HAS_AGENT_FLOW:
    visualize_agent_flow = visualize_agent_flow_wrapper

if __name__ == "__main__":
    main() 