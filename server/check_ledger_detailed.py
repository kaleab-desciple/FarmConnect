from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.getcwd())

from app.infrastructure.db.models import LedgerEventORM

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")
Session = sessionmaker(bind=engine)
session = Session()

escrow_id = "395fc336-7982-4248-add5-fdee00865221"
merchant_id = "MER-00016"
farmer_id = "FAR-00015"

print(f"--- Events for Escrow {escrow_id} ---")
events = session.query(LedgerEventORM).filter(LedgerEventORM.aggregate_id == escrow_id).all()
for e in events:
    print(f"ID: {e.id}, Type: {e.event_type}, Amount: {e.amount}, Dir: {e.direction}")

print(f"\n--- Events for Merchant {merchant_id} ---")
events = session.query(LedgerEventORM).filter(LedgerEventORM.aggregate_id == merchant_id).all()
for e in events:
    print(f"ID: {e.id}, Type: {e.event_type}, Amount: {e.amount}, Dir: {e.direction}")

print(f"\n--- Events for Farmer {farmer_id} ---")
events = session.query(LedgerEventORM).filter(LedgerEventORM.aggregate_id == farmer_id).all()
for e in events:
    print(f"ID: {e.id}, Type: {e.event_type}, Amount: {e.amount}, Dir: {e.direction}")
