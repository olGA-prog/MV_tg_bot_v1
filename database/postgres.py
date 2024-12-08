import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import os
from dotenv import load_dotenv , find_dotenv
from sqlalchemy.dialects.oracle import NUMBER

load_dotenv()

# Устанавливаем соединение с postgres
connection = psycopg2.connect(
    dbname=os.getenv('DBNAME'),
    user=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    host=os.getenv('HOST'),
    port=os.getenv('PORT')
)
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)


#Создание пользователя
def insert_user(users_id, user_name ):
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE id = %s', (users_id,))
        user = cursor.fetchone()
        if user is None:
            # Вставка нового пользователя
            cursor.execute('INSERT INTO users (id , name) VALUES (%s, %s) RETURNING id', (users_id,user_name))
            new_user_id = cursor.fetchone()[0]  # Получаем сгенерированный id


            # Вставка в таблицу basket, используя новый id
            cursor.execute('INSERT INTO basket (users_id) VALUES (%s)', (new_user_id,))
            print("Пользователь добавлен в базу!")
        else:
            print("Пользователь уже есть в базе!")


#Получение категории (получение названия, картинки и описания)
def get_products_category():
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT name, img, description FROM categories')
            result = cursor.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")

        categories_objects = [
            {"name": name, "img": f"{code}.jpg", "description": description} for name, code, description in result
        ]
        return categories_objects

def get_products_category_by_name(name):
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT name, img, description FROM categories WHERE name = %s', (name,))
            result = cursor.fetchone()
        except Exception as e:
            print(f"An error occurred: {e}")

        categories_objects = [
            {"name": result[0], "img": f"{result[1]}.jpg", "description": result[2]}
        ]
        return categories_objects


def get_all_products_category():
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, name FROM categories')
            result = cursor.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
        return result

def get_all_products_types():
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, name FROM types')
            result = cursor.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
        return result

def get_products_type(category):
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM categories WHERE name = %s', (category,))
            category_id = cursor.fetchone()
            cursor.execute('SELECT types_id FROM products WHERE categories_id = %s', (category_id,))
            id_type = cursor.fetchall()
            types_obj = set([item[0] for item in id_type])
            arrTypes =[]
            for t_id in types_obj:
                cursor.execute('SELECT  name FROM types WHERE id = %s', (t_id,))
                result=cursor.fetchone()
                arrTypes.append(result)
        except Exception as e:
            print(f"An error occurred: {e}")
        return arrTypes

def get_products_category_image(category):
    with connection as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT img FROM categories WHERE name = %s', (category,))
            category_img = cursor.fetchone()

        except Exception as e:
            print(f"An error occurred: {e}")
        return category_img[0]

# Возвращаем только самую важную информацию о товарах (название и цена)
def get_products_info_by_types(type):
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM types WHERE name = %s', (type,))
        types_id = cursor.fetchone()
        cursor.execute('SELECT unit FROM types WHERE id = %s', (types_id,))
        types_unit = cursor.fetchone()
        cursor.execute(
            'SELECT p.id, p.name, p.price, t.unit FROM products p JOIN types t ON p.types_id = t.id WHERE p.types_id = %s',
            (types_id,))
        product_info = cursor.fetchall()

        # Обрабатываем полученные данные
        products_objects = [
            {"id": item[0], "name": item[1], "price": item[2], "unit": item[3]} for item in product_info
        ]
        print(products_objects)
        return products_objects

def get_product_full_info(product_id):
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price, description, count, img FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        cursor.execute('SELECT types_id FROM products WHERE id = %s',
                       (product_id,))
        tipe_id = cursor.fetchone()
        cursor.execute('SELECT unit FROM types WHERE id = %s',
                       (tipe_id,))
        unit_product = cursor.fetchone()
        result = {}
        result['id'] = product[0]
        result['name'] = product[1]
        result['price'] = product[2]
        result['description'] = product[3]
        result['count'] = product[4]
        result['img'] = product[5]
        return [result, unit_product[0]]



######################################
# Для Админ панели
def get_bot_users():
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users')
        result = cursor.fetchall()
        return result


def get_count_product():
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()
        result = count[0]
        return result

def get_count_type():
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM types')
        count = cursor.fetchone()
        result = count[0]
        return result

def get_count_category():
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM categories')
        count = cursor.fetchone()
        result = count[0]
        return result


def save_product_to_db( name, description, price, quantity, product_type, product_category_id, file_name):
    try:
        with connection as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    INSERT INTO products (name, description, price, count, types_id, categories_id, img)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, description, price, quantity, product_type, product_category_id, file_name))

                conn.commit()

                return "Товар успешно добавлен в базу данных!"

    except Exception as e:
        return f"Произошла ошибка при добавлении товара: {str(e)}"

def save_product_type( product_type_name, unit):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO types ( name, unit)
                    VALUES (%s, %s)
                """, (product_type_name, unit))

                conn.commit()

                return "Тип товара успешно добавлен в базу данных!"

    except Exception as e:
        return f"Произошла ошибка при добавлении типа товара: {str(e)}"

def save_product_category(product_category_name, img, desc):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO categories (name, img, description)
                    VALUES ( %s, %s, %s)
                """, ( product_category_name, img,desc ))

                conn.commit()

                return "Категория товара успешно добавлена в базу данных!"

    except Exception as e:
        return f"Произошла ошибка при добавлении категории товара: {str(e)}"




