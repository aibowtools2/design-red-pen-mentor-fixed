import os
import datetime
from sqlalchemy import create_engine, Column, String, Text, Integer, JSON, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Placeholder - will be loaded from env
DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None
Base = declarative_base()

# --- Models ---

class User(Base):
    """
    User Table: Stores Line User ID and Premium Status
    replaces premium_users.json and user_usage.json
    """
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True) # Line UID or UUID
    username = Column(String, unique=True, index=True, nullable=True) # New: 10char limit
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)
    premium_expiry = Column(DateTime, nullable=True)
    plan_type = Column(String, default="free")
    
    last_free_usage_date = Column(String) # For daily limit check (YYYY-MM-DD)
    daily_usage_count = Column(Integer, default=0) # Counter for daily usage
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AnalysisLog(Base):
    """
    Analysis Log Table: Stores history of analyses
    replaces history_log.json
    """
    __tablename__ = "analysis_logs"

    id = Column(String, primary_key=True) # UUID
    user_id = Column(String, index=True, nullable=True) # Linked to User
    timestamp = Column(Integer)
    image_filename = Column(String)
    analysis_type = Column(String)
    design_score = Column(Integer)
    status = Column(String, default="pending") # pending, processing, completed, failed
    
    # Store full JSON result
    full_result = Column(JSON) 
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db(db_url=None):
    global engine, SessionLocal
    url = db_url or DATABASE_URL
    if not url:
        logger.warning("DATABASE_URL not set. Running without DB (In-memory/Filesystem only).")
        return

    try:
        # Fix for Supabase (uses postgres:// but SQLAlchemy needs postgresql://)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        engine = create_engine(url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create Tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"DB Initialization Error: {e}")

def get_db():
    if not SessionLocal:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
