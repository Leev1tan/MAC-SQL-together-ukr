"""
Pretty Debug Utilities for MAC-SQL
Provides functions to visualize agent communication in a more human-readable format
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Terminal colors for prettier output
class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# List to store agent communication flow
agent_flow = []

def track_agent_communication(from_agent: str, to_agent: str, message: Dict[str, Any]):
    """Track agent communication for later display"""
    global agent_flow
    
    # Create a simplified copy of the message
    simplified_input = {
        'query': message.get('query', ''),
        'db_id': message.get('db_id', '')
    }
    
    # Create a simplified output based on message content
    simplified_output = {}
    
    # Track schema info if available
    if 'desc_str' in message:
        simplified_input['schema'] = "Schema available"
    if 'fk_str' in message and message['fk_str']:
        simplified_input['foreign_keys'] = "Foreign keys available"
    
    # Track SQL if available
    if 'final_sql' in message:
        simplified_output['sql'] = message['final_sql']
    elif 'pred' in message:
        simplified_output['sql'] = message['pred']
    
    # Add to flow tracker
    agent_flow.append({
        'agent': from_agent,
        'action': "process_message",
        'input': simplified_input,
        'output': simplified_output
    })
    
    print(f"[DEBUG] Tracked agent {from_agent} communicating to {to_agent}")

def print_agent_header(agent_name: str, message_type: str = "THINKING"):
    """Print a formatted header for agent messages"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}💬 AGENT: {agent_name} - {message_type}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'-'*80}{Colors.END}")

def print_schema_preview(schema: str, max_lines: int = 10):
    """Print a preview of the schema information"""
    if not schema:
        print(f"{Colors.YELLOW}[No schema provided]{Colors.END}")
        return
        
    lines = schema.split('\n')
    print(f"{Colors.CYAN}SCHEMA PREVIEW:{Colors.END}")
    
    # Print header lines always
    db_line = next((line for line in lines if line.startswith("Database:")), None)
    if db_line:
        print(f"{Colors.GREEN}{db_line}{Colors.END}")
    
    # Print tables with formatting
    for i, line in enumerate(lines):
        if i >= max_lines:
            print(f"{Colors.YELLOW}... [truncated, {len(lines) - max_lines} more lines]{Colors.END}")
            break
            
        # Highlight table names
        if line.startswith("# Table:"):
            print(f"{Colors.BOLD}{Colors.GREEN}{line}{Colors.END}")
        # Highlight foreign keys section  
        elif "Foreign keys" in line:
            print(f"{Colors.BOLD}{Colors.YELLOW}{line}{Colors.END}")
        # Regular lines
        elif i > 0:  # Skip Database line which was already printed
            print(f"{Colors.CYAN}{line}{Colors.END}")

def print_sql(sql: str):
    """Print SQL with syntax highlighting"""
    if not sql:
        print(f"{Colors.YELLOW}[No SQL provided]{Colors.END}")
        return
        
    # Truncate long SQL
    if len(sql) > 500:
        sql = sql[:500] + "... [truncated]"
        
    print(f"{Colors.CYAN}SQL QUERY:{Colors.END}")
    
    # Basic SQL syntax highlighting
    keywords = ["SELECT", "FROM", "WHERE", "JOIN", "ON", "GROUP BY", "HAVING", 
                "ORDER BY", "LIMIT", "DISTINCT", "COUNT", "SUM", "AVG", "MIN", "MAX"]
    
    # Split lines and highlight each line
    lines = sql.split('\n')
    for line in lines:
        highlighted = line
        for keyword in keywords:
            # Case-insensitive replacement with highlighting
            pattern = keyword.lower()
            if pattern in highlighted.lower():
                # Replace while preserving case
                idx = highlighted.lower().find(pattern)
                original_keyword = highlighted[idx:idx+len(keyword)]
                highlighted = highlighted.replace(
                    original_keyword, 
                    f"{Colors.BOLD}{Colors.YELLOW}{original_keyword}{Colors.END}{Colors.CYAN}"
                )
        
        # Print the highlighted line
        print(f"{Colors.CYAN}{highlighted}{Colors.END}")

