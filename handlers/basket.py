import os
import re
import threading
import time
from datetime import datetime
from gc import callbacks
from plistlib import loads

from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputMedia, \
    Update, LabeledPrice
from telegram._utils import markup

from bot_setting import bot
from database import postgres
from dotenv import load_dotenv





def basket_handler():
    # –––––– COMMANDS ------

    # –––––– REGEXP ------
    bot.register_message_handler(send_products_basket, regexp="🛒Корзина")
    bot.register_message_handler(send_profile_info, regexp="🐰Личный кабинет")

    # –––––– CALLBACKS ------
    bot.register_callback_query_handler(send_to_user_products, lambda x: x.data.startswith('send_users_product_all'))
    bot.register_callback_query_handler(send_list_delete_product_to_basket, lambda x: x.data.startswith('delete_product_to_basket'))
    bot.register_callback_query_handler(delete_product_to_basket, lambda x: x.data.startswith('prod_delete_'))
    bot.register_callback_query_handler(back_to_my_product_from_delete,lambda x: x.data.startswith('return_my_product'))
    bot.register_callback_query_handler(delete_all_product_from_basket,lambda x: x.data.startswith('delete_product_all'))
    bot.register_callback_query_handler(send_list_product_edit_to_basket,lambda x: x.data.startswith('edit_count_product_to_basket'))
    bot.register_callback_query_handler(edit_product_to_basket,lambda x: x.data.startswith('ed_product_count_'))
    bot.register_callback_query_handler(delete_message2,lambda x: x.data.startswith('delete_message_chat'))
    bot.register_callback_query_handler(send_message_change_name,lambda x: x.data.startswith('send_edit_message_name'))
    bot.register_callback_query_handler(send_edit_message_adress,lambda x: x.data.startswith('send_edit_message_adress'))
    bot.register_callback_query_handler(send_edit_message_phone_number,lambda x: x.data.startswith('send_edit_message_phone_number'))
    bot.register_callback_query_handler(send_profile_info,lambda x: x.data.startswith('return_profile_info'))
    bot.register_callback_query_handler(add_order_prepare,lambda x: x.data.startswith('order_add'))
    bot.register_callback_query_handler(confirm_order,lambda x: x.data.startswith('order_done_'))
    bot.register_callback_query_handler(handle_payment,lambda x: x.data.startswith('pay_order_'))



