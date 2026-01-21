import os

class Settings:
    PROJECT_NAME: str = "Farmer-Merchant Connector"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost/farm_connect")

settings = Settings()