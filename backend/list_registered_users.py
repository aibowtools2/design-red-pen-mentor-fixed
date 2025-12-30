import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not set in environment.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def list_users():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT user_id, username, email, created_at FROM users ORDER BY created_at DESC;"))
        users = result.fetchall()
        
        print(f"{'UserID':<40} | {'Username':<15} | {'Email':<30} | {'Created At'}")
        print("-" * 100)
        for user in users:
            print(f"{str(user.user_id):<40} | {str(user.username):<15} | {str(user.email):<30} | {user.created_at}")

if __name__ == "__main__":
    list_users()
