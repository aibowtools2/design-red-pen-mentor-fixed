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

def add_column_if_not_exists(table_name, column_name, column_type):
    with engine.connect() as connection:
        try:
            print(f"Attempting to add {column_name} column...")
            connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};"))
            connection.commit()
            print(f"Column '{column_name}' added.")
        except Exception as e:
            connection.rollback()
            print(f"'{column_name}' migration skipped/failed: {e}")

def run_migration():
    add_column_if_not_exists("users", "daily_usage_count", "INTEGER DEFAULT 0")
    add_column_if_not_exists("users", "username", "VARCHAR")
    add_column_if_not_exists("users", "email", "VARCHAR")
    add_column_if_not_exists("users", "password_hash", "VARCHAR")

if __name__ == "__main__":
    run_migration()
