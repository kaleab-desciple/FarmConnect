from sqlalchemy import create_engine
from sqlalchemy import text
import sys
import os

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, currency FROM ledger_events"))
    for row in result:
        print(f"ID: {row[0]}, Currency: '{row[1]}'")
