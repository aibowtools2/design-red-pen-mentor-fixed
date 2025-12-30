
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import User, init_db, SessionLocal
from dotenv import load_dotenv

load_dotenv()

def check_users_in_supabase():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found.")
        return

    init_db(db_url)
    
    if not SessionLocal:
        print("Failed to initialize DB session.")
        return

    session = SessionLocal()
    try:
        users = session.query(User).all()
        print(f"Total Users in Supabase: {len(users)}")
        for i, user in enumerate(users):
            print(f"{i+1}. UserID: {user.user_id}, Plan: {user.plan_type}, Premium: {user.is_premium}, Expiry: {user.premium_expiry}")
            
    except Exception as e:
        print(f"Error querying users: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_users_in_supabase()
