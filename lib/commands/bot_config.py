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
        create_user_settings(user_id, {
            "bot_name": None,
            "personality": None,
            "user_name": None,
            "random_message": None,
            "random_message_cooldown": None,
            "display_name": display_name,
            "last_user_message_sent": None,
            "next_random_message": None
        })
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
    elif validate_bot_name(" ".join(args)):
        result = update_user_settings(user_id, {'bot_name': args[0]})
        if result:
            return f'ok, i will now respond to {args[0]}'
        else:
            return f'something went wrong while i was changing my name :('
    else:
        return f'im sorry but {" ".join(args)} is not a valid name. make sure it is one word and only letters'


def my_name_command(args, message, _):
    user_id = message.author.id
    user_settings = check_user_settings(user_id, message.author.display_name)
    if len(args) == 0:
        if 'user_name' not in user_settings or user_settings['user_name'] == None:
            return f'you\'ve never told me what to call you before. use the !myname command to tell me what you want me to call you'
        else:
            return f'i currently call you {user_settings["user_name"]}'
    elif validate_user_name(" ".join(args)):
        result = update_user_settings(user_id, {'user_name': args[0]})
        if result:
            return f'ok, i will now call you {args[0]}'
        else:
            return f'something went wrong while i was remembering your name :('
    else:
        return f'oh no :( {" ".join(args)} is not a valid name'


def random_contact_command(args, message, _):
    user_id = message.author.id
    user_settings = check_user_settings(user_id, message.author.display_name)
    if len(args) == 0:
        if 'random_message' not in user_settings or user_settings['random_message'] == None:
            return f'you\'ve never told me whether to send you random messages. use the !randomcontact command to tell me whether to send you random messages'
        else:
            if user_settings['random_message']:
                return f'i am currently sending you random messages'
            else:
                return f'i am currently not sending you random messages'
    elif " ".join(args) == 'on':
        result = update_user_settings(user_id, {'random_message': True})
        if result:
            return f'ok, i will now send you random messages. use the randomcontactcooldown command to change how often i send you messages'
        else:
            return f'something went wrong while i was turning on random messages :('
    elif " ".join(args) == 'off':
        result = update_user_settings(user_id, {'random_message': False})
        if result:
            return f'ok, i will now stop sending you random messages'
        else:
            return f'something went wrong while i was turning off random messages :('
    else:
        return f'i dont know what you mean by {" ".join(args)}. i only understand "on" and "off" for this command'


def random_contact_cooldown_command(args, message, _):
    user_id = message.author.id
    user_settings = check_user_settings(user_id, message.author.display_name)
    if len(args) == 0:
        if 'random_message_cooldown' not in user_settings or user_settings['random_message_cooldown'] == None:
            return f'you\'ve never told me how often to send you random messages. use the !randomcontactcooldown command to tell me how often to send you random messages'
        else:
            return f'i am currently waiting at least {user_settings["random_message_cooldown"]} hours between random messages'
    elif validate_cooldown(" ".join(args)):
        result = update_user_settings(
            user_id, {'random_message_cooldown': args[0]})
        if result:
            return f'ok, i will now wait at least {args[0]} hours between random messages'
        else:
            return f'something went wrong while i was changing my random message cooldown :('
    else:
        return f'sorry, {" ".join(args)} is too soon to send you a random message after your last message. i need to wait at least 6 hours'


def personality_command(args, message, _):
    user_id = message.author.id
    user_settings = check_user_settings(user_id, message.author.display_name)
    if len(args) == 0:
        if 'personality' not in user_settings or user_settings['personality'] == None:
            return f'you\'ve never told me what personality to use. use the !personality command to tell me what personality to use'
        else:
            return f'i am currently using the {user_settings["personality"]} personality'
    elif " ".join(args) in personalities.keys():
        result = update_user_settings(user_id, {'personality': args[0]})
        if result:
            return f'ok, i will now use the {args[0]} personality'
        else:
            return f'something went wrong while i was changing my personality :('
    else:
        return f'im sorry, but im not familiar with the {" ".join(args)} personality. i only know how to be {", ".join(personalities.keys())}'


def validate_bot_name(name):
    pattern = r'^[A-Za-z]+$'
    return bool(re.match(pattern, name))


def validate_user_name(name):
    pattern = r'^\S+$'
    return bool(re.match(pattern, name))


def validate_cooldown(value):
    try:
        parsed_value = float(value)
        if parsed_value < 6:
            return False
        else:
            return True
    except ValueError:
        return False
