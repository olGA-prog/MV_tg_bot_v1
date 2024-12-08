from dotenv import  load_dotenv
import os

from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker

from database.arrayList import categories_data, types_data, products_data
from database.schema_db import categories, types, products

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

Session = sessionmaker(bind=engine)
session = Session()

session.execute(insert(categories), categories_data)
session.execute(insert(types), types_data)
session.execute(insert(products), products_data)
session.commit()
session.close()




