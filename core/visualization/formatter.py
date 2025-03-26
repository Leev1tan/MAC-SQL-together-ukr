"""
Agent Communication Formatters

This module provides formatter functions for displaying agent communication
in different formats: text table, HTML, Mermaid, and JSON.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_simple_text(messages: List[Dict[str, Any]]) -> str:
    """
    Format agent communication as simple text output
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        Formatted text string
    """
    if not messages:
        return "No agent flow to display."
        
    # Build the output
    output = []
    output.append("\n-------- Agent Communication Flow --------\n")
    
    # Print each message
    for i, msg in enumerate(messages):
        from_agent = msg.get('sender', 'Unknown')
        to_agent = msg.get('recipient', 'Unknown')
        action = msg.get('type', 'Unknown')
        timestamp = msg.get('timestamp', '')
        
        output.append(f"Step {i+1}: {from_agent} → {to_agent} ({action})")
        
        # Print message data if available
        data = msg.get('data', {})
        if data:
            if isinstance(data, dict):
                # Try to show important fields
                if 'query' in data:
                    if isinstance(data['query'], dict):
                        output.append(f"  Query: {data['query'].get('query', '')}")
                    else:
                        output.append(f"  Query: {data['query']}")
                        
                if 'final_sql' in data:
                    output.append(f"  SQL: {data['final_sql']}")
                elif 'pred' in data:
                    output.append(f"  SQL: {data['pred']}")
                
                # Show agent role if available
                if 'agent_role' in data:
                    output.append(f"  Role: {data['agent_role']}")
            else:
                output.append(f"  Data: {data}")
                
        output.append("")
        
    output.append("\n" + "-" * 40 + "\n")
    
    # Join and return
    return "\n".join(output)

def format_table_text(messages: List[Dict[str, Any]], max_width: int = 100) -> str:
    """
    Format agent communication as a text table
    
    Args:
        messages: List of message dictionaries
        max_width: Maximum width for the table
        
    Returns:
        Formatted text table
    """
    if not messages:
        return "No agent flow to display."
        
    # Build the output
    output = []
    output.append("\n-------- Agent Communication Flow --------\n")
    
    # Create column widths
    step_width = 5
    from_width = 10
    to_width = 10
    action_width = 20
    content_width = max_width - step_width - from_width - to_width - action_width - 9  # 9 for separators
    
    # Table header
    output.append(f"{'Step':<{step_width}} | {'From':<{from_width}} | {'To':<{to_width}} | {'Action':<{action_width}} | {'Content':<{content_width}}")
    output.append("-" * max_width)
    
    # Each message as a row
    for i, msg in enumerate(messages):
        from_agent = msg.get('sender', 'Unknown')
        to_agent = msg.get('recipient', 'Unknown')
        action = msg.get('type', 'Unknown')
        
        # Extract content from data
        data = msg.get('data', {})
        content = ""
        
        if isinstance(data, dict):
            # Try to extract query or SQL
            if 'query' in data:
                if isinstance(data['query'], dict):
                    q = data['query'].get('query', '')
                    if len(q) > content_width:
                        content = f"Q: {q[:content_width-5]}..."
                    else:
                        content = f"Q: {q}"
                elif isinstance(data['query'], str):
                    if len(data['query']) > content_width:
                        content = f"Q: {data['query'][:content_width-5]}..."
                    else:
                        content = f"Q: {data['query']}"
                else:
                    content = f"Q: {str(data['query'])[:content_width-5]}..."
                    
            # Try to extract SQL
            elif 'final_sql' in data:
                sql = data['final_sql']
                if len(sql) > content_width:
                    content = sql.replace('\n', ' ')[:content_width-3] + "..."
                else:
                    content = sql.replace('\n', ' ')
            elif 'pred' in data:
                sql = data['pred']
                if len(sql) > content_width:
                    content = sql.replace('\n', ' ')[:content_width-3] + "..."
                else:
                    content = sql.replace('\n', ' ')
        elif isinstance(data, str):
            # Just use the string data
            if len(data) > content_width:
                content = data[:content_width-3] + "..."
            else:
                content = data
                
        # Format the row
        output.append(f"{i+1:<{step_width}} | {from_agent[:from_width]:<{from_width}} | {to_agent[:to_width]:<{to_width}} | {action[:action_width]:<{action_width}} | {content}")
        
    output.append("\n" + "-" * 40 + "\n")
    
    # Join and return
    return "\n".join(output)

def format_agent_flow_html(messages, output_path=None, title="Agent Flow Visualization"):
    """Format agent flow as HTML with message bubbles."""
    if not messages:
        return "No agent flow to display."
    
    # Create HTML header
    html = [f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .flow-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .message {{
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: relative;
            transition: all 0.3s ease;
        }}
        
        .message:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .user-message {{
            background-color: #e3f2fd;
            border-left: 5px solid #2196F3;
            margin-left: 50px;
            margin-right: 20px;
        }}
        
        .ai-message {{
            background-color: #f1f8e9;
            border-left: 5px solid #8bc34a;
            margin-left: 20px;
            margin-right: 50px;
        }}
        
        .selector-message {{
            background-color: #fff8e1;
            border-left: 5px solid #ffc107;
        }}
        
        .decomposer-message {{
            background-color: #f3e5f5;
            border-left: 5px solid #9c27b0;
        }}
        
        .refiner-message {{
            background-color: #e8f5e9;
            border-left: 5px solid #4caf50;
        }}
        
        .system-message {{
            background-color: #eceff1;
            border-left: 5px solid #607d8b;
            font-style: italic;
        }}
        
        .agent-label {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #555;
        }}
        
        .transition {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 5px 0;
            position: relative;
        }}
        
        .transition svg {{
            width: 30px;
            height: 30px;
            fill: #999;
        }}
        
        .transition-label {{
            position: absolute;
            background: #f0f0f0;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 0.8em;
            color: #666;
            top: -8px;
        }}
        
        .message-content {{
            white-space: pre-wrap;
        }}
        
        .sql-code {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #007bff;
            font-family: monospace;
            overflow-x: auto;
            white-space: pre;
        }}
        
        .schema-info {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #28a745;
            font-family: monospace;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 10px;
        }}
        
        .collapsible {{
            background-color: #eee;
            color: #444;
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-weight: bold;
            margin-top: 10px;
            border-radius: 5px;
        }}
        
        .active, .collapsible:hover {{
            background-color: #ddd;
        }}
        
        .content {{
            padding: 0 18px;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.2s ease-out;
            background-color: #f9f9f9;
            border-radius: 0 0 5px 5px;
        }}
        
        .arrow {{
            margin-left: 5px;
            display: inline-block;
            transition: transform 0.2s;
        }}
        
        .active .arrow {{
            transform: rotate(180deg);
        }}
        
        .message-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            font-size: 0.8em;
            color: #999;
        }}
        
        .message-type {{
            font-size: 0.8em;
            padding: 2px 5px;
            border-radius: 3px;
            background-color: #eee;
            margin-left: 10px;
        }}
        
        .message-flow {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .arrow-right {{
            margin: 0 5px;
        }}

        .agent-flow-summary {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 5px solid #3498db;
        }}

        .agent-flow-summary h2 {{
            margin-top: 0;
            color: #2c3e50;
            font-size: 1.2em;
        }}

        .agent-flow-steps {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 15px 0;
        }}

        .agent-step {{
            padding: 8px 15px;
            background-color: #e1f5fe;
            border-radius: 20px;
            margin: 0 5px;
            font-weight: bold;
        }}

        .agent-step.user {{
            background-color: #e3f2fd;
        }}

        .agent-step.selector {{
            background-color: #fff8e1;
        }}

        .agent-step.decomposer {{
            background-color: #f3e5f5;
        }}

        .agent-step.refiner {{
            background-color: #e8f5e9;
        }}

        .agent-step.system {{
            background-color: #eceff1;
        }}

        .agent-arrow {{
            color: #999;
            font-size: 1.5em;
            margin: 0 5px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="flow-container">
"""]

    # Helper function to format timestamp
    def format_timestamp(timestamp_str):
        try:
            from datetime import datetime
            timestamp = datetime.fromisoformat(timestamp_str)
            return timestamp.strftime("%H:%M:%S")
        except:
            return timestamp_str.split("T")[1].split(".")[0] if "T" in timestamp_str else timestamp_str
    
    # Process each message
    question = None
    db_schema = None
    foreign_keys = None
    db_id = None
    
    # First scan for key information and identify unique agents
    agents_involved = set()
    for msg in messages:
        sender = msg.get('sender', 'Unknown')
        recipient = msg.get('recipient', 'Unknown')
        msg_data = msg.get('data', {})
        
        # Track unique agents (excluding User and System)
        if sender not in ['User', 'System', 'Unknown']:
            agents_involved.add(sender)
        if recipient not in ['User', 'System', 'Unknown']:
            agents_involved.add(recipient)
        
        # Try to extract the question
        if not question:
            if isinstance(msg_data, dict):
                if 'question' in msg_data:
                    question = msg_data['question']
                elif 'query' in msg_data and isinstance(msg_data['query'], dict):
                    question = msg_data['query'].get('question', '')
                elif 'query' in msg_data and isinstance(msg_data['query'], str):
                    question = msg_data['query']
            
        # Try to extract schema
        if not db_schema and isinstance(msg_data, dict):
            if 'desc_str' in msg_data:
                db_schema = msg_data['desc_str']
        
        # Try to extract foreign keys
        if not foreign_keys and isinstance(msg_data, dict):
            if 'fk_str' in msg_data:
                foreign_keys = msg_data['fk_str']
                
        # Try to extract db_id
        if not db_id and isinstance(msg_data, dict):
            if 'db_id' in msg_data:
                db_id = msg_data['db_id']
    
    # Show agent flow summary
    html.append("""
    <div class="agent-flow-summary">
        <h2>Agent Flow Summary</h2>
        <div class="agent-flow-steps">
            <div class="agent-step user">User</div>
            <div class="agent-arrow">→</div>
    """)
    
    # Standard agent flow: User -> Selector -> Decomposer -> Refiner -> System
    standard_flow = ["Selector", "Decomposer", "Refiner"]
    actual_flow = [agent for agent in standard_flow if agent in agents_involved]
    
    # Add each agent in the flow
    for agent in actual_flow:
        agent_class = agent.lower()
        html.append(f"""
            <div class="agent-step {agent_class}">{agent}</div>
            <div class="agent-arrow">→</div>
        """)
    
    # Close with System
    html.append("""
            <div class="agent-step system">System</div>
        </div>
    </div>
    """)
    
    # Display question at the top if available
    if question:
        html.append(f"""
    <div class="message user-message">
        <div class="message-header">
            <div class="agent-label">User Question</div>
            <div class="timestamp">{format_timestamp(messages[0].get('timestamp', ''))}</div>
        </div>
        <div class="message-content">{question}</div>
    </div>
    
    <div class="transition">
        <div class="transition-label">Query Submitted</div>
        <svg viewBox="0 0 24 24">
            <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
        </svg>
    </div>
""")
    
    # Display schema collapsible
    if db_schema:
        html.append(f"""
    <button type="button" class="collapsible">Database Schema {f"({db_id})" if db_id else ""} <span class="arrow">▼</span></button>
    <div class="content">
        <div class="schema-info">{db_schema}</div>
    </div>
""")
    
    # Display foreign keys collapsible
    if foreign_keys:
        html.append(f"""
    <button type="button" class="collapsible">Foreign Keys <span class="arrow">▼</span></button>
    <div class="content">
        <div class="schema-info">{foreign_keys}</div>
    </div>
""")
    
    # Organize messages by agent chain and filter duplicates
    agent_messages = {
        "User": [],
        "Selector": [],
        "Decomposer": [],
        "Refiner": [],
        "System": []
    }
    
    # Capture SQL development
    final_sql = None
    reasoning = []
    
    # First pass: organize by agent
    for msg in messages:
        sender = msg.get('sender', 'Unknown')
        msg_type = msg.get('type', 'unknown')
        
        # Skip internal or redundant messages
        if 'initial' in msg_type or 'agent_flow' in msg_type:
            continue
        
        # Categorize by sender
        if sender in agent_messages:
            agent_messages[sender].append(msg)
            
            # Check for SQL output
            msg_data = msg.get('data', {})
            if isinstance(msg_data, dict):
                if 'final_sql' in msg_data:
                    final_sql = msg_data['final_sql']
                elif 'pred' in msg_data:
                    final_sql = msg_data['pred']
                    
                if 'reasoning' in msg_data and msg_data['reasoning']:
                    reasoning.append(msg_data['reasoning'])
    
    # Second pass: only keep one representative message per agent
    agent_order = ["User", "Selector", "Decomposer", "Refiner", "System"]
    
    last_sender = None
    
    # Process each agent in order
    for agent in agent_order:
        if agent not in agent_messages or not agent_messages[agent]:
            continue
            
        # Sort messages by timestamp
        agent_messages[agent].sort(key=lambda x: x.get('timestamp', ''))
        
        # Take one representative message (could be improved to show best message)
        msgs = agent_messages[agent]
        best_msg = None
        
        # For output agents, prefer messages with SQL
        if agent in ["Decomposer", "Refiner", "System"]:
            for msg in msgs:
                msg_data = msg.get('data', {})
                if isinstance(msg_data, dict) and ('final_sql' in msg_data or 'pred' in msg_data):
                    best_msg = msg
                    break
        
        # If no best message identified, use the last one
        if not best_msg and msgs:
            best_msg = msgs[-1]
            
        if not best_msg:
            continue
            
        # Display transition arrow if we have a previous agent
        if last_sender:
            transition_type = f"{last_sender} → {agent}"
            html.append(f"""
    <div class="transition">
        <div class="transition-label">{transition_type}</div>
        <svg viewBox="0 0 24 24">
            <path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z" />
        </svg>
    </div>
""")
        
        # Render the message
        msg = best_msg
        sender = msg.get('sender', 'Unknown')
        recipient = msg.get('recipient', 'Unknown')
        message_type = msg.get('type', 'unknown')
        timestamp = msg.get('timestamp', '')
        msg_data = msg.get('data', {})
        
        # Determine message class based on sender
        if sender.lower() == 'user':
            message_class = 'user-message'
        elif sender.lower() == 'system':
            message_class = 'system-message'
        elif 'selector' in sender.lower():
            message_class = 'selector-message'
        elif 'decomposer' in sender.lower():
            message_class = 'decomposer-message'
        elif 'refiner' in sender.lower():
            message_class = 'refiner-message'
        else:
            message_class = 'ai-message'
            
        # Start message div
        html.append(f"""
    <div class="message {message_class}">
        <div class="message-header">
            <div class="agent-label">{sender}</div>
            <div>
                <span class="timestamp">{format_timestamp(timestamp)}</span>
                <span class="message-type">{message_type}</span>
            </div>
        </div>
        <div class="message-flow">From: {sender} → To: {recipient}</div>
""")
        
        # Extract message content
        message_content = ""
        
        # Check for SQL content
        sql_content = None
        if isinstance(msg_data, dict):
            if 'final_sql' in msg_data:
                sql_content = msg_data['final_sql']
            elif 'pred' in msg_data:
                sql_content = msg_data['pred']
        
        # Display message content
        if isinstance(msg_data, dict):
            # Show message content differently based on sender
            if 'selector' in sender.lower():
                # For selector, focus on schema selection
                tables_used = msg_data.get('tables_used', [])
                if tables_used:
                    message_content += "<strong>Selected Tables:</strong><br>"
                    message_content += ", ".join(tables_used)
                
            elif 'decomposer' in sender.lower():
                # For decomposer, focus on reasoning
                if 'reasoning' in msg_data:
                    message_content += "<strong>Reasoning:</strong><br>"
                    message_content += msg_data['reasoning']
                
            elif 'refiner' in sender.lower():
                # For refiner, focus on SQL improvements
                if 'issues' in msg_data:
                    message_content += "<strong>Issues:</strong><br>"
                    message_content += msg_data['issues']
                
                if 'execution_error' in msg_data:
                    message_content += "<strong>Execution Error:</strong><br>"
                    message_content += msg_data['execution_error']
                    
                if 'fixed' in msg_data and msg_data['fixed']:
                    message_content += "<strong>SQL Fixed:</strong> Yes<br>"
            
            # Generic handler for other fields
            for key, value in msg_data.items():
                if key not in ['final_sql', 'pred', 'desc_str', 'fk_str', 'reasoning', 'tables_used', 'issues', 'execution_error', 'query', 'question']:
                    if value and not isinstance(value, (dict, list)):
                        message_content += f"<strong>{key}:</strong> {value}<br>"
        
        elif isinstance(msg_data, str) and msg_data:
            message_content = msg_data
        
        # Display message content if we have any
        if message_content:
            html.append(f"""
        <div class="message-content">{message_content}</div>
""")
        
        # Display SQL if we have it
        if sql_content:
            html.append(f"""
        <div class="sql-code">{sql_content}</div>
""")
        
        # Close message div
        html.append("""
    </div>
""")
        
        # Update last sender
        last_sender = sender
    
    # Display reasoning collapsible if we have it
    if reasoning:
        combined_reasoning = "<br><br>".join(reasoning)
        html.append(f"""
    <button type="button" class="collapsible">Reasoning Process <span class="arrow">▼</span></button>
    <div class="content">
        <div class="message-content">{combined_reasoning}</div>
    </div>
""")
    
    # Display final SQL at the bottom
    if final_sql:
        html.append(f"""
    <div class="message system-message">
        <div class="agent-label">Final SQL</div>
        <div class="sql-code">{final_sql}</div>
    </div>
""")
    
    # Add message statistics
    html.append(f"""
    <button type="button" class="collapsible">Message Statistics <span class="arrow">▼</span></button>
    <div class="content">
        <p>Total messages: {len(messages)}</p>
        <ul>
""")

    # Count messages by agent
    agent_counts = {}
    for msg in messages:
        sender = msg.get('sender', 'Unknown')
        if sender not in agent_counts:
            agent_counts[sender] = 0
        agent_counts[sender] += 1
    
    # Show counts by agent
    for agent, count in agent_counts.items():
        html.append(f"            <li>{agent}: {count} messages</li>\n")
    
    html.append("""
        </ul>
    </div>
""")
    
    # Complete HTML
    html.append("""
    </div>
    
    <script>
        // Collapsible sections
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.maxHeight) {
                    content.style.maxHeight = null;
                } else {
                    content.style.maxHeight = content.scrollHeight + "px";
                }
            });
        }
    </script>
</body>
</html>
""")
    
    # Write to file if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html))
        logger.info(f"Saved agent flow HTML visualization to {output_path}")
        return output_path
    
    # Return HTML string
    return '\n'.join(html)