def delete_message2(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

def back_to_my_product_from_delete(call):
    send_to_user_products(call, edit=True)

def send_products_basket(message):
    caption = f"Это ваша корзина с товарам. Вы можете её редактировать: любой товар можно удалить, либо поменять его количество! Также здесь вы можете оформить заказ, нажав кнопку 'Оформить заказ'"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Мои товары", callback_data='send_users_product_all'))
    bot.send_message(message.from_user.id, caption, reply_markup=markup, parse_mode='markdown')

def send_to_user_products(call, edit=True):
    fullprice = 0
    caption = ""
    user_id = call.from_user.id
    products_and_count = postgres.get_products_to_basket_user(user_id)
    if products_and_count:
        markup = InlineKeyboardMarkup()
        for item in products_and_count:
            count = item["count_product"]
            product_info, unit = postgres.get_product_full_info(item["products_id"])
            caption += f"Название товара: {product_info["name"]}  \nЦена за {unit}. : {product_info["price"]}.00 руб.  \nВыбранное количество: {count} {unit}. \nОбщая стоимость за товар: {int(count)* int(product_info["price"])}.00 руб.\n\n\n\n"
            fullprice += int(count)* int(product_info["price"])
            markup.add(InlineKeyboardButton(text=f" {product_info["name"]}  {int(count)* int(product_info["price"])}.00 руб." , callback_data=f'product_{item["products_id"]}'))
        markup.add(InlineKeyboardButton(text="Удалить товары", callback_data='delete_product_to_basket'),
                   InlineKeyboardButton(text="Изменить количество", callback_data='edit_count_product_to_basket'), )
        markup.add(InlineKeyboardButton(text="Оформить заказ", callback_data='order_add'))
        bot.send_message(call.from_user.id, caption + f"Общая стоимость (за все товары):  {fullprice}.00 руб. \n\nВы можете подробнее узнать о выбранных товарах, нажав соответствующую кнопку!", reply_markup=markup, parse_mode='markdown')
    else:
        caption = "Ваша корзина пуста!\n Нажмите на кнопку 'Товары', чтобы ознакомиться с каталогом!"
        bot.send_message(call.from_user.id, caption ,  parse_mode='markdown')


def send_list_delete_product_to_basket(call):
    markup = InlineKeyboardMarkup()
    user_id = call.from_user.id
    products_and_count = postgres.get_products_to_basket_user(user_id)
    for item in products_and_count:
        product_id = item["products_id"]
        count = item["count_product"]
        product_info, unit = postgres.get_product_full_info(product_id)
        print(f" item_id {item["products_id"]}")
        markup.add(
            InlineKeyboardButton(text=f" {product_info["name"]}  {int(count) * int(product_info["price"])}.00 руб.",
                                 callback_data=f'prod_delete_{item["products_id"]}'))
    markup.add(InlineKeyboardButton(text="Удалить все товары", callback_data='delete_product_all'))
    markup.add(InlineKeyboardButton(text="Назад", callback_data='return_my_product'))
    bot.send_message(call.from_user.id, "Выберите товар, который хотите удалить:", reply_markup=markup, parse_mode='markdown')

def delete_product_to_basket(call):
    product_id = call.data[12:]
    print(f" item {product_id}")
    user_id = call.from_user.id
    result_message= postgres.delete_product_basket(user_id, int(product_id))
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Вернуться к товарам", callback_data='return_my_product'))
    bot.send_message(call.from_user.id, result_message,  reply_markup=markup, parse_mode='markdown' )

def delete_all_product_from_basket(call):
    user_id = call.from_user.id
    result_message = postgres.delete_all_users_product_basket(user_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Вернуться к товарам", callback_data='return_my_product'))
    bot.send_message(call.from_user.id, result_message, reply_markup=markup, parse_mode='markdown')

def send_list_product_edit_to_basket(call):
    markup = InlineKeyboardMarkup()
    user_id = call.from_user.id
    products_and_count = postgres.get_products_to_basket_user(user_id)
    for item in products_and_count:
        product_id = item["products_id"]
        count = item["count_product"]
        product_info, unit = postgres.get_product_full_info(product_id)
        markup.add(
            InlineKeyboardButton(text=f" {product_info["name"]} Выбранное количество: {int(count)}  {int(count) * int(product_info["price"])}.00 руб.",
                                 callback_data=f'ed_product_count_{item["products_id"]}'))
    markup.add(InlineKeyboardButton(text="Назад", callback_data='return_my_product'))
    bot.send_message(call.from_user.id, "Выберите товар, который хотите изменить:", reply_markup=markup,
                     parse_mode='markdown')

def edit_product_to_basket(call):
    product_id = call.data[17:]

    bot.send_message(call.from_user.id, "Введите новое количество в килограммах (минимальное количество от 1 кг):")
    bot.register_next_step_handler(call.message, save_new_count_product, product_id)

def save_new_count_product(message, product_id):
    product_info, unit = postgres.get_product_full_info(product_id)
    quantity = int(message.text)
    user_id = message.from_user.id
    if  quantity >= 1 and quantity<= int(product_info["count"]):
        result_message = postgres.edit_count_product(user_id, int(product_id), quantity)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Вернуться к товарам", callback_data='return_my_product'))
        bot.send_message(message.from_user.id, result_message, reply_markup=markup, parse_mode='markdown')
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное количество товаров (минимум 1 кг).")
        bot.register_next_step_handler(message, save_new_count_product)

def send_profile_info(message):
    user_id = message.from_user.id
    user_info = postgres.get_full_user_info(user_id)
    print(user_info )
    adress_user = 'Адрес не указан'
    phone_number_user = 'Номер телефона не указан'
    if user_info["adress"] is not None:
        adress_user = user_info["adress"]
    if user_info['phone_number'] is not None:
        phone_number_user = user_info['phone_number']
    caption = f"Это ваш личный кабинет. \nЗдесь показана информация о вас, которую вы можете редактировать!\n\n\nНа данный момент ваши данные такие:\n\n"
    caption_info = f"Имя: <b>{user_info["name"]}</b> \nАдрес: <b>{adress_user}</b> \nНомер телефона: <b>{phone_number_user}</b>\n"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Изменить имя", callback_data='send_edit_message_name'),
               InlineKeyboardButton(text="Изменить адрес", callback_data='send_edit_message_adress'))
    markup.add(InlineKeyboardButton(text="Изменить телефонные номер", callback_data='send_edit_message_phone_number'))
    bot.send_message(message.from_user.id, caption + caption_info, reply_markup=markup, parse_mode='html')

def send_message_change_name(call):
    bot.send_message(call.from_user.id, "Введите новое имя:")
    bot.register_next_step_handler(call.message, save_edit_user_name)

def save_edit_user_name(message):
    user_id = message.from_user.id
    new_name_user = message.text
    result_message = postgres.edit_name_user(user_id, new_name_user)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Вернуться в личный кабинет", callback_data='return_profile_info'))
    bot.send_message(message.from_user.id, result_message, reply_markup=markup, parse_mode='markdown')

def send_edit_message_adress(call):
    bot.send_message(call.from_user.id, "Введите новый адрес:")
    bot.register_next_step_handler(call.message, send_message_change_adress)

def send_message_change_adress(message):
    user_id = message.from_user.id
    new_name_adress = message.text
    result_message = postgres.edit_adress_user(user_id, new_name_adress)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Вернуться в личный кабинет", callback_data='return_profile_info'))
    bot.send_message(message.from_user.id, result_message, reply_markup=markup, parse_mode='markdown')


def send_edit_message_phone_number(call):
    bot.send_message(call.from_user.id, "Введите новый номер телефона:")
    bot.register_next_step_handler(call.message, send_message_change_phone_number)


def send_message_change_phone_number(message):
    user_id = message.from_user.id
    new_phone_number = message.text.strip()

    phone_pattern = re.compile(r'^(?:\+7|8)(?:\s|\(?)(\d{3})(?:\)?(\s|-)?)(\d{3})(?:\2)(\d{2})(?:\2)(\d{2})$|^(?:\+7|8)\d{10}$')
    markup = InlineKeyboardMarkup()
    if phone_pattern.match(new_phone_number):
        result_message = postgres.edit_phone_number(user_id, new_phone_number)
        markup.add(InlineKeyboardButton(text="Вернуться в личный кабинет", callback_data='return_profile_info'))
        bot.send_message(message.from_user.id, result_message, reply_markup=markup, parse_mode='markdown')
    else:
        markup.add(InlineKeyboardButton(text="Вернуться в личный кабинет", callback_data='return_profile_info'))
        bot.send_message(message.from_user.id, "Пожалуйста, введите корректный номер телефона.\n"
                                                 "Формат: +7 (999) 999-99-99, +79999999999 или 89999999999.", reply_markup=markup)



def add_order_prepare(call):
    user_id = call.from_user.id
    user_info = postgres.get_full_user_info(user_id)


    missing_info = []
    if user_info["adress"] is None:
        missing_info.append("адрес")
    if user_info["phone_number"] is None:
        missing_info.append("номер телефона")


    if missing_info:
        missing_info_str = ", ".join(missing_info)
        bot.send_message(user_id, f"Пожалуйста, укажите {missing_info_str}.")
        bot.register_next_step_handler(call.message, update_user_info, missing_info)
    else:

        show_user_and_cart_info(call)


def update_user_info(message, missing_info):
    user_id = message.from_user.id

    if "адрес" in missing_info and message.text:
        postgres.edit_adress_user(user_id, message.text)
        bot.send_message(user_id, "Адрес обновлён.")
        missing_info.remove("адрес")
    elif "номер телефона" in missing_info and message.text:
        postgres.edit_phone_number(user_id, message.text)
        bot.send_message(user_id, "Номер телефона обновлён.")
        missing_info.remove("номер телефона")


    if missing_info:
        if "адрес" in missing_info:
            bot.send_message(user_id, "Пожалуйста, укажите адрес.")
            bot.register_next_step_handler(message, update_user_info, missing_info)
        elif "номер телефона" in missing_info:
            bot.send_message(user_id, "Пожалуйста, укажите номер телефона.")
            bot.register_next_step_handler(message, update_user_info, missing_info)
    else:
        show_user_and_cart_info(message)


def show_user_and_cart_info(message):
    fullprice = 0
    caption = ""
    user_id = message.from_user.id
    basket_id = postgres.get_basket_id_by_user_id(user_id)
    user_info = postgres.get_full_user_info(user_id)
    products_and_count = postgres.get_products_to_basket_user(user_id)
    markup = InlineKeyboardMarkup()
    if products_and_count:
        caption_user = ""
        for item in products_and_count:
            count = item["count_product"]
            product_info, unit = postgres.get_product_full_info(item["products_id"])
            caption += f"Название товара: {product_info["name"]}  \nЦена за {unit}. : {product_info["price"]}.00 руб.  \nВыбранное количество: {count} {unit}. \nОбщая стоимость за товар: {int(count) * int(product_info["price"])}.00 руб.\n\n\n\n"
            fullprice += int(count) * int(product_info["price"])
        caption_user = f"Информация о пользователе:\n\nИмя: <b>{user_info["name"]}</b> \nАдрес: <b>{user_info["adress"]}</b> \nНомер телефона: <b>{user_info["phone_number"]}</b>\n\n\n"
        markup.add(InlineKeyboardButton(text="Подтвердить", callback_data=f"order_done_{fullprice}_{basket_id}"))
        markup.add(InlineKeyboardButton(text="Отменить оформление", callback_data='return_my_product'))
        bot.send_message(message.from_user.id,
                         caption_user + caption + f"Общая стоимость (за все товары):  <b>{fullprice}.00 руб.</b> \n\n",
                         reply_markup=markup, parse_mode='html')


def confirm_order(call):
    user_id = call.from_user.id
    date_order = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = call.data.split("_")
    fullprice = parts[2]
    basket_id = parts[3]
    status = "Создан"

    order_id, message = postgres.create_order_for_user(user_id, basket_id, date_order, fullprice, status)
    print(order_id, "  ", message)

    if message == "Заказ создан!":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="Оплатить заказ", callback_data=f'pay_order_{order_id}_{fullprice}'))
        bot.send_message(user_id, "Заказ создан! Оплатите его, нажав кнопку:", reply_markup=markup)

        threading.Thread(target=check_order_status, args=(order_id, user_id), daemon=True).start()
    else:
        bot.send_message(user_id, "Произошла ошибка при создании заказа. Пожалуйста, попробуйте снова.")

