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
escrow_id = "80eb5c4f-1026-4e7c-af77-c0792c08938d"

print(f"Testing list_by_aggregate for {escrow_id}...")
events = repo.list_by_aggregate(AggregateType.ESCROW, escrow_id)
print(f"Found {len(events)} events")

print(f"\nTesting get_balance for {escrow_id}...")
balance = repo.get_balance(AggregateType.ESCROW, escrow_id)
print(f"Balance: {balance}")
