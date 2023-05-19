import re

from lib.es_utils import get_user_settings, create_user_settings, update_user_settings


personalities = {
    "standard": "AnythingAI",
    "girlfriend": "GirlfriendAI",
}


def list_commands_command(_, message, commands):
    message = f'Available commands: {", ".join(commands.keys())}\n\nuse "!<command> help" for more information on a command'
    return message


def check_user_settings(user_id, display_name):
    user_settings = get_user_settings(user_id)
    if user_settings == None:
        create_user_settings(user_id, {"bot_name": None, "personality": None,
                             "user_name": None, "random_message": None, "random_message_cooldown": None, "display_name": display_name})
        user_settings = get_user_settings(user_id)
    return user_settings


def bot_name_command(args, message, _):
    user_id = message.author.id
    user_settings = check_user_settings(user_id, message.author.display_name)
    if len(args) == 0:
        if 'bot_name' not in user_settings or user_settings['bot_name'] == None:
            return f'you havent given me a name before. use the !botname command to tell me what you want to call me'
        else:
            return f'you currently call me {user_settings["bot_name"]}'
    elif validate_bot_name(args[0]):
        result = update_user_settings(user_id, {'bot_name': args[0]})
        if result:
            return f'ok, i will now respond to {args[0]}'
        else:
            return f'something went wrong while i was changing my name :('
    else:
        return f'im sorry but {args[0]} is not a valid name. make sure it is one word and only letters'


def my_name_command(args, message, _):
    user_id = message.author.id
    user_settings = check_user_settings(user_id, message.author.display_name)
    if len(args) == 0:
        if 'user_name' not in user_settings or user_settings['user_name'] == None:
            return f'you\'ve never told me what to call you before. use the !myname command to tell me what you want me to call you'
        else:
            return f'i currently call you {user_settings["user_name"]}'
    elif validate_user_name(args[0]):
        result = update_user_settings(user_id, {'user_name': args[0]})
        if result:
            return f'ok, i will now call you {args[0]}'
        else:
            return f'something went wrong while i was remembering your name :('
    else:
        return f'oh no :( {args[0]} is not a valid name'


def random_contact_command(args, message, _):
    if len(args) == 0:
        return f'if this command was implemented, i would tell you whether i am currently configured to send you random messages'
    elif args[0] == 'on':
        return f'if this command was implemented, i would start sending you random messages. use the randomcontactcooldown command to change how often i send you messages'
    elif args[0] == 'off':
        return f'if this command was implemented, i would stop sending you random messages'
    else:
        return f'i dont know what you mean by {args[0]}. i only understand "on" and "off" for this command'


def random_contact_cooldown_command(args, message, _):
    if len(args) == 0:
        return f'if this command was implemented, i would tell you the minimum number of hours i am currently waiting, after your last message, before i send you a random message'
    elif validate_cooldown(args[0]):
        return f'if this command was implemented, i would make sure to start waiting at least {args[0]} hours after your last message to send you a random message (assuming {args[0]} is a number)'
    else:
        return f'sorry, {args[0]} is too soon to send you a random message after your last message. i need to wait at least 6 hours'


def personality_command(args, message, _):
    if len(args) == 0:
        return f'if this command was implemented, i would send the name of my current personality and a list of the personalities i know how to be'
    elif args[0] in personalities.keys():
        return f'if this command was implemented, i would change my personality to {args[0]}'
    else:
        return f'im sorry, but im not familiar with the {args[0]} personality. i only know how to be {", ".join(personalities.keys())}'


def validate_bot_name(name):
    pattern = r'^[A-Za-z]+$'
    return bool(re.match(pattern, name))


def validate_user_name(name):
    pattern = r'^\S+$'
    return bool(re.match(pattern, name))


def validate_cooldown(value):
    if isinstance(value, (int, float)) and value > 6:
        return True
    else:
        return False
