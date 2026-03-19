from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# In production (Google Cloud Run), these will be set in the environment directly.
load_dotenv()

# Database credentials from environment
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "designer_panel")

# URL encode the password to handle special characters
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

# Construct the SQLAlchemy URL
# Example format: postgresql://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
