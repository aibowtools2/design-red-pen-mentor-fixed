import os
import db
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv("backend/.env")
db.DATABASE_URL = os.getenv("DATABASE_URL")
db.init_db()

def verify_and_fix():
    if not db.SessionLocal:
        print("DB not initialized")
        return

    session = db.SessionLocal()
    try:
        # 1. Check users
        users = session.query(db.User).all()
        print(f"\n--- Users ({len(users)}) ---")
        target_uid = "Ub8234c87179de71018b3b54c9dc4f1f5"
        for u in users:
            print(f"ID: {u.user_id}, Premium: {u.is_premium}, Usage: {u.last_free_usage_date}")
            if u.user_id == target_uid:
                print(f">>> Found target user! Upgrading to premium manually...")
                u.is_premium = True
                session.commit()
                print(">>> Upgrade Success!")

        # 2. Check logs
        logs = session.query(db.AnalysisLog).all()
        print(f"\n--- Analysis Logs ({len(logs)}) ---")
        for l in logs:
            print(f"ID: {l.id}, Score: {l.design_score}, Status: {l.status}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_and_fix()
