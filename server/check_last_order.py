import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append('/home/kaleab/Desktop/Farm_Connect/server')

from app.infrastructure.db.models.order import OrderORM

load_dotenv('/home/kaleab/Desktop/Farm_Connect/.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

last_order = session.query(OrderORM).order_by(OrderORM.created_at.desc()).first()
if last_order:
    print(f"ID: {last_order.id}")
    print(f"Total Price: {last_order.total_price}")
    print(f"Created At: {last_order.created_at}")
    print(f"Delivery Cost: {last_order.delivery_cost}")
    print(f"Platform Fee: {last_order.platform_fee}")
else:
    print("No orders found")
session.close()
