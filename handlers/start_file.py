from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bot_setting import  bot
from database import postgres
import  os
from dotenv import load_dotenv
import json
load_dotenv()
ADMIN = json.loads(os.getenv('ADMIN'))

def start_file_handler():
    # –––––– COMMANDS ------
    bot.register_message_handler(welcome_message, commands=['start'])
    # –––––– REGEXP ------

    # –––––– CALLBACKS ------


def welcome_message(message):
    try:
        postgres.insert_user(message.from_user.id, message.from_user.username)

        bot.send_message(message.from_user.id, "Добро пожаловать в интернет-магазин 'МясоВкус'! "
                                               "Здесь вы можете увидеть весь ассортимент нашего магазина, а также заказать понравившиеся товары!"
                                                "Воспользуйтесь кнопками навигации! Удачных покупок!", reply_markup=main_keyboard(message))

    except Exception as e:
        print(str(e))


def main_keyboard(message):
    markup = ReplyKeyboardMarkup()
    markup.add(
        KeyboardButton(text="🥩Товары"),
        KeyboardButton(text="🛒Корзина"),
        KeyboardButton(text="🐰Личный кабинет"),
        KeyboardButton(text="✉️Поддержка"))
    if message.from_user.id in ADMIN:
        markup.add(KeyboardButton(text="✅Админ панель"))

    return markup