import os

from dotenv import load_dotenv
import openai

from lib.logger import logger
from lib.template_utils import render
from lib.commands.bot_config import personalities

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

MAX_RETRIES = 3

def send(messages):
  response = None
  retries = 0

  while retries < MAX_RETRIES:
    try:
      response = openai.ChatCompletion.create(
        model=os.getenv('OPENAI_MODEL'),
        messages=messages,
        temperature=0.9
      )
      
      return response.choices[0].message.content.lower()
    except Exception as e:
      logger.error('Error generating response: ', str(e))
      retries += 1
      
  return 'something went wrong, try resending your message'


def build_context(user_settings, messages):
  context = []

  data = {'bot_name': user_settings['bot_name'], 'user': user_settings['user_name'], 'user_message': messages[0]['content']}
  prompt = render(f'{personalities[user_settings["personality"]]}.hbs', **data)
  logger.debug(prompt)

  context.append({'role': 'user', 'content': prompt})
  context.append({'role': 'system', 'content': f'respond the way you think the character {user_settings["bot_name"]} would for the rest of the conversation. do not say you are an ai language model.'})
  context = context + messages[1:]

  return context
