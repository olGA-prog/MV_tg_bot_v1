from telebot import types
from telebot.states.sync import context
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputMedia, \
    Update
from bot_setting import bot
from database import postgres



def products_handler():
    # –––––– COMMANDS ------

    # –––––– REGEXP ------
    bot.register_message_handler(send_products_to_user_message, regexp="🥩Товары")
    bot.register_message_handler(send_support_message, regexp="✉️Поддержка")
    # –––––– CALLBACKS ------
    bot.register_callback_query_handler(delete_message, lambda x: x.data.startswith('delete_message'))
    bot.register_callback_query_handler(send_products_by_types, lambda x: x.data.startswith('types_'))
    bot.register_callback_query_handler(send_products_by_types_from_category, lambda x: x.data.startswith('category_'))
    bot.register_callback_query_handler(send_products_to_user_message_edit, lambda x: x.data.startswith('back_to_category'))
    bot.register_callback_query_handler(send_products_to_user_message_edit1,lambda x: x.data.startswith('back_to_types'))
    bot.register_callback_query_handler(send_products_full_info, lambda x: x.data.startswith('product_'))
    bot.register_callback_query_handler(add_to_basket_callback, lambda x: x.data.startswith('add_to_basket_'))
    bot.register_callback_query_handler(confirm_add_to_basket, lambda x: x.data.startswith('confirm_add_'))





def send_products_to_user_message_edit(call):
    send_products_to_user_message(call, edit=True)


def send_products_to_user_message_edit1(call):
    send_products_by_types_from_category(call, edit=True)



def send_products_to_user_message(message, edit=False):

    categories = postgres.get_products_category()
    markup = InlineKeyboardMarkup()
    for category in categories:
        markup.add(InlineKeyboardButton(text=category["name"], callback_data=f'category_{category["name"]}'))
    markup.add(InlineKeyboardButton(text="Назад", callback_data='delete_message'))
    if not edit:
        try:
            with open(f'image/forAll/market1.jpg', 'rb') as img:
                bot.send_photo(message.from_user.id, img, "Выберите категорию товаров:",parse_mode='html',  reply_markup=markup)
        except Exception as e:
            print(str(e))
    else:
        bot.edit_message_reply_markup(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                      reply_markup=markup)




def send_products_by_types_from_category(call, edit=False):

    category = call.data[9:]
    products = postgres.get_products_type(category)
    category_current = postgres.get_products_category_by_name(category)
    types_name = set([item[0] for item in products])
    print(category_current)
    img_category = category_current[0]["img"]


    markup = InlineKeyboardMarkup()
    for types in types_name:
        markup.add(InlineKeyboardButton(text=f"{types}", callback_data=f'types_{types}'))
    markup.add(InlineKeyboardButton(text="Назад", callback_data='back_to_category'))

    if not edit:
        try:
            with open(f'image/category/{img_category}', 'rb') as img:
                bot.send_photo(call.from_user.id, img, f"Категория:<b>  {category_current[0]['name']}</b> \n\n<u><i>{category_current[0]['description']}</i></u> \n \nВыберите тип товара:", parse_mode='html',  reply_markup=markup)
        except Exception as e:
            print(str(e))
    else:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)




def send_products_by_types(call):

    type = call.data[6:]
    products = postgres.get_products_info_by_types(type)
    markup = InlineKeyboardMarkup()
    for item in products:
        print(item)
        markup.add(InlineKeyboardButton(text=f"Название: {item['name']}  Цена: {item['price']}.00 руб/{item['unit']}",  callback_data=f"product_{item['id']}"))
    markup.add(InlineKeyboardButton(text="Назад", callback_data="back_to_types"))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=markup)




def send_products_full_info(call):

    product_id = call.data[8:]
    product_info, unit_product = postgres.get_product_full_info(int(product_id))
    description = f"Название товара: <b>{product_info['name']}</b>\n\n\nЦена: <u>{product_info['price']}.00 руб/{unit_product}</u>\nКоличество товара в наличии: {product_info['count']}\nОписание товара: <i>{product_info['description']}</i> "
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_basket_{product_id}"))
    markup.add(InlineKeyboardButton(text="Назад", callback_data="back_to_product"))
    if product_info is None:
        description = "Нет описания товара"
    try:
        #with open(f'image/{product_info["img"]}.jpg', 'rb') as img:
        with open(f'image/product/1_1.jpg', 'rb') as img:
            media = InputMedia(type='photo', media=img)
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=media)
            bot.edit_message_caption(chat_id=call.message.chat.id, parse_mode='html',  message_id=call.message.message_id,
                                     caption=description)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)

    except Exception as e:
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=description)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)



user_states = {}
user_products = {}

def add_to_basket_callback(call):

    product_id = call.data[14:]
    user_states[call.from_user.id] = 'ask_quantity'
    user_products[call.from_user.id] = product_id

    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "Введите количество товара в килограммах, которое вы хотите добавить (минимальное количество: 1 кг):")
    bot.register_next_step_handler(call.message, ask_quantity)


def ask_quantity(message):

    product_id = user_products.get(message.from_user.id)
    product_info, unit_product = postgres.get_product_full_info(product_id)
    quantity = message.text

    if quantity.isdigit() and int(quantity) >= 1 and int(quantity)<= product_info["count"]:
        quantity = int(quantity)
        total_price = product_info['price'] * quantity
        confirmation_text = f"Вы хотите добавить {quantity} кг. товара - {product_info['name']}  на сумму {total_price}.00 руб. в корзину?\n\n"
        confirmation_markup = types.InlineKeyboardMarkup()
        confirmation_markup.add(
            types.InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_add_{product_id}_{quantity}"))
        confirmation_markup.add(
            types.InlineKeyboardButton(text="Отмена", callback_data="cancel_add"))

        bot.send_message(message.chat.id, confirmation_text, reply_markup=confirmation_markup)
        user_states[message.from_user.id] = 'confirmation'


    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное количество товаров (минимум 1 кг).")
        bot.register_next_step_handler(message, ask_quantity)



def confirm_add_to_basket(call):

    parts = call.data.split('_')
    product_id = parts[2]
    quantity = parts[3]
    quantity = int(quantity)
    user_id = call.from_user.id
    print(user_id)

    postgres.add_product_to_basket(user_id, product_id, quantity)
    bot.send_message(call.message.chat.id, "Товар добавлен в корзину!")



def cancel_add(call):
    global last_message_id
    bot.answer_callback_query(call.id)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Добавление товара отменено.")




def delete_message(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


def send_support_message(message):
    link = '[Написать менеджеру]()'
    bot.send_message(message.from_user.id, link, parse_mode='markdown')