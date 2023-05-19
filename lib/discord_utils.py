import asyncio # usage commented out below
import os

from dotenv import load_dotenv
import discord

from lib.logger import logger
from lib.es_utils import search_es, index_es, index_es_bot, parse_hits
from lib.chatgpt_utils import send, build_context
from lib.bot_utils import periodic_task
from lib.tts_utils import process_text


intents = discord.Intents.default()
client = discord.Client(intents=intents)


def start_client():
  load_dotenv()
  client.run(os.getenv('DISCORD_BOT_TOKEN'))


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

  logger.info(f'{message.author.display_name}: {message.content}')
  user = message.author.display_name

  messages = parse_hits(search_es(user))
  id = index_es(user, message)
  messages.append({'role': 'user', 'content': message.content})
  
  context = build_context(user, messages)
  logger.debug(context)
  chatgpt_response = send(context)
  logger.debug(chatgpt_response)

  # audio_path = process_text(chatgpt_response, "en-US-Wavenet-H", "happy", user)
  # logger.debug(f"audio path: {audio_path}")
  # if audio_path:
  #   await send_tts(message, audio_path)

  await send_reply(message, chatgpt_response)

  index_es_bot(id, chatgpt_response)


async def send_reply(user_message, bot_message):
  if user_message.channel.type == discord.ChannelType.private:
    channel = user_message.author.dm_channel or await user_message.author.create_dm()
  else:
    channel = user_message.channel

  try:
    await channel.send(bot_message)
  except Exception as e:
    logger.error(f'Error sending message to {user_message.author.display_name}: ', str(e))
    return


async def send_dm(channel, message):
  try:
    await channel.send(message)
    logger.debug(f'sent message to {channel.recipient.display_name}: {message}')
  except Exception as e:
    logger.error(f'Error sending message to {channel.recipient.display_name}: ', str(e))
    return


async def send_tts(user_message, audio_path):
  guild = user_message.author.mutual_guilds[0]
  member = guild.get_member(user_message.author.id)
  
  if member.voice:
    channel = member.voice.channel
    voice_client = await channel.connect()

    # Play the TTS audio in the voice channel
    voice_client.play(discord.FFmpegPCMAudio(audio_path))
    await voice_client.disconnect()
  else:
    await user_message.channel.send("You are not connected to a voice channel.")
