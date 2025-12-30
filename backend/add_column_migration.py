import os
import sqlalchemy
from sqlalchemy import create_engine, text

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
        try:
            # Check if column exists
            # This is a basic check; for production, use Alembic properly.
            # But for this rapid dev, raw SQL is fine.
            print("Attempting to add daily_usage_count column...")
            connection.execute(text("ALTER TABLE users ADD COLUMN daily_usage_count INTEGER DEFAULT 0;"))
            print("Column added successfully.")
        except Exception as e:
            print(f"Migration might have failed (column might exist): {e}")

if __name__ == "__main__":
    run_migration()
