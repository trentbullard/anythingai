import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] (%(levelname)s) - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

logger = logging.getLogger('chatbot')

handler = logging.FileHandler('logs/chatbot.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('[%(asctime)s] (%(levelname)s) - %(message)s'))
logger.addHandler(handler)