def generate_mermaid(messages: List[Dict[str, Any]], output_path: Optional[str] = None) -> str:
    """
    Generate Mermaid diagram of agent communication
    
    Args:
        messages: List of message dictionaries
        output_path: Path to save the Mermaid file
        
    Returns:
        Path to the generated Mermaid file
    """
    if not messages:
        logger.warning("No messages to visualize in Mermaid format")
        return None
        
    logger.debug(f"Creating Mermaid visualization with {len(messages)} messages")
    
    # Default output path if not specified
    if not output_path:
        output_path = "output/agent_flow.mmd"
        
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build Mermaid content
    mermaid = [
        "sequenceDiagram",
        "    title Agent Communication Flow"
    ]
    
    # Define participants
    participants = set()
    for msg in messages:
        sender = msg.get('sender', 'Unknown')
        recipient = msg.get('recipient', 'Unknown')
        participants.add(sender)
        participants.add(recipient)
    
    # Add participants in order: User, Selector, Decomposer, Refiner, System
    ordered_participants = ['User', 'Selector', 'Decomposer', 'Refiner', 'System']
    for participant in ordered_participants:
        if participant in participants:
            mermaid.append(f"    participant {participant}")
    
    # Add any other participants not in the ordered list
    for participant in participants:
        if participant not in ordered_participants:
            mermaid.append(f"    participant {participant}")
    
    # Add arrows for each message
    for i, msg in enumerate(messages):
        sender = msg.get('sender', 'Unknown')
        recipient = msg.get('recipient', 'Unknown')
        msg_type = msg.get('type', 'unknown')
        
        # Get message data
        data = msg.get('data', {})
        
        # Determine message content for the arrow
        if isinstance(data, dict):
            # First try to get agent role
            if 'agent_role' in data:
                content = data['agent_role']
            # Then try SQL or query
            elif 'pred' in data:
                content = "Refined SQL"
            elif 'final_sql' in data:
                content = "Generated SQL"
            elif 'query' in data:
                if isinstance(data['query'], str) and len(data['query']) > 20:
                    content = data['query'][:20] + "..."
                else:
                    content = str(data['query'])
            else:
                # Use message type as fallback
                content = msg_type.replace('_', ' ').title()
        else:
            content = str(data)[:20] + "..." if len(str(data)) > 20 else str(data)
        
        # Add the arrow
        mermaid.append(f"    {sender}->>+{recipient}: {content}")
    
    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(mermaid))
        logger.info(f"Mermaid visualization saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save Mermaid file: {str(e)}")
        return None

def generate_json(messages: List[Dict[str, Any]], output_path: Optional[str] = None) -> str:
    """
    Generate JSON representation of agent communication
    
    Args:
        messages: List of message dictionaries
        output_path: Path to save the JSON file
        
    Returns:
        Path to the generated JSON file
    """
    if not messages:
        logger.warning("No messages to visualize in JSON format")
        return None
        
    logger.debug(f"Creating JSON visualization with {len(messages)} messages")
    
    # Default output path if not specified
    if not output_path:
        output_path = "output/agent_flow.json"
        
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a JSON-serializable representation
    output = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages
    }
    
    # Write to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)
        logger.info(f"JSON visualization saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save JSON file: {str(e)}")
        return None

# Exports
__all__ = [
    'format_simple_text',
    'format_table_text',
    'format_agent_flow_html',
    'generate_mermaid',
    'generate_json'
] 