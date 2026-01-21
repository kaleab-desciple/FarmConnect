from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.getcwd())

from app.infrastructure.db.models import LedgerEventORM

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")
Session = sessionmaker(bind=engine)
session = Session()

events = session.query(LedgerEventORM).all()
print(f"Total events: {len(events)}")
for e in events:
    print(f"ID: {e.id}, AggType: {e.aggregate_type}, AggID: {e.aggregate_id}, Type: {e.event_type}, Amount: {e.amount}, Dir: {e.direction}")
