from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.getcwd())

from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.domain.ledger.entities import AggregateType

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")
Session = sessionmaker(bind=engine)
session = Session()

repo = LedgerRepository(session)
user_id = "MER-00016"

print(f"Testing list_by_aggregate for User {user_id}...")
events = repo.list_by_aggregate(AggregateType.USER, user_id)
print(f"Found {len(events)} events")
for e in events:
    print(f"  Event: {e.id}, Type: {e.event_type}, Direction: {e.direction}")

print(f"\nTesting get_balance for User {user_id}...")
balance = repo.get_balance(AggregateType.USER, user_id)
print(f"Balance: {balance}")
