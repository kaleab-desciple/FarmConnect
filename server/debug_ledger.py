from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the server directory to sys.path to find the app package
sys.path.append(os.getcwd())

from app.infrastructure.db.models import LedgerEventORM
from app.domain.ledger.entities import AggregateType

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")
Session = sessionmaker(bind=engine)
session = Session()

print("Querying all ledger events...")
events = session.query(LedgerEventORM).all()
for e in events:
    print(f"ID: {e.id}, AggregateType: {e.aggregate_type} ({type(e.aggregate_type)}), AggregateID: {e.aggregate_id}")

print("\nQuerying with filter...")
escrow_id = "80eb5c4f-1026-4e7c-af77-c0792c08938d"
filtered = session.query(LedgerEventORM).filter(
    LedgerEventORM.aggregate_type == AggregateType.ESCROW,
    LedgerEventORM.aggregate_id == escrow_id
).all()
print(f"Found {len(filtered)} events")
