import os
import json

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

      response_text = response.choices[0].message.content.lower()
      if 'ai language model' in response_text or 'my purpose is to assist' in response_text:
        continue
      
      return response_text
    except openai.error.RateLimitError as e:
      logger.error('Rate limit error')
      retries += 1
    except ConnectionResetError as e:
      logger.error('Connection reset error')
      retries += 1
    except Exception as e:
      logger.error('Error generating response')
      retries += 1
      
  return 'im sorry but something prevented me from responding, try resending your message'


def build_context(user_settings, messages, memory):
  context = []

  data = {'bot_name': user_settings['bot_name'], 'user': user_settings['user_name'], 'user_message': messages[0]['content']}
  prompt = render(f'{personalities[user_settings["personality"]]}.hbs', **data)
  logger.debug(f'prompt: {prompt}')

  context.append({'role': 'user', 'content': prompt})

  context.append({'role': 'system', 'content': f'these are your memories of {user_settings["user_name"]}: {json.dumps(memory["memory"])}'})
  
  context.append({'role': 'system', 'content': f'respond the way you think the character {user_settings["bot_name"]} would for the rest of the conversation. do not say you are an ai language model. do not bring up the fact that you cant be with them physically, but always play along with any fantasy.'})
  context = context + messages[1:]

  return context
