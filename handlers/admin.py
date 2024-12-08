from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_setting import bot
from dotenv import load_dotenv
from database import postgres
import shutil
import os
import json

from database.postgres import get_all_products_category, get_all_products_types, save_product_type, \
    save_product_category

load_dotenv()
ADMIN = json.loads(os.getenv('ADMIN'))
print(ADMIN)



def admin_handler():
    # –––––– COMMANDS ------
    bot.register_message_handler(admin_message, commands=['admin'])
    # –––––– REGEXP ------
    bot.register_message_handler(admin_message, regexp="✅Админ панель")
    # –––––– CALLBACKS ------
    bot.register_callback_query_handler(send_bot_users, lambda x: x.data.startswith('send_bot_users'))
    bot.register_callback_query_handler(send_message_to_users, lambda x: x.data.startswith('send_message_to_users'))
    bot.register_callback_query_handler(cancel_sending_message, lambda x: x.data.startswith('cancel_message'))
    bot.register_callback_query_handler(add_product_in_db, lambda x: x.data.startswith('add_product_in_db'))
    bot.register_callback_query_handler(add_product_type_in_db, lambda x: x.data.startswith('add_product_type_in_db'))
    bot.register_callback_query_handler(add_category_in_db, lambda x: x.data.startswith('add_category_in_db'))


def admin_message(message):
    count = 10
    if message.from_user.id in ADMIN:
        caption = f"Это админская панель.\n\nКоличество пользователей бота: *{count}*"
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Пользователи бота", callback_data='send_bot_users'),
                   InlineKeyboardButton(text="Отправить сообщение", callback_data='send_message_to_users'),)

        markup.add(InlineKeyboardButton(text="Добавить товар", callback_data='add_product_in_db'),
                   InlineKeyboardButton(text="Добавить тип товара", callback_data='add_product_type_in_db'),)
        markup.add(InlineKeyboardButton(text="Добавить категорию товара", callback_data='add_category_in_db'))

        markup.add(InlineKeyboardButton(text="Назад", callback_data='delete_message'))
        bot.send_message(message.from_user.id, caption, reply_markup=markup, parse_mode='markdown')


def send_bot_users(call):
    if call.from_user.id in ADMIN:
        users = postgres.get_bot_users()
        print(users)
        caption = ''
        for user in users:
            user_str = ') '.join(map(str, user))
            caption += f'{user_str}\n'
        try:
            bot.send_message(call.from_user.id, caption)
        except Exception as e:
            bot.send_message(call.from_user.id, "Слишком большое количество людей для сообщения.")


def send_message_to_users(call):
    if call.from_user.id in ADMIN:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Отменить отправку", callback_data='cancel_message'))
        msg = bot.send_message(call.from_user.id, "Введите текст для отправки рассылки:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_message_for_users)


def process_message_for_users(message):
    if message.from_user.id in ADMIN:
        text_to_send = message.text
        users_id = postgres.get_bot_users()
        for user in users_id:
            bot.send_message(user[0], text_to_send)


def cancel_sending_message(call):
    if call.from_user.id in ADMIN:
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Отправка отменена!")


def add_product_in_db(call):
    if call.from_user.id in ADMIN:
        bot.send_message(call.from_user.id, "Введите имя товара:")
        bot.register_next_step_handler(call.message, process_product_name)


def process_product_name(message):
    product_name = message.text
    bot.send_message(message.from_user.id, "Введите описание товара:")
    bot.register_next_step_handler(message, process_product_description_tovar, product_name)


def process_product_description_tovar(message, product_name):
    product_description = message.text
    bot.send_message(message.from_user.id, "Введите цену товара:")
    bot.register_next_step_handler(message, process_product_price, product_name, product_description)


def process_product_price(message, product_name, product_description):
    try:
        product_price = float(message.text)  # Конвертируем строку в число с плавающей точкой
        bot.send_message(message.from_user.id, "Введите количество товара:")
        bot.register_next_step_handler(message, process_product_quantity, product_name, product_description,
                                       product_price)
    except ValueError:
        bot.send_message(message.from_user.id, "Ошибка: Введите корректную цену товара:")
        bot.register_next_step_handler(message, process_product_price, product_name, product_description)


def process_product_quantity(message, product_name, product_description, product_price):
    try:
        product_quantity = int(message.text)

        product_types = postgres.get_all_products_types()
        types_message = "Напишите id типа товара:\n" + "\n".join([f"{pt[0]}. {pt[1]} (id: {pt[0]})" for pt in product_types])
        bot.send_message(message.from_user.id, types_message)
        bot.register_next_step_handler(message, process_product_type, product_name, product_description, product_price,
                                       product_quantity)

    except ValueError:
        bot.send_message(message.from_user.id, "Ошибка: Введите корректное количество товара:")
        bot.register_next_step_handler(message, process_product_quantity, product_name, product_description,
                                       product_price)


def process_product_type(message, product_name, product_description, product_price, product_quantity):
    try:
        product_type_id = int(message.text)
        print(product_type_id)

        # Запрашиваем категорию товара
        product_categories = get_all_products_category()  # Функция должна возвращать список категорий товара
        categories_message = "Напишите id категории товара:\n" + "\n".join([f"{pt[0]}. {pt[1]} (id: {pt[0]})" for pt in product_categories])
        bot.send_message(message.from_user.id, categories_message)
        bot.register_next_step_handler(message, process_product_category, product_name, product_description,
                                       product_price, product_quantity, product_type_id)

    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, "Ошибка: Выберите корректный тип товара:")
        bot.register_next_step_handler(message, process_product_type, product_name, product_description, product_price,
                                       product_quantity)


