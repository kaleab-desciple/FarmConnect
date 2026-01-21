from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import sys
import os

sys.path.append(os.getcwd())

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")

with engine.connect() as conn:
    result = conn.execute(text("SELECT aggregate_type, aggregate_id, direction, amount FROM ledger_events"))
    for row in result:
        print(f"Type: {row[0]} ({type(row[0])}), ID: {row[1]}, Dir: {row[2]} ({type(row[2])}), Amt: {row[3]}")
