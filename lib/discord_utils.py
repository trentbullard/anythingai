from dotenv import load_dotenv
import discord

from lib.logger import logger
from lib.es_utils import search_es, index_es, index_es_bot, parse_hits
from lib.chatgpt_utils import send, build_context
from lib.bot_utils import periodic_task
from lib.tts_utils import process_text

load_dotenv()


intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_client():
    return client


async def send_reply(user_message, bot_message):
    if user_message.channel.type == discord.ChannelType.private:
        channel = user_message.author.dm_channel or await user_message.author.create_dm()
    else:
        channel = user_message.channel

    try:
        await channel.send(bot_message)
    except Exception as e:
        logger.error(
            f'Error sending message to {user_message.author.display_name}: ', str(e))
        return


async def send_dm(channel, message):
    try:
        await channel.send(message)
        logger.debug(
            f'sent message to {channel.recipient.display_name}: {message}')
    except Exception as e:
        logger.error(
            f'Error sending message to {channel.recipient.display_name}: ', str(e))
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
