from os import environ
import telebot
from flask import Flask, request
import config
import replies

bot = telebot.TeleBot(config.TOKEN)
server = Flask(__name__)

min_channel_size = 0  # variable globale

@server.route('/' + config.TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='NOM_DE_TON_APPLICATION_HEROKU' + config.TOKEN)
    return "!", 200

def write_results(channel):
    """ Écrit les noms des chaînes dans un fichier """
    with open('base.txt', 'a') as list:
        list.write("{} \n".format(channel))

def is_admin(message):
    """ Vérifie si un utilisateur est dans la liste des administrateurs (c'est-à-dire mon ID) """
    return (message.from_user.id in config.CHAT_ID) or (message.chat.id in config.CHAT_ID)

def is_length(message):
    """ Vérifie si le message a une longueur définie """
    return len(message) <= 25

def is_channel(message):
    """ Vérifie si le message correspond à un nom de chaîne """
    try:
        # Comme l'argument 'message' est passé sous forme de chaîne sans le @,
        # on ajoute ce signe avec .format()
        name_or_not = bot.get_chat("@{}".format(message)).type
    except Exception:
        return False
    return name_or_not == "channel"

def channel_is_size(channel):
    """ Vérifie si une chaîne atteint une taille minimale définie (voir : gestionnaire /setsize) """
    channel_number = bot.get_chat_members_count(channel)
    return channel_number >= min_channel_size

def gen_response(channel, description, message_words):
    """ Génère une réponse après ajout d'une chaîne """
    if not channel:
        return replies.enter_addmessage_error

    if not description:
        return replies.enter_desc_error

    if description[0] != '-':
        return replies.enter_addmessage_error

    if not (is_channel(channel) and is_length(description)):
        return replies.enter_chan

    if not channel_is_size(channel):
        return replies.small_chan.format(min_channel_size)

    write_results(' '.join(message_words[1:]))
    return replies.success_add.format(channel)

@bot.message_handler(commands=['setsize'])
def set_size(message):
    """ Définit la taille minimale requise pour les chaînes """
    global min_channel_size
    temp_min_channel_size = ' '.join(message.text.split()[1:])

    if is_admin(message) and temp_min_channel_size:
        min_channel_size = int(temp_min_channel_size)
        bot.reply_to(message, replies.size_set.format(min_channel_size))
    elif not temp_min_channel_size:
        bot.reply_to(message, replies.size_set_error)
    else:
        bot.reply_to(message, replies.admin_only)

@bot.message_handler(commands=['start'])
def send_start(message):
    """ Envoie le message de démarrage """
    bot.reply_to(message, replies.start_reply, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def send_help(message):
    """ Envoie le message d'aide """
    bot.reply_to(message, replies.help_reply, parse_mode='HTML')

@bot.message_handler(commands=['add'])
def start_message(message):
    """ Ajoute des chaînes au document base.txt """
    message_words = message.text.split()
    channel = ' '.join(message_words[1:2])
    description = ' '.join(message_words[2:])
    bot.reply_to(message, gen_response(channel, description, message_words))

@bot.message_handler(commands=['list'])
def show_list(message):
    """ Envoie le contenu du fichier base.txt sous forme de message Telegram """
    if is_admin(message):
        with open('base.txt', 'r') as list:
            ready_list = list.read()  # Stocke le contenu du fichier dans une variable
            bot.reply_to(message, ready_list if ready_list else replies.no_chans)
    else:
        bot.reply_to(message, replies.admin_only)

@bot.message_handler(commands=['clear'])
def clear_list(message):
    """ Vide le fichier base.txt """
    if is_admin(message):
        with open('base.txt', 'w') as list:
            list.seek(0)  # Va au début du fichier pour le vider
            list.truncate()
        bot.reply_to(message, replies.trunc_list)
    else:
        bot.reply_to(message, replies.admin_only)

# @bot.message_handler(commands=['ban'])
# def ban_user(message):
#     """ Bannit des utilisateurs """
#     user_id = message.reply_to_message.from_user.id
#     username = message.reply_to_message.from_user.username
#     if is_admin(message):
#         bot.kick_chat_member(chat_id=message.chat.id, user_id=message.from_user.id, until_date=1)
#         bot.reply_to(message, replies.ban_member.format(username))
#     else:
#         bot.reply_to(replies.admin_only)

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
