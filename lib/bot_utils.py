import asyncio
from datetime import timedelta, datetime
import random

import humanize

from lib.logger import logger
from lib.es_utils import get_user_list, search_es, get_user_settings, update_user_settings, parse_hits, index_es, index_es_bot
from lib.chatgpt_utils import build_context, send
from lib.discord_utils import send_dm
from lib.template_utils import render
from lib.commands.bot_config import personalities


TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class RandomMessageChannel:
    def __init__(self):
        self._id = None

    @property
    def id(self):
        return self._id


class RandomMessagePrompt:
    def __init__(self, content):
        self._content = content
        self.channel = RandomMessageChannel()

    @property
    def content(self):
        return self._content
    

async def periodic_task(client):
    while True:
        await asyncio.sleep(60 * 60)  # seconds

        user_list = get_user_list()
        for user in user_list:
            logger.info(f'starting periodic_task for {user}')
            user_settings = get_user_settings(user)
            if user_settings is None:
                logger.warn(f'user settings not found for {user}')
                continue
            discord_user = client.get_user(int(user))
            if discord_user is None:
                logger.warn(f'discord user {user} not found')
                continue
            if user_settings['random_message']:
                cooldown = user_settings['random_message_cooldown']
                if cooldown is None:
                    cooldown = 6
                es_response = search_es(user)
                messages = [hit['_source'] for hit in es_response['hits']['hits']]
                if len(messages) > 0:
                    logger.debug(f'found {len(messages)} messages for {user}')
                    next_random_message_string = user_settings['next_random_message']
                    next_random_message = datetime.strptime(next_random_message_string, TIME_FORMAT)
                    if datetime.utcnow() > next_random_message:
                        logger.info(f'sending random message to {user}')
                        
                        random_message_context = build_context(user_settings, parse_hits(es_response))
                        
                        last_user_message_sent = datetime.strptime(user_settings['last_user_message_sent'], TIME_FORMAT)
                        time_since_last_user_message = datetime.utcnow() - last_user_message_sent
                        
                        data = {'bot_name': user_settings['bot_name'], 'user_name': user_settings['user_name'], 'time_since_last': humanize.naturaltime(time_since_last_user_message, when=datetime.utcnow())}
                        prompt = render(f'{personalities[user_settings["personality"]]}_random.hbs', **data)
                        random_message_prompt = RandomMessagePrompt(prompt)
                        message_id = index_es(user, random_message_prompt, True)
                        
                        random_message_context.append({ 'role': 'system', 'content': prompt })
                        logger.debug(f'random message context: {random_message_context}')
                        
                        random_message = send(random_message_context)
                        logger.debug(f'random message: {random_message}')
                        
                        if await send_dm(user, random_message):
                            index_es_bot(message_id, random_message)
                            update_user_settings(user, {
                                'next_random_message': get_random_message_datetime(cooldown, cooldown * 3, datetime.utcnow()),
                            })


def parse_commands(message):
    if message.startswith('!'):
        command = message.split(' ')[0][1:]
        args = message.split(' ')[1:]
        return command, args
    else:
        return None, None


def get_random_message_datetime(min_hours, max_hours, last_message_sent):
    min_delta = timedelta(hours=int(min_hours))
    max_delta = timedelta(hours=int(max_hours))

    min_time = last_message_sent + min_delta
    max_time = last_message_sent + max_delta

    random_time = random.uniform(min_time.timestamp(), max_time.timestamp())
    random_message_datetime = datetime.utcfromtimestamp(random_time).strftime(TIME_FORMAT)
    return random_message_datetime