def check_order_status(order_id, user_id):
    while True:
        order_info = postgres.get_order_status(order_id)
        if order_info and order_info == 'Оплачен':
            bot.send_message(user_id, "Ваш заказ успешно оплачен! Спасибо за покупку!🍖❤️🍖")
            break
        time.sleep(10)


def handle_payment(call):
    load_dotenv()
    TOKEN_TEST =  os.getenv('TOKEN_YOOKASSA_TEST')
    parts = call.data.split("_")
    order_id = parts[2]
    fullprice = float(parts[3])
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    title = f"Заказ #{order_id}"
    description = "Товары мясного магазина 🥩МясоВкус. Приятного аппетита!"
    invoice_payload = f"order_{order_id}"
    currency = "RUB"
    prices = [LabeledPrice("Заказ", int(1000 * 100))]  # Цена в копейках

    # Отправка счета на оплату
    bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        invoice_payload=invoice_payload,
        provider_token=TOKEN_TEST,
        prices=prices,
        currency=currency,
        is_flexible=False
    )

    bot.answer_callback_query(call.id, "Счет на оплату отправлен.")

@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout_query_handler(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment_handler(message):
    order_id = message.successful_payment.invoice_payload.split("_")[1]
    res= postgres.update_order_status(order_id, 'Оплачен')
    print(res)







