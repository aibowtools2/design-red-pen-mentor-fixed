from db import init_db
from dotenv import load_dotenv
import os

load_dotenv()
print("Ensuring database tables exist...")
try:
    init_db()
    print("Tables created/verified successfully.")
except Exception as e:
    print(f"Error creating tables: {e}")
