from bot_setting import bot
from handlers import basket
from handlers import start_file
from handlers import products
from handlers import  admin

def register_handlers():

    start_file.start_file_handler()
    products.products_handler()
    admin.admin_handler()
    basket.basket_handler()

register_handlers()
bot.polling(none_stop=True)