def add_product_to_basket(user_id, product_id, quantity):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT  id FROM basket WHERE users_id = %s', (user_id,))
                basket_id1 = cursor.fetchone()
                basket_id = basket_id1[0]
                cursor.execute("""
                    INSERT INTO basket_products (basket_id, products_id, count_product)
                    VALUES (%s, %s, %s)
                """, (basket_id, int(product_id), quantity))

                conn.commit()

                return "Товар добавлен в корзину"

    except Exception as e:
        return f"Произошла ошибка при добавлении товара: {str(e)}"


###############################Корзина############################

def get_products_to_basket_user(user_id):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT  id FROM basket WHERE users_id = %s', (user_id,))
                basket_id1 = cursor.fetchone()
                basket_id = basket_id1[0]
                cursor.execute('SELECT  products_id, count_product  FROM basket_products WHERE basket_id = %s', (basket_id,))
                result = cursor.fetchall()
                product_obj = [
                    {"products_id": id_p, "count_product": count } for id_p, count in result
                ]
                print(product_obj)

                return product_obj

    except Exception as e:
        return f"Произошла ошибка при получении товаров: {str(e)}"


def delete_product_basket(user_id, product_id):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT  id FROM basket WHERE users_id = %s', (user_id,))
                basket_id1 = cursor.fetchone()
                basket_id = basket_id1[0]

                cursor.execute('DELETE FROM basket_products WHERE products_id = %s AND basket_id = %s',
                               (product_id, basket_id))

                return "Товар успешно удален из вашей корзины!"

    except Exception as e:
        return f"Произошла ошибка при удалении товара!: {str(e)}"


def delete_all_users_product_basket(user_id):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT  id FROM basket WHERE users_id = %s', (user_id,))
                basket_id1 = cursor.fetchone()
                basket_id = basket_id1[0]

                cursor.execute('DELETE FROM basket_products WHERE  basket_id = %s',
                               (basket_id, ))

                return "Все товары успешно удалены из вашей корзины!"

    except Exception as e:
        return f"Произошла ошибка при удалении товаров!: {str(e)}"


def edit_count_product(user_id, product_id, new_count):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT  id FROM basket WHERE users_id = %s', (user_id,))
                basket_id1 = cursor.fetchone()
                basket_id = basket_id1[0]

                cursor.execute('UPDATE basket_products SET count_product = %s WHERE products_id = %s AND basket_id = %s',(new_count, product_id, basket_id))

                return " Количество товара успешно изменено!"

    except Exception as e:
        return f"Произошла ошибка при изменении количества товара!: {str(e)}"


def get_full_user_info(user_id):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                print(user_id)
                cursor.execute('SELECT  name, adress, phone_number  FROM users WHERE id = %s', (int(user_id),))
                user_info1 = cursor.fetchall()
                user_info = user_info1[0]
                if not user_info:
                    return f"Пользователь с id {user_id} не найден."
                result = {}
                result['name'] = user_info[0]
                result['adress'] = user_info[1]
                result['phone_number'] = user_info[2]
                return result

    except Exception as e:
        return f"Произошла ошибка при получении информации о пользователе!: {str(e)}"


def edit_name_user(user_id, new_name_user):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE users SET name = %s WHERE id = %s ',
                    (new_name_user, int(user_id)))
                return " Имя успешно изменено!"

    except Exception as e:
        return f"Произошла ошибка при изменении имени!: {str(e)}"


def edit_adress_user(user_id, new_name_adress):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE users SET adress = %s WHERE id = %s ',
                    (new_name_adress, int(user_id)))
                return " Адрес успешно изменен!"

    except Exception as e:
        return f"Произошла ошибка при изменении адреса!: {str(e)}"


def edit_phone_number(user_id, new_phone_number):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE users SET phone_number = %s WHERE id = %s ',
                    (new_phone_number, int(user_id)))
                return " Номер телефона сохранен!"

    except Exception as e:
        return f"Произошла ошибка при изменении телефона!: {str(e)}"

#заказ

def get_basket_id_by_user_id(user_id):
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM basket WHERE users_id = %s', (int(user_id),))
        count = cursor.fetchone()
        result = count[0]
        print(result)
        return result


def create_order_for_user(user_id, basket_id, date_order, fullprice, status):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO orders (basket_id, order_date, user_id, status, total_amount)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id;
                """, (int(basket_id), date_order, int(user_id), status, int(fullprice)))

                order_id = cursor.fetchone()[0]
                conn.commit()

                return order_id, "Заказ создан!"

    except Exception as e:
        return None, f"Произошла ошибка при создании заказа: {str(e)}"


def get_order_status(order_id):
    with connection as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM orders WHERE id = %s', (int(order_id),))
        count = cursor.fetchone()
        result = count[0]
        print(result)
        return result


def update_order_status(order_id, param):
    try:
        with connection as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'UPDATE orders SET status = %s WHERE id = %s ',
                    (param, int(order_id)))
                return " Новый статус сохранен!"

    except Exception as e:
        return f"Произошла ошибка при изменении статуса!: {str(e)}"