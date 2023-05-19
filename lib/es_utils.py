import os
from datetime import datetime

from dotenv import load_dotenv
import humanize
from elasticsearch import Elasticsearch
from pydash import py_

from lib.logger import logger

load_dotenv()

es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_URL')])

def index_es(user_value, message_value):
  try:
    res = es.index(index='chatbot', body={'user': user_value, 'user_message': message_value.content, 'channel_id': message_value.channel.id, 'timestamp': datetime.now().isoformat()}, id=f'{user_value}-{datetime.now().isoformat()}')
  except Exception as e:
    logger.error(f'Error indexing message {message_value.content} from {user_value}: ', str(e))
    return None

  id = res['_id']
  return id

def index_es_bot(id, bot_message):
  try:
    es.update(index='chatbot', id=id, body={'doc': {'bot_message': bot_message}})
  except Exception as e:
    logger.error(f'Error updating {id} with {bot_message}: ', str(e))
  
def search_es(user_value):
  query = {
    "query": {
      "bool": {
        "must": [
          {
            "match": {
              "user": user_value
            }
          },
          {
            "exists": {
              "field": "user_message"
            }
          }
        ]
      }
    },
    "sort": [
      {
        "timestamp": {
          "order": "desc"
        }
      }
    ],
    "size": 5
  }

  try:
    results = es.search(index='chatbot', body=query)
  except Exception as e:
    logger.error(f'Error searching for messages from {user_value}: ', str(e))
    return []

  return results

def get_user_list():
  users_query = {
    "aggs": {
      "users": {
        "terms": {
          "field": "user.keyword",
          "size": 10000
        }
      }
    },
    "query": {
      "exists": {
        "field": "user_message"
      }
    },
    "size": 0
  }

  try:
    results = es.search(index='chatbot', body=users_query)
  except Exception as e:
    logger.error('Error searching for users: ', str(e))
    return []
  
  return py_.map_(results['aggregations']['users']['buckets'], 'key')

def parse_hits(response):
  hits = [hit['_source'] for hit in response['hits']['hits']]
  sorted_hits = py_.sort_by(hits, ['timestamp'])
  messages = []
  for i in range(len(sorted_hits)):
    timestamp = datetime.fromisoformat(sorted_hits[i]['timestamp'])
    delta = humanize.naturaltime(timestamp, datetime.now())
    messages.append({'role': 'system' if i == 0 else 'user', 'content': f"({delta}) {sorted_hits[i]['user_message']}"})
    if 'bot_message' in sorted_hits[i]:
      messages.append({'role': 'assistant', 'content': sorted_hits[i]['bot_message']})
  return messages
