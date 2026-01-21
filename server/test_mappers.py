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

events = repo.list_by_aggregate(AggregateType.ESCROW, escrow_id)
if events:
    event = events[0]
    print(f"Event ID: {event.id}")
    print(f"Event Type: {event.event_type} (Type: {type(event.event_type)})")
    try:
        print(f"Event Type Value: {event.event_type.value}")
    except AttributeError as e:
        print(f"Caught expected error: {e}")
else:
    print("No events found")
