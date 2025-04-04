import sys
import json
import time
import os
import logging
from core.api_config import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TRY = 5

# 用来传递外面的字典进来
world_dict = {}

log_path = None
api_trace_json_path = None
total_prompt_tokens = 0
total_response_tokens = 0


def init_log_path(my_log_path):
    global total_prompt_tokens
    global total_response_tokens
    global log_path
    global api_trace_json_path
    log_path = my_log_path
    total_prompt_tokens = 0
    total_response_tokens = 0
    dir_name = os.path.dirname(log_path)
    os.makedirs(dir_name, exist_ok=True)

    # 另外一个记录api调用的文件
    api_trace_json_path = os.path.join(dir_name, 'api_trace.json')


def api_func(prompt:str):
    """
    Call the appropriate API based on configuration
    """
    global MODEL_NAME
    
    if USE_TOGETHER_AI:
        # Use Together AI API
        try:
            from core import api
            return api.together_api_call(prompt)
        except ImportError:
            logger.warning("Together API module not found, falling back to OpenAI")
    
    # Fall back to OpenAI API
    print(f"\nUse OpenAI model: {MODEL_NAME}\n")
    
    try:
        import openai
        
        if 'Llama' in MODEL_NAME:
            openai.api_version = None
            openai.api_type = "open_ai"
            openai.api_key = "EMPTY"
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
        else:
            response = openai.ChatCompletion.create(
                engine=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
        text = response['choices'][0]['message']['content'].strip()
        prompt_token = response['usage']['prompt_tokens']
        response_token = response['usage']['completion_tokens']
        return text, prompt_token, response_token
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        raise


def safe_call_llm(input_prompt, **kwargs) -> str:
    """
    Call LLM with error handling and logging
    """
    global MODEL_NAME
    global log_path
    global api_trace_json_path
    global total_prompt_tokens
    global total_response_tokens
    global world_dict

    # If Together API is enabled and available, use its own safe_call_llm
    if USE_TOGETHER_AI:
        try:
            from core import api
            return api.safe_call_llm(input_prompt, **kwargs)
        except ImportError:
            logger.warning("Together API module not found, using default implementation")
    
    # Default implementation with OpenAI
    for i in range(MAX_TRY):
        try:
            if log_path is None:
                # Simple logging to console
                sys_response, prompt_token, response_token = api_func(input_prompt)
                print(f"\nsys_response: \n{sys_response}")
                print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n')
            else:
                # Comprehensive logging to file
                if (log_path is None) or (api_trace_json_path is None):
                    raise FileExistsError('log_path or api_trace_json_path is None, init_log_path first!')
                    
                with open(log_path, 'a+', encoding='utf8') as log_fp, open(api_trace_json_path, 'a+', encoding='utf8') as trace_json_fp:
                    print('\n' + f'*'*20 +'\n', file=log_fp)
                    print(input_prompt, file=log_fp)
                    print('\n' + f'='*20 +'\n', file=log_fp)
                    sys_response, prompt_token, response_token = api_func(input_prompt)
                    print(sys_response, file=log_fp)
                    print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n', file=log_fp)
                    print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n')

                    # Reset dict for this invocation
                    if len(world_dict) > 0:
                        world_dict = {}
                    
                    # Add kwargs to world_dict
                    if len(kwargs) > 0:
                        world_dict = {}
                        for k, v in kwargs.items():
                            world_dict[k] = v
                            
                    # Add prompt and response to world_dict
                    world_dict['response'] = '\n' + sys_response.strip() + '\n'
                    world_dict['input_prompt'] = input_prompt.strip() + '\n'
                    world_dict['prompt_token'] = prompt_token
                    world_dict['response_token'] = response_token
                    
                    # Track total tokens
                    total_prompt_tokens += prompt_token
                    total_response_tokens += response_token
                    world_dict['cur_total_prompt_tokens'] = total_prompt_tokens
                    world_dict['cur_total_response_tokens'] = total_response_tokens

                    # Write to trace file
                    world_json_str = json.dumps(world_dict, ensure_ascii=False)
                    print(world_json_str, file=trace_json_fp)

                    # Clean up
                    world_dict = {}
                    world_json_str = ''

                    # Log token totals
                    print(f'\n total_prompt_tokens,total_response_tokens: {total_prompt_tokens} {total_response_tokens}\n', file=log_fp)
                    print(f'\n total_prompt_tokens,total_response_tokens: {total_prompt_tokens} {total_response_tokens}\n')
                    
            return sys_response
        except Exception as ex:
            print(ex)
            print(f'Request {MODEL_NAME} failed. try {i} times. Sleep 20 secs.')
            time.sleep(20)

    raise ValueError('safe_call_llm error after multiple retries!')


if __name__ == "__main__":
    res = safe_call_llm('Test query: what is SQL?')
    print(res)
