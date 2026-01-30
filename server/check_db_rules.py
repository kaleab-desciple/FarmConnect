import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add parent directory to sys.path to import app
sys.path.append('/home/kaleab/Desktop/Farm_Connect/server')

from app.infrastructure.db.models.pricing import PricingRuleORM

load_dotenv('/home/kaleab/Desktop/Farm_Connect/.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

rules = session.query(PricingRuleORM).all()
print(f"Total rules: {len(rules)}")
for r in rules:
    print(f"ID: {r.id}, Type: {r.rule_type}, Value: {r.fee_value}, Active: {r.active}")
session.close()
