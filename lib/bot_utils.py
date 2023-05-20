import asyncio

from lib.logger import logger
from lib.chatgpt_utils import send
from lib.es_utils import get_user_list, search_es


async def periodic_task(send_dm):
  while True:
    await asyncio.sleep(5) # seconds
    logger.info('starting periodic_task')


def parse_commands(message):
  if message.startswith('!'):
    command = message.split(' ')[0][1:]
    args = message.split(' ')[1:]
    return command, args
  else:
    return None, None
