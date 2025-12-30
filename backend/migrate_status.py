import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def migrate():
    if not DATABASE_URL:
        print("DATABASE_URL not found")
        return

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='analysis_logs' AND column_name='status';
            """))
            if not result.fetchone():
                print("Adding 'status' column to 'analysis_logs'...")
                conn.execute(text("ALTER TABLE analysis_logs ADD COLUMN status VARCHAR DEFAULT 'pending';"))
                conn.commit()
                print("Migration successful!")
            else:
                print("'status' column already exists.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
