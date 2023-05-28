import os
from datetime import datetime
import json

from dotenv import load_dotenv
import humanize
from elasticsearch import Elasticsearch
from pydash import py_

from lib.logger import logger

load_dotenv()

es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_URL')])


def index_es(user_value, message_value, random_message=False):
    try:
        timestamp = f'{datetime.utcnow().isoformat()}Z'
        res = es.index(index='chatbot', body={'user': user_value, 'user_message': message_value.content,
                       'channel_id': message_value.channel.id, 'timestamp': timestamp, 'random_message': random_message}, id=f'{user_value}-{timestamp}')
    except Exception as e:
        logger.error(
            f'Error indexing message {message_value} from {user_value}: {str(e)}')
        return None

    id = res['_id']
    return id


def index_es_bot(id, bot_message):
    try:
        es.update(index='chatbot', id=id, body={
                  'doc': {'bot_message': bot_message}})
    except Exception as e:
        logger.error(f'Error updating {id} with {bot_message}: {str(e)}')


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
        logger.error(
            f'Error searching for messages from {user_value}: {str(e)}')
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
        logger.error(f'Error searching for users: {str(e)}')
        return []

    return py_.map_(results['aggregations']['users']['buckets'], 'key')


def get_user_settings(user_id):
    try:
        response = es.get(index='usersettings', id=user_id)
        if 'found' in response and response['found']:
            logger.debug(f'User settings found for {user_id}: {json.dumps(response["_source"], indent=2)}')
            return response['_source']
        else:
            logger.warn(f'User settings not found for {user_id}')
            return {}
    except Exception as e:
        logger.error(f'Error retrieving user settings for {user_id}: {str(e)}')
        return


def create_user_settings(user_id, user_settings):
    try:
        es.create(index='usersettings', id=user_id, body=user_settings)
        return True
    except Exception as e:
        logger.error(f'Error creating user settings for {user_id}: {str(e)}')
        return False


def update_user_settings(user_id, field_values):
    try:
        es.update(index='usersettings', id=user_id, body={'doc': field_values})
        return True
    except Exception as e:
        logger.error(
            f'Error updating the user settings for {user_id}: {str(e)}')
        return False


def get_bot_memory(user_id):
    try:
        response = es.get(index='botmemory', id=user_id)
        if 'found' in response and response['found']:
            return response['_source']
        else:
            logger.warn(f'Bot memory not found for {user_id}')
            return {}
    except Exception as e:
        logger.error(f'Error retrieving bot memory for {user_id}: {str(e)}')
        return
    

def create_bot_memory(user_id):
    try:
        es.create(index='botmemory', id=user_id, body={})
        return True
    except Exception as e:
        logger.error(f'Error creating bot memory for {user_id}: {str(e)}')
        return False
    

def update_bot_memory(user_id, field_values):
    try:
        es.update(index='botmemory', id=user_id, body={'doc': field_values})
        return True
    except Exception as e:
        logger.error(
            f'Error updating the bot memory for {user_id}: {str(e)}')
        return False


def parse_hits(response):
    hits = [hit['_source'] for hit in response['hits']['hits']]
    sorted_hits = py_.sort_by(hits, ['timestamp'])
    messages = []
    for i in range(len(sorted_hits)):
        timestamp = datetime.strptime(
            sorted_hits[i]['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        delta = humanize.naturaltime(timestamp, when=datetime.utcnow())
        role = 'system' if i == 0 or bool(sorted_hits[i]['random_message']) else 'user'
        messages.append({'role': role,
                        'content': f"({delta}) {sorted_hits[i]['user_message']}"})
        if 'bot_message' in sorted_hits[i]:
            messages.append(
                {'role': 'assistant', 'content': sorted_hits[i]['bot_message']})
    return messages