def print_communication(from_agent: str, to_agent: str, message: Dict[str, Any]):
    """
    Print a pretty formatted representation of agent communication
    
    Args:
        from_agent: Name of the sending agent
        to_agent: Name of the receiving agent
        message: The message dictionary being passed
    """
    # Track communication for later display
    track_agent_communication(from_agent, to_agent, message)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Print message header
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}🔄 COMMUNICATION: {from_agent} → {to_agent} ({timestamp}){Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'-'*80}{Colors.END}")
    
    # Print important fields
    if 'query' in message:
        print(f"{Colors.BOLD}QUESTION:{Colors.END} {message['query']}")
    
    if 'db_id' in message:
        print(f"{Colors.BOLD}DATABASE:{Colors.END} {message['db_id']}")
    
    # Print schema preview if available
    if 'desc_str' in message:
        print_schema_preview(message['desc_str'])
    elif 'pruned_schema' in message:
        print_schema_preview(message['pruned_schema'])
    
    # Print SQL preview if available
    if 'final_sql' in message:
        print_sql(message['final_sql'])
    elif 'pred' in message:
        print_sql(message['pred'])
        
    # Print any errors
    if 'error' in message:
        print(f"{Colors.RED}ERROR: {message['error']}{Colors.END}")
    
    print(f"{Colors.BOLD}{Colors.PURPLE}{'-'*80}{Colors.END}")

def print_agent_communication_flow():
    """Print a simple structured summary of agent communication flow"""
    print("\n-------- Agent Communication Flow --------\n")
    
    if not agent_flow:
        print("No agent communication was tracked. The flow is empty.")
        print("\n----------------------------------------")
        return
    
    for i, step in enumerate(agent_flow):
        agent = step.get('agent', 'Unknown')
        action = step.get('action', 'process_message')
        
        print(f"[Step {i+1}] Agent: {agent}, Action: {action}")
        
        # Print input
        print("  Input:", end=" ")
        if step.get('input'):
            # Remove empty values to make output cleaner
            input_display = {k: v for k, v in step['input'].items() if v}
            if input_display:
                print(json.dumps(input_display, sort_keys=True))
            else:
                print("{}")
        else:
            print("{}")
        
        # Print output
        print("  Output:", end=" ")
        if step.get('output'):
            # Remove empty values to make output cleaner
            output_display = {k: v for k, v in step['output'].items() if v}
            if output_display:
                print(json.dumps(output_display, sort_keys=True))
            else:
                print("{}")
        else:
            print("{}")
        
        print("")
    
    print("----------------------------------------")

def install_communication_hooks(chat_manager):
    """
    Install hooks into the chat manager to pretty-print agent communication
    
    Args:
        chat_manager: The chat manager instance to hook into
    """
    original_send = chat_manager.send
    
    def hooked_send(message):
        """Hooked version of send method"""
        from_agent = message.get('from', 'System')
        to_agent = message.get('send_to', 'Unknown')
        
        # Pretty print the communication
        print_communication(from_agent, to_agent, message)
        
        # Call the original method
        return original_send(message)
    
    # Replace the method
    chat_manager.send = hooked_send
    print(f"{Colors.GREEN}✅ Installed pretty communication hooks{Colors.END}")

# Main function to enable pretty debug output
def enable_pretty_debug():
    """
    Enable pretty debug output for agent communication
    """
    # Clear agent flow list
    global agent_flow
    agent_flow = []
    
    print(f"{Colors.GREEN}🌟 Pretty debug output enabled{Colors.END}")
    print(f"{Colors.GREEN}Agent communication will be displayed in a more readable format{Colors.END}")
    
    # Check if we should always use colors
    os.environ['FORCE_COLOR'] = '1'
    
    return True 