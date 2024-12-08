from datetime import datetime
from xmlrpc.client import DateTime
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, String, Integer, Text, ForeignKey, TIMESTAMP
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

metadata_odj = MetaData()

users = Table('users', metadata_odj,
              Column('id', Integer(), primary_key=True),
              Column('name', String(200), nullable=True),
              Column('adress', String(300)),
              Column('phone_number', String(20))
              )

products = Table('products', metadata_odj,
                 Column('id', Integer(), primary_key=True),
                 Column('name', String(200), nullable=False),
                 Column('price', Integer(), nullable=False),
                 Column('description', Text(), nullable=False),
                 Column('count', Integer(), nullable=False),
                 Column('img',String(), default='defaultImg'),
                 Column('types_id', ForeignKey("types.id")),
                 Column('categories_id', ForeignKey("categories.id"))
                )

types = Table('types', metadata_odj,
              Column('id', Integer(), primary_key=True),
              Column('name', String(200), nullable=False),
              Column('unit', String(100), nullable=True)
              )

categories = Table('categories', metadata_odj,
                   Column('id', Integer(), primary_key=True),
                   Column('name', String(200), nullable=False),
                   Column('description', String(), default='Нет описания категории'),
                   Column('img', String(), default='defaultImg_Category')
                   )

basket = Table('basket', metadata_odj,
               Column('id', Integer(), primary_key=True),
               Column('users_id', ForeignKey("users.id")),
               )
basket_products = Table('basket_products', metadata_odj,
               Column('id', Integer(), primary_key=True),
               Column('basket_id', ForeignKey("basket.id"), nullable=False),
               Column('products_id', ForeignKey("products.id"), nullable=False),
               Column('count_product', Integer(),  nullable=False),
               )
orders = Table('orders', metadata_odj,
               Column('id',  Integer(), primary_key=True),
               Column('basket_id', ForeignKey("basket.id"), nullable=False),
               Column('order_date', TIMESTAMP(), default=datetime.utcnow),
               Column('user_id', Integer(), ForeignKey('users.id'), nullable=False),
               Column('status', String(20), default='Создан'),
               Column('total_amount', Integer(), nullable=False)
               )





def create_tables_db():
    metadata_odj.drop_all(engine)
    metadata_odj.create_all(engine)

create_tables_db()




