import re
import json

from lib.logger import logger
from lib.es_utils import get_bot_memory, create_bot_memory, update_bot_memory
from lib.chatgpt_utils import send
from lib.template_utils import render


def get_memory(user_id):
    memory = get_bot_memory(user_id)
    if memory is None:
        memory = []
        create_bot_memory(user_id)
    return memory


def merge_memory(user_settings, user_message, bot_message):
    data = {'bot_name': user_settings['bot_name'], 'user_name': user_settings['user_name']}
    prompt = render('MemoryGPT.hbs', **data)

    messages = []
    messages.append({'role': 'system', 'content': prompt})

    memory = get_bot_memory(user_settings['user_id'])
    if memory is None:
        memory = []
        create_bot_memory(user_settings['user_id'])

    content = {
        'memory': json.dumps(memory),
        'interaction': {
            f'{user_settings["user_name"]}': user_message,
            f'{user_settings["bot_name"]}': bot_message,
        }
    }
    messages.append({'role': 'system', 'content': json.dumps(content)})

    memory_response = send(messages)
    if memory_response is None:
        logger.warn(f'memory response is None')
        return

    logger.debug(f'memory response: {memory_response}')
    pattern = r'\[(.*?)\]'

    match = re.search(pattern, memory_response)
    if match:
        result = eval(f'[{match.group(1)}]')
    
    update_result = update_bot_memory(user_settings['user_id'], {'memory': result})
    if update_result:
        logger.info(f'saved memories for {user_settings["user_id"]}')
    else:
        logger.error(f'error saving memories for {user_settings["user_id"]}')
        return
