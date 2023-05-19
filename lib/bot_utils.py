import asyncio
from datetime import datetime, timedelta
import random

import humanize

from lib.logger import logger
from lib.chatgpt_utils import send
from lib.es_utils import get_user_list, search_es


async def periodic_task(send_dm):
  while True:
    await asyncio.sleep(5) # seconds
    logger.info('starting periodic_task')

    users = get_user_list()
    for user in users:
      messages = search_es(user)
      if messages:
        last_message = messages['hits']['hits'][0]['_source']
        timestamp = datetime.fromisoformat(last_message['timestamp'])
        if timestamp < datetime.now() - timedelta(hours=random.randint(12, 24)):
          chatgpt_response = send([{ 'role': 'system', 'content': f'{user}s last message was {humanize.naturaltime(timestamp, datetime.now())}. what message would a girlfriend like mathilde send {user} to start a conversation?' }])
          logger.debug(f'chatbot random message: {chatgpt_response}')
          await send_dm(user, chatgpt_response)
          logger.debug(f'sent random message to {user}')


def parse_commands(message):
  if message.startswith('!'):
    command = message.split(' ')[0][1:]
    args = message.split(' ')[1:]
    return command, args
  else:
    return None, None
