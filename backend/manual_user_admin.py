import os
import uuid
import datetime
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load database connection
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_engine():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in .env")
    return create_engine(DATABASE_URL)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_premium_user(username, email, password):
    """Creates a new user and sets them to premium immediately."""
    engine = get_engine()
    user_id = str(uuid.uuid4())
    pw_hash = hash_password(password)
    now = datetime.datetime.utcnow()
    expiry = now + datetime.timedelta(days=365) # 1 year for manual
    
    with engine.connect() as conn:
        # Check if email exists
        res = conn.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
        if res.fetchone():
            print(f"Error: User with email {email} already exists. Use upgrade function instead.")
            return
            
        conn.execute(text("""
            INSERT INTO users (user_id, username, email, password_hash, is_premium, premium_expiry, plan_type, created_at, updated_at)
            VALUES (:uid, :uname, :email, :pw, true, :expiry, 'premium', :now, :now)
        """), {
            "uid": user_id,
            "uname": username,
            "email": email,
            "pw": pw_hash,
            "expiry": expiry,
            "now": now
        })
        conn.commit()
        print(f"Successfully created Premium User: {username} ({email})")

def upgrade_existing_user(email):
    """Upgrades an existing user to premium."""
    engine = get_engine()
    now = datetime.datetime.utcnow()
    expiry = now + datetime.timedelta(days=365)
    
    with engine.connect() as conn:
        res = conn.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
        if not res.fetchone():
            print(f"Error: User {email} not found.")
            return
            
        conn.execute(text("""
            UPDATE users SET is_premium = true, premium_expiry = :expiry, plan_type = 'premium', updated_at = :now
            WHERE email = :email
        """), {"email": email, "expiry": expiry, "now": now})
        conn.commit()
        print(f"Successfully upgraded {email} to Premium.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manual_user_admin.py create <username> <email> <password>")
        print("  python manual_user_admin.py upgrade <email>")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "create" and len(sys.argv) == 5:
        create_premium_user(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "upgrade" and len(sys.argv) == 3:
        upgrade_existing_user(sys.argv[2])
    else:
        print("Invalid arguments.")
