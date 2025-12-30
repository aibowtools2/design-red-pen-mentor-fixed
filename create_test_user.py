from dotenv import load_dotenv
load_dotenv()

import os
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from backend.db import User, Base

# Setup DB
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

import bcrypt

def get_password_hash(password):
    # Use bcrypt directly to avoid passlib version check issues
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_test_user():
    session = SessionLocal()
    try:
        # Check if exists
        test_email = "test@example.com"
        existing = session.query(User).filter(User.email == test_email).first()
        
        if existing:
            print(f"Test user {test_email} already exists. Updating password...")
            existing.password_hash = get_password_hash("password123")
            existing.username = "testuser"
            existing.daily_usage_count = 0 
            existing.plan_type = "free"
            existing.is_premium = False
            session.commit()
            print("Test user updated.")
            return

        # Create new
        new_user = User(
            user_id=str(uuid.uuid4()),
            username="testuser",
            email=test_email,
            password_hash=get_password_hash("password123"),
            plan_type="free",
            daily_usage_count=0
        )
        session.add(new_user)
        session.commit()
        print(f"Test user created: {test_email} / password123")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_test_user()
