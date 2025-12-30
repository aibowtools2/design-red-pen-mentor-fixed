import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Get Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not set")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.connect() as connection:
        # 1. Add daily_usage_count (if missed)
        try:
            print("Attempting to add daily_usage_count column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN daily_usage_count INTEGER DEFAULT 0;"))
            print("Column 'daily_usage_count' added.")
        except Exception as e:
            print(f"'daily_usage_count' migration skipped/failed: {e}")

        # 2. Add username
        try:
            print("Attempting to add username column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR;"))
            print("Column 'username' added.")
        except Exception as e:
            print(f"'username' migration skipped/failed: {e}")

if __name__ == "__main__":
    run_migration()
