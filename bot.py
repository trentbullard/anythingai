import os

from dotenv import load_dotenv
import discord
import json

from lib.logger import logger
from lib.es_utils import search_es, index_es, index_es_bot, parse_hits, get_user_settings
from lib.chatgpt_utils import send, build_context
from lib.discord_utils import get_client, send_reply
from lib.bot_utils import parse_commands

load_dotenv()


client = get_client()


# Load the bot commands from JSON
with open('bot_commands.json') as f:
    commands = json.load(f)


@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))
    # asyncio.ensure_future(periodic_task(send_dm, client.private_channels))


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    if message.channel.type not in [discord.ChannelType.private, discord.ChannelType.text]:
        return

    logger.info(f'({message.author.id}) {message.author.display_name}: {message.content}')
    user_settings = get_user_settings(message.author.id)
    logger.debug(f'User settings found for ({message.author.id}) {message.author.display_name}')
    if user_settings is None:
        user_settings = {
            'user_id': message.author.id,
            'user_name': message.author.display_name,
            'bot_name': 'FriendBot',
            'personality': 'standard',
            'randomcontact': False,
        }
    else:
        user_settings['user_id'] = message.author.id

    command_name, args = parse_commands(message.content)
    if command_name is not None:
        if command_name in commands:
            command_data = commands[command_name]
            module_name = command_data['module']
            function_name = command_data['function']
            help_text = command_data['help']

            if 'help' in args:
                await send_reply(message, help_text)
                return

            try:
                command_module = __import__(f'lib.commands.{module_name}', fromlist=[function_name])
                command_function = getattr(command_module, function_name)
                if command_data['async']:
                    command_response = await command_function(args, message, commands)
                else:
                    command_response = command_function(args, message, commands)

                await send_reply(message, command_response)
            except (ImportError, AttributeError) as e:
                logger.error(f'Error importing command {command_name}: ', e)
                await send_reply(message, f'Error importing command {command_name}')
            except Exception as e:
                logger.error(f'Error running command {command_name}: ', e)
                await send_reply(message, f'Error running command {command_name}')
        else:
            logger.warn(f'Command {command_name} not found')
            await send_reply(message, f'{command_name} is not a valid command')

        return

    messages = parse_hits(search_es(user_settings['user_id']))
    message_id = index_es(user_settings['user_id'], message)
    messages.append({'role': 'user', 'content': message.content})
    
    context = build_context(user_settings, messages)
    logger.debug(context)
    chatgpt_response = send(context)
    logger.debug(chatgpt_response)

    # audio_path = process_text(chatgpt_response, "en-US-Wavenet-H", "happy", user)
    # logger.debug(f"audio path: {audio_path}")
    # if audio_path:
    #   await send_tts(message, audio_path)

    await send_reply(message, chatgpt_response)

    index_es_bot(message_id, chatgpt_response)


client.run(os.getenv('DISCORD_BOT_TOKEN'))
