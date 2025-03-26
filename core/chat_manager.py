# -*- coding: utf-8 -*-
from core.agents import Selector, Decomposer, Refiner
from core.const import MAX_ROUND, SYSTEM_NAME, SELECTOR_NAME, DECOMPOSER_NAME, REFINER_NAME

INIT_LOG__PATH_FUNC = None
LLM_API_FUC = None
try:
    from core import api
    LLM_API_FUC = api.safe_call_llm
    INIT_LOG__PATH_FUNC = api.init_log_path
    print(f"Use func from core.api in chat_manager.py")
except:
    from core import llm
    LLM_API_FUC = llm.safe_call_llm
    INIT_LOG__PATH_FUNC = llm.init_log_path
    print(f"Use func from core.llm in chat_manager.py")

import time
from pprint import pprint

# Initialize debugger if available
try:
    from core.debug_llm import debugger
    HAS_DEBUGGER = True
except ImportError:
    HAS_DEBUGGER = False
    print("Debug module not found, running without enhanced debugging")


class ChatManager(object):
    def __init__(self, data_path: str, tables_json_path: str, log_path: str, model_name: str, dataset_name:str, lazy: bool=False, without_selector: bool=False, debug_mode: bool=False):
        self.data_path = data_path  # root path to database dir, including all databases
        self.tables_json_path = tables_json_path # path to table description json file
        self.log_path = log_path  # path to record important printed content during running
        self.model_name = model_name  # name of base LLM called by agent
        self.dataset_name = dataset_name
        self.debug_mode = debug_mode
        self.execution_trace = []  # For tracking agent interactions
        
        self.ping_network()
        self.chat_group = [
            Selector(data_path=self.data_path, tables_json_path=self.tables_json_path, model_name=self.model_name, dataset_name=dataset_name, lazy=lazy, without_selector=without_selector),
            Decomposer(dataset_name=dataset_name),
            Refiner(data_path=self.data_path, dataset_name=dataset_name)
        ]
        INIT_LOG__PATH_FUNC(log_path)

    def ping_network(self):
        # check network status
        print("Checking network status...", flush=True)
        try:
            _ = LLM_API_FUC("Hello world!")
            print("Network is available", flush=True)
        except Exception as e:
            raise Exception(f"Network is not available: {e}")

    def _chat_single_round(self, message: dict):
        # we use `dict` type so value can be changed in the function
        for agent in self.chat_group:  # check each agent in the group
            if message['send_to'] == agent.name:
                # Create copy of the message before processing
                message_before = message.copy()
                
                # Track which agent is processing
                current_agent = agent.name
                
                # Log message pre-agent
                if self.debug_mode:
                    print(f"\n[DEBUG] Message to {current_agent}: {message_before.get('send_to')}")
                    if "desc_str" in message_before:
                        desc_preview = message_before["desc_str"][:100] + "..." if len(message_before["desc_str"]) > 100 else message_before["desc_str"]
                        print(f"[DEBUG] desc_str preview: {desc_preview}")
                    if "fk_str" in message_before:
                        fk_preview = message_before["fk_str"][:100] + "..." if len(message_before["fk_str"]) > 100 else message_before["fk_str"]
                        print(f"[DEBUG] fk_str preview: {fk_preview}")
                
                # Call the agent
                agent.talk(message)
                
                # Log message post-agent
                if self.debug_mode:
                    next_agent = message.get('send_to', 'Unknown')
                    print(f"[DEBUG] After {current_agent}, sending to: {next_agent}")
                    
                    # Check for key changes
                    for key in ['desc_str', 'fk_str', 'pred', 'final_sql']:
                        if key in message and (key not in message_before or message[key] != message_before.get(key)):
                            value = message[key]
                            preview = value[:100] + "..." if isinstance(value, str) and len(value) > 100 else value
                            print(f"[DEBUG] {key} changed: {preview}")
                
                # Record in execution trace
                if 'trace_enabled' in message and message['trace_enabled']:
                    trace_entry = {
                        'agent': agent.name,
                        'action': 'process_message',
                        'input': message_before,
                        'output': {
                            'next_agent': message.get('send_to'),
                            'message_updates': {
                                k: v for k, v in message.items() 
                                if k not in message_before or message_before.get(k) != v
                            }
                        }
                    }
                    
                    if HAS_DEBUGGER:
                        # Add full LLM prompt/response if available
                        if hasattr(agent, '_last_prompt') and hasattr(agent, '_last_response'):
                            trace_entry['output']['llm_response'] = {
                                'prompt': agent._last_prompt,
                                'response': agent._last_response
                            }
                    
                    # Add to trace
                    self.execution_trace.append(trace_entry)
                    
                    # Store in message for later access
                    if 'exec_trace' not in message:
                        message['exec_trace'] = []
                    message['exec_trace'] = self.execution_trace
                
                # Use debugger if available
                if HAS_DEBUGGER:
                    from_agent = agent.name
                    to_agent = message.get('send_to', SYSTEM_NAME)
                    debugger.log_agent_message(from_agent, to_agent, message)

    def start(self, user_message: dict):
        # we use `dict` type so value can be changed in the function
        start_time = time.time()
        
        # Reset execution trace
        self.execution_trace = []
        
        if user_message['send_to'] == SYSTEM_NAME:  # in the first round, pass message to prune
            user_message['send_to'] = SELECTOR_NAME
        
        if self.debug_mode:
            print(f"\n[DEBUG] Starting chat with message to: {user_message['send_to']}")
            print(f"[DEBUG] Original message: {user_message}")
        
        for round_num in range(MAX_ROUND):  # start chat in group
            if self.debug_mode:
                print(f"\n[DEBUG] Round {round_num+1}, message goes to: {user_message['send_to']}")
            
            self._chat_single_round(user_message)
            
            if user_message['send_to'] == SYSTEM_NAME:  # should terminate chat
                break
        
        end_time = time.time()
        exec_time = end_time - start_time
        print(f"\033[0;34mExecute {exec_time} seconds\033[0m", flush=True)


if __name__ == "__main__":
    test_manager = ChatManager(data_path="../data/spider/database",
                               log_path="",
                               model_name='gpt-4-32k',
                               dataset_name='spider',
                               lazy=True)
    msg = {
        'db_id': 'concert_singer',
        'query': 'How many singers do we have?',
        'evidence': '',
        'extracted_schema': {},
        'ground_truth': 'SELECT count(*) FROM singer',
        'difficulty': 'easy',
        'send_to': SYSTEM_NAME
    }
    test_manager.start(msg)
    pprint(msg)
    print(msg['pred'])