def process_product_category(message, product_name, product_description, product_price, product_quantity, product_type):
    try:
        product_category_id = int(message.text)

        # Запрашиваем изображение
        bot.send_message(message.from_user.id, "Пожалуйста, отправьте изображение товара:")
        bot.register_next_step_handler(message, process_product_image, product_name, product_description,
                                       product_price, product_quantity, product_type, product_category_id)

    except (ValueError, IndexError):
        bot.send_message(message.from_user.id, "Ошибка: Выберите корректную категорию товара:")
        bot.register_next_step_handler(message, process_product_category, product_name, product_description,
                                       product_price, product_quantity, product_type)


def process_product_image(message, product_name, product_description, product_price, product_quantity, product_type,
                          product_category):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name1 = file_info.file_path.split('/')[-1]
        file_name, _ = os.path.splitext(file_name1)
        downloaded_file = bot.download_file(file_info.file_path)
        project_root = os.path.dirname(os.path.abspath(__file__))
        images_folder = os.path.join(project_root, '..', 'image', 'product')
        image_path = os.path.join(images_folder, file_name1)
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        print(file_name)
        prod_id = postgres.get_count_product() + 1
        res = postgres.save_product_to_db(product_name, product_description, product_price, product_quantity,
                                          product_type, product_category, file_name)
        bot.send_message(message.from_user.id, res)

    else:
        bot.send_message(message.from_user.id, "Ошибка: Пожалуйста, отправьте изображение в формате документа.")
        bot.register_next_step_handler(message, process_product_image, product_name, product_description,
                                       product_price, product_quantity, product_type, product_category)




def add_product_type_in_db(call):
    if call.from_user.id in ADMIN:
        bot.send_message(call.from_user.id, "Введите название новый тип товара:")
        bot.register_next_step_handler(call.message, process_product_type1)

def process_product_type1(message):
    product_type_name = message.text
    id_type = postgres.get_count_type() + 1
    res = save_product_type(product_type_name, 'кг')
    bot.send_message(message.from_user.id, res)




def add_category_in_db(call):
    if call.from_user.id in ADMIN:
        bot.send_message(call.from_user.id, "Введите название новой категории товара:")
        bot.register_next_step_handler(call.message, process_product_category_name)


def process_product_category_name(message):
    product_type_name = message.text
    bot.send_message(message.from_user.id, "Теперь, пожалуйста, отправьте изображение для новой категории товара:")
    bot.register_next_step_handler(message, process_product_image_category, product_type_name)


def process_product_image_category(message, product_type_name):
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name1 = file_info.file_path.split('/')[-1]
        file_name, _ = os.path.splitext(file_name1)

        downloaded_file = bot.download_file(file_info.file_path)

        project_root = os.path.dirname(os.path.abspath(__file__))
        categories_folder = os.path.join(project_root, '..', 'image', 'category')
        image_path = os.path.join(categories_folder, file_name1)

        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        print(file_name)


        bot.send_message(message.from_user.id, "Введите описание для новой категории:")
        bot.register_next_step_handler(message, process_product_description, product_type_name, file_name)
    else:
        bot.send_message(message.from_user.id, "Ошибка: Пожалуйста, отправьте изображение в формате фотоснимка.")
        bot.register_next_step_handler(message, process_product_image_category, product_type_name)


def process_product_description(message, product_type_name, file_name):
    category_description = message.text
    res = save_product_category(product_type_name, file_name, category_description)
    bot.send_message(message.from_user.id, res)




