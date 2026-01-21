from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.getcwd())

from app.infrastructure.db.models import LedgerEventORM
from app.infrastructure.db.mappers import orm_to_domain
from app.domain.ledger.entities import LedgerEvent, Direction

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")
Session = sessionmaker(bind=engine)
session = Session()

orm = session.query(LedgerEventORM).filter(LedgerEventORM.aggregate_id == "MER-00016").first()
if orm:
    print(f"ORM Direction: {orm.direction} (Type: {type(orm.direction)})")
    domain = orm_to_domain(orm)
    print(f"Domain Direction: {domain.direction} (Type: {type(domain.direction)})")
    try:
        print(f"Domain Direction Value: {domain.direction.value}")
    except AttributeError as e:
        print(f"Caught error: {e}")
else:
    print("No ORM found")
