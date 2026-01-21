from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.getcwd())

from app.infrastructure.db.models import ReputationORM

engine = create_engine("postgresql+psycopg2://kaleab:From%401994@localhost/farm_connect")
Session = sessionmaker(bind=engine)
session = Session()

reputations = session.query(ReputationORM).all()
print(f"Total reputation records: {len(reputations)}")
for r in reputations:
    print(f"User: {r.user_id}, Score: {r.reputation_score}")
