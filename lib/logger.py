import logging

logger = logging.getLogger('chatbot')
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler('logs/chatbot.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('[%(asctime)s] (%(levelname)s) - %(message)s'))
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('[%(asctime)s] (%(levelname)s) - %(message)s'))
logger.addHandler(console_handler)
