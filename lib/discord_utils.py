from dotenv import load_dotenv
import discord

from lib.logger import logger

load_dotenv()


intents = discord.Intents.default()
intents.members = True
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
        return True
    except Exception as e:
        logger.error(
            f'Error sending message to {user_message.author.display_name}: ', str(e))
        return False


async def send_dm(user_id, message):
    await client.wait_until_ready()

    user = client.get_user(int(user_id))
    if user:
        await user.send(message)
        return True
    else:
        logger.warn(f'Failed to send dm - user {user_id} not found.')
        return False


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
