import telebot
from telebot.apihelper import ApiTelegramException
import traceback
from threading import Thread

# temp: ------------------------
from rich.console import Console
console = Console()
log = console.log
#-------------------------------

bot = telebot.TeleBot("5752551076:AAFPXorMvZ4QnNqYbR9GoEkuctJyAizCGzE")
users_join_data = {} # { user_id: {chat_id: is_joined_or_not} }
all_chat_ids = ["-1001693174398"]
all_admin_ids = ["5412438166"] # unusable, for now!

def check_joins():
    for user_id in users_join_data:
        for chat_id in users_join_data[user_id]:
            if users_join_data[user_id][chat_id]:
                users_join_data[user_id][chat_id] = is_joined(chat_id, user_id)

def thread_function():
    while 1:
        sleep(10)
        log("thread loop")
        check_joins()

checker = Thread(target = thread_function)

def is_joined(chat_id, user_id):
    log("check for", chat_id, user_id)
    try:
        res = bot.get_chat_member(chat_id, user_id)
        log("result: ", res.status, "from", res)
        return True if res.status != 'left' else False
    except ApiTelegramException as e:
        if e.result_json['description'] == 'Bad Request: user not found':
            return False
        else:
            print(traceback.format_exc())
            raise e

@bot.message_handler(commands = ['start'])
def command_start(message):
    log("/start")
    log("globals:", globals())
    user_id = message.from_user.id
    log("user id =", user_id)
    log("chat id =", message.chat.id)
    log("chat type =", message.chat.type)
    if not user_id in users_join_data or not all(users_join_data[user_id].values()):
        users_join_data[user_id] = {
            chat_id: is_joined(chat_id, user_id)
            for chat_id in all_chat_ids
        }
        log("new users_join_data[user_id] =", users_join_data[user_id])
        if all(users_join_data[user_id].values()):
            user_is_joined = True
        else:
            user_is_joined = False
    else:
        log("all joined users_join_data[user_id] =", users_join_data[user_id])
        user_is_joined = True
    
    if user_is_joined:
        log("False for", user_id, users_join_data[user_id])
        bot.send_message(
            message.chat.id,
            "hello:)"
        )
    else:
        log("True for", user_id, users_join_data[user_id])
        markup = telebot.types.InlineKeyboardMarkup(row_width = 1)
        markup.add(
            telebot.types.InlineKeyboardButton("➡️Katıldım⬅️", callback_data="/start")
        )
        bot.send_message(
            message.chat.id,
            "**🔮Kanala Katılman Gerek**\nhttps://t.me/ZehirHack2",
            reply_markup = markup
        )    

checker.start() # move it to the end of your process
bot.polling()
