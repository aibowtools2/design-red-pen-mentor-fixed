from fastapi import FastAPI, File, UploadFile, Form, Request, Header, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import shutil
import uuid
import time
import datetime
import stripe
from typing import List, Optional
from dotenv import load_dotenv
import tempfile
import logging
import jwt
import bcrypt
from pydantic import BaseModel, EmailStr

from .gemini_client import analyze_image_design

# Database Imports
from . import db
from sqlalchemy.orm import Session

# LINE Bot SDK
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from linebot import WebhookParser

# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Auth Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-prod")
ALGORITHM = "HS256"


import re

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    # Validator
    def validate_username(self):
        if not re.match(r'^[a-z0-9]{1,10}$', self.username):
            raise ValueError("Username must be lowercase alphanumeric and max 10 chars")

class UserLogin(BaseModel):
    email: str
    password: str

def get_password_hash(password):
    # Use bcrypt directly to avoid passlib version check issues
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password, hashed_password):
    # Use bcrypt directly to avoid passlib version check issues
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def send_welcome_email(to_email: str, username: str):
    """
    Mock Email Sender.
    In production, use smtplib or SendGrid/Resend API.
    """
    logger.info(f"--- EMAIL SENT ---")
    logger.info(f"To: {to_email}")
    logger.info(f"Subject: Welcome to Design Red Pen Mentor!")
    logger.info(f"Body: Hello {username}, thank you for registering! Your account is ready.")
    logger.info(f"------------------")

load_dotenv()

app = FastAPI()

# Initialize DB on Startup
@app.on_event("startup")
def on_startup():
    db.init_db()

# Config
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_API_KEY

line_bot_api = None
parser = None

if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET:
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    parser = WebhookParser(LINE_CHANNEL_SECRET)

# Robust CORS Handling
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [frontend_url, "http://localhost:5173"]

if frontend_url.endswith("/"):
    origins.append(frontend_url[:-1])
else:
    origins.append(frontend_url + "/")
    
# Explicitly add production domains (just to be safe)
origins.append("https://design-sensei.aibowtools.com")
origins.append("https://design-red-pen-mentor.onrender.com")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.aibowtools\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists for production
# Ensure upload directory exists (Use tempdir for Render Read-Only FS compatibility)
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "design_uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# app.mount("/files", StaticFiles(directory="."), name="files") # REMOVED: SECURITY RISK (Exposed whole source folder)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Fallback to serve index.html for SPA


@app.get("/")
def read_root():
    return {"message": "Naruhodo Design AI API is running (DB Enabled)"}

# --- Premium Logic (DB Version) ---

def is_premium(user_id: str) -> bool:
    """Check if user is premium using DB"""
    if not db.SessionLocal: 
        logger.warning("DB: SessionLocal is None in is_premium")
        return False
    
    clean_uid = user_id.strip()
    session = db.SessionLocal()
    try:
        user = session.query(db.User).filter(db.User.user_id == clean_uid).first()
        if not user:
            logger.info(f"DB: User {clean_uid} not found in DB")
            return False
            
        logger.info(f"DB: Checking User {clean_uid} -> is_premium={user.is_premium}, expiry={user.premium_expiry}, plan={user.plan_type}")
        
        # If is_premium is False, definitely not premium
        if not user.is_premium:
            return False
            
        # If it is premium, check if it has expired
        if user.premium_expiry and user.premium_expiry < datetime.datetime.utcnow():
            logger.info(f"DB: User {clean_uid} premium EXPIRED")
            return False
            
        # Otherwise, user IS premium
        logger.info(f"DB: User {clean_uid} premium VALIDATED")
        return True
    except Exception as e:
        logger.error(f"DB Error checking premium for {clean_uid}: {e}")
        return False
    finally:
        session.close()

def update_premium_status(user_id: str, plan_type: str = "monthly"):
    """Update or Add user to premium list with expiry in DB"""
    if not db.SessionLocal: return
    
    session = db.SessionLocal()
    try:
        user = session.query(db.User).filter(db.User.user_id == user_id).first()
        
        now = datetime.datetime.utcnow()
        if plan_type == "monthly":
            expiry = now + datetime.timedelta(days=32)
        else:
            expiry = now + datetime.timedelta(days=365)
            
        if user:
            user.is_premium = True
            user.premium_expiry = expiry
            user.plan_type = plan_type
            user.updated_at = now
        else:
            user = db.User(
                user_id=user_id,
                is_premium=True,
                premium_expiry=expiry,
                plan_type=plan_type,
                created_at=now,
                updated_at=now
            )
            session.add(user)
            
        session.commit()
        logger.info(f"Updated premium status for {user_id} in DB")
    except Exception as e:
        logger.error(f"Failed to write premium to DB: {e}")
        session.rollback()
    finally:
        session.close()

def save_analysis_log(job_id, user_id, filename, analysis_type, data, status="completed"):
    """Helper to save analysis results to Supabase"""
    if not db.SessionLocal: return
    try:
        with db.SessionLocal() as session:
            # Check if exists
            log = session.query(db.AnalysisLog).filter(db.AnalysisLog.id == job_id).first()
            if not log:
                log = db.AnalysisLog(id=job_id, user_id=user_id)
                session.add(log)
            
            log.timestamp = int(time.time())
            log.image_filename = filename
            log.analysis_type = analysis_type
            log.design_score = data.get("design_score", 0)
            log.status = status
            log.full_result = data
            session.commit()
            logger.info(f"Saved analysis log {job_id} to DB")
    except Exception as e:
        logger.error(f"Failed to save analysis log to DB: {e}")

# --- LINE Bot Logic (DB Version) ---

# --- Auth Endpoints ---

@app.post("/auth/signup")
def signup(user: UserCreate, background_tasks: BackgroundTasks):
    # Validation
    if not re.match(r'^[a-z0-9]{1,10}$', user.username):
        raise HTTPException(status_code=400, detail="Username must be lowercase alphanumeric and max 10 chars")

    session = db.SessionLocal()
    try:
        # Check Username
        if session.query(db.User).filter(db.User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        # Check Email
        if session.query(db.User).filter(db.User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = db.User(
            user_id=str(uuid.uuid4()),
            username=user.username,
            email=user.email,
            password_hash=get_password_hash(user.password),
            plan_type="free",
            daily_usage_count=0
        )
        session.add(new_user)
        session.commit()
        
        # Trigger Email
        background_tasks.add_task(send_welcome_email, user.email, user.username)

        return {"status": "success", "message": "User created", "user_id": new_user.user_id}
    finally:
        session.close()

@app.post("/auth/login")
def login(user: UserLogin):
    session = db.SessionLocal()
    try:
        db_user = session.query(db.User).filter(db.User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password_hash):
            if not db_user: logger.info(f"Login failed: User {user.email} not found")
            else: logger.info(f"Login failed: Password mismatch for {user.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = create_access_token({"sub": db_user.user_id, "email": db_user.email})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": db_user.user_id,
            "is_premium": db_user.is_premium
        }
    finally:
        session.close()

def get_current_user_id(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception as e:
        logger.error(f"JWT Decode Error: {e}")
        return None

def check_and_update_usage(user_id: str) -> bool:
    """Check daily usage limit using DB"""
    if not db.SessionLocal: return True # Fail open if DB issue
    
    # If premium, unlimited
    if is_premium(user_id):
        return True
        
    session = db.SessionLocal()
    try:
        user = session.query(db.User).filter(db.User.user_id == user_id).first()
        today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        
        if not user:
            # New user, create record
            user = db.User(
                user_id=user_id, 
                last_free_usage_date=today_str,
                daily_usage_count=1 # First usage
            )
            session.add(user)
            session.commit()
            return True
            
        if user.last_free_usage_date != today_str:
            # New day, reset
            user.last_free_usage_date = today_str
            user.daily_usage_count = 1
            session.commit()
            return True

        # Same day, check limit
        if user.daily_usage_count >= 3:
            return False # Limit reached
            
        # Update usage
        user.daily_usage_count += 1
        session.commit()
        return True
    except Exception as e:
        logger.error(f"Usage check error: {e}")
        return True # Fail open
    finally:
        session.close()

def handle_event_background(event):
    # Same logic but uses updated check_and_update_usage which uses DB
    try:
        if isinstance(event, MessageEvent):
            user_id = event.source.user_id
            logger.info(f"LINE EVENT: Received event from user_id: {user_id}")
            
            if isinstance(event.message, TextMessage):
                text = event.message.text
                
                if text == "使い方を見る":
                    reply_text = "【使い方ガイド】\n1. 添削したい画像を送信してください。\n2. AIがデザインを分析し、スコアとアドバイスを返信します。\n3. Web版ではさらに詳細なレポートを確認できます！"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                    return
                elif text == "分析履歴を確認":
                    history_url = f"https://design-sensei.aibowtools.com/history?uid={user_id}"
                    reply_text = f"これまでの分析履歴はこちらから確認できます！\n{history_url}"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                    return
                elif text == "無制限プランに参加":
                    upgrade_url = f"https://design-sensei.aibowtools.com/upgrade?uid={user_id}"
                    reply_text = f"🚀 無制限プラン（月額350円）に参加すると、1日の回数制限がなくなり、より詳細なデザイン分析が可能になります！\n\nお申し込みはこちら：\n{upgrade_url}"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                    return
                
                # Default reply for other texts
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="画像を送信すると、デザイン赤ペン先生が添削します！")
                )
            elif isinstance(event.message, ImageMessage):
                if not check_and_update_usage(user_id): # DB Check
                    upgrade_url = f"https://design-sensei.aibowtools.com/upgrade?uid={user_id}"
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"⚠️ 本日の無料添削は終了しました。\n(1日1回まで無料です)\n\n👇月額350円で無制限プランに参加！\n{upgrade_url}")
                    )
                    return

                message_id = event.message.id
                message_content = line_bot_api.get_message_content(message_id)
                
                temp_filename = f"line_{message_id}.jpg"
                temp_path = os.path.join(UPLOAD_DIR, temp_filename)
                
                with open(temp_path, 'wb') as fd:
                    for chunk in message_content.iter_content():
                        fd.write(chunk)
                
                try:
                    context = {"type": "LINE Upload", "target": "Unknown", "purpose": "General Check"}
                    result_json_str = analyze_image_design(temp_path, context)
                    logger.info(f"Gemini Raw Result for LINE: {result_json_str}")
                    
                    try:
                        data = json.loads(result_json_str)
                    except Exception as parse_err:
                        logger.error(f"Failed to parse Gemini JSON: {parse_err}")
                        data = {"design_score": 0, "good_points": ["解析エラーが発生しました"], "improvements": []}

                    # --- Save to Supabase ---
                    save_analysis_log(
                        job_id=f"line_{message_id}",
                        user_id=user_id,
                        filename=temp_filename,
                        analysis_type="LINE Analysis",
                        data=data
                    )
                    
                    score = data.get('design_score', 0)
                    good_points = "\n".join([f"✅ {p}" for p in data.get('good_points', [])[:2]])
                    improvements = "\n".join([f"🔧 {i.get('issue','')} -> {i.get('suggestion','')}" for i in data.get('improvements', [])[:2]])
                    
                    reply_text = f"【添削完了】\n🏆 デザインスコア: {score}点\n\n{good_points}\n\n{improvements}\n\n👇Web版ならもっと詳細な分析が見れます！\n(色・構図・フォントなど10項目以上)\nhttps://design-sensei.aibowtools.com/"
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=reply_text)
                    )
                    
                except Exception as e:
                    print(f"LINE Analysis Error: {e}")
                    try:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="申し訳ありません。分析中にエラーが発生しました。"))
                    except: pass
    except Exception as e:
        print(f"Background Task Error: {e}")

@app.post("/callback")
async def callback(request: Request, background_tasks: BackgroundTasks, x_line_signature: str = Header(None)):
    if not parser:
        return {"status": "error", "message": "LINE Bot not configured"}
    body = await request.body()
    body_str = body.decode("utf-8")
    try:
        events = parser.parse(body_str, x_line_signature)
    except InvalidSignatureError:
        return {"status": "error", "message": "Invalid signature"}

    for event in events:
        background_tasks.add_task(handle_event_background, event)
    return "OK"

# --- Async Analysis Job Store & Background Task ---
    with open("debug.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()}: {msg}\n")

JOBS = {}

def process_analysis_background(job_id: str, file_path: str, context: dict, filename: str):
    """Background Task to run Gemini Analysis and save to DB"""
    try:
        print(f"DEBUG: Background Task Started for {job_id}")
        
        # 1. Update status to 'processing'
        JOBS[job_id] = {"status": "processing"}
        if db.SessionLocal:
            with db.SessionLocal() as session:
                log = session.query(db.AnalysisLog).filter(db.AnalysisLog.id == job_id).first()
                if log:
                    log.status = "processing"
                    session.commit()
        
        print(f"DEBUG: Job {job_id}: Calling Gemini API...")
        result_json_str = analyze_image_design(file_path, context)
        print(f"DEBUG: Job {job_id}: Gemini API returned {len(result_json_str)} chars")
        
        try:
            data = json.loads(result_json_str)
            data["source_image"] = filename
            
            # 2. Update status and save result in DB
            save_analysis_log(job_id, JOBS[job_id].get("user_id", "WebUser"), filename, "Web Analysis", data)
            
            JOBS[job_id].update({"status": "completed", "data": data})
            print(f"Job {job_id}: Completed successfully.")
            
        except Exception as e:
            logger.error(f"Job {job_id} JSON Parsing Error: {e}")
            JOBS[job_id] = {"status": "failed", "error": f"JSON Parse Error: {e}", "raw": result_json_str}
            save_analysis_log(job_id, "WebUser", filename, "Web Analysis", {}, status="failed")
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        JOBS[job_id] = {"status": "failed", "error": str(e)}
        if db.SessionLocal:
            with db.SessionLocal() as session:
                log = session.query(db.AnalysisLog).filter(db.AnalysisLog.id == job_id).first()
                if log:
                    log.status = "failed"
                    session.commit()

@app.get("/status/{job_id}")
def get_job_status(job_id: str):
    """Check status of background task (uses DB to support multi-worker environments)"""
    # 1. Check local memory (fastest)
    if job_id in JOBS:
        return JOBS[job_id]
    
    # 2. Check Database (reliable for multi-worker Render/Gunicorn)
    if db.SessionLocal:
        with db.SessionLocal() as session:
            log = session.query(db.AnalysisLog).filter(db.AnalysisLog.id == job_id).first()
            if log:
                # If completed, return data
                if log.status == "completed":
                    return {"status": "completed", "data": log.full_result}
                return {"status": log.status}
    
    return {"status": "not_found"}

@app.get("/user/status")
def get_user_status(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
        
    session = db.SessionLocal()
    try:
        user = session.query(db.User).filter(db.User.user_id == user_id).first()
        if not user:
            return {"plan": "free", "usage": 0, "limit": 3}
            
        is_prem = is_premium(user_id)
        
        # Reset visual usage if new day (for display consistency)
        today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        usage = user.daily_usage_count
        if user.last_free_usage_date != today_str:
            usage = 0
            
        return {
            "plan": "premium" if is_prem else "free",
            "usage": usage,
            "limit": "unlimited" if is_prem else 3
        }
    finally:
        session.close()

@app.get("/history")
def get_history(uid: Optional[str] = None):
    """Retrieve history from DB, optionally filtered by User ID"""
    if not db.SessionLocal: return []
    
    session = db.SessionLocal()
    try:
        query = session.query(db.AnalysisLog)
        if uid:
            # Match LINE user_id or Web user_id
            query = query.filter(db.AnalysisLog.user_id == uid.strip())
            
        logs = query.order_by(db.AnalysisLog.timestamp.desc()).limit(50).all()
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "timestamp": log.timestamp,
                "type": log.analysis_type,
                "image": log.image_filename,
                "score": log.design_score,
                "status": log.status
            })
        return result
    except Exception as e:
        logger.error(f"History Fetch Error: {e}")
        return []
    finally:
        session.close()

@app.get("/history/{analysis_id}")
def get_history_item(analysis_id: str):
    """Retrieve single item from DB"""
    if not db.SessionLocal: return {"error": "DB not available"}
    
    session = db.SessionLocal()
    try:
        log = session.query(db.AnalysisLog).filter(db.AnalysisLog.id == analysis_id).first()
        if log:
            return log.full_result
        return {"error": "History item not found"}
    finally:
        session.close()

@app.post("/analyze")
def analyze_image(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    type: str = Form(""),
    target: str = Form(""),
    purpose: str = Form("")
):
    user_id = get_current_user_id(request)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not logged in")
    
    if not is_premium(user_id):
        raise HTTPException(status_code=402, detail="Premium subscription required for Web analysis (500 JPY/mo)")

    # Security: Limit file size (e.g., 10MB)
    MAX_SIZE = 10 * 1024 * 1024
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large (Max 10MB)")

    # Security: Clean unique filename to avoid path traversal
    clean_original_name = "".join([c for c in file.filename if c.isalnum() or c in "._-"])
    unique_filename = f"{uuid.uuid4()}_{clean_original_name}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create Job ID (Analysis ID)
    analysis_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Store initial status in DB (to support cross-worker coordination)
    if db.SessionLocal:
        with db.SessionLocal() as session:
            try:
                log = db.AnalysisLog(
                    id=analysis_id,
                    user_id=None,
                    timestamp=timestamp,
                    image_filename=unique_filename,
                    analysis_type=type or "Unknown",
                    status="pending"
                )
                session.add(log)
                session.commit()
            except Exception as e:
                logger.error(f"Failed to init Job in DB: {e}")
                # Fallback to local dict for local dev safety, 
                # but production relies on DB.
                JOBS[analysis_id] = {"status": "pending"}
    else:
        JOBS[analysis_id] = {"status": "pending"}
    
    context = {"type": type, "target": target, "purpose": purpose}
    
    # Start Background Task
    JOBS[analysis_id] = {"status": "pending", "user_id": user_id}
    background_tasks.add_task(process_analysis_background, analysis_id, file_path, context, unique_filename)
    
    return {"status": "accepted", "job_id": analysis_id}

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """Webhook to handle Stripe payment events (Automated Premium Linking)"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not set")
        raise HTTPException(status_code=400, detail="Webhook Secret Not Configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        
        # client_reference_id contains the LINE User ID
        user_id = session_obj.get('client_reference_id')
        customer_email = session_obj.get('customer_details', {}).get('email')
        
        logger.info(f"WEBHOOK: Received session completed. UserID: {user_id}, Email: {customer_email}")
        
        if user_id:
            logger.info(f"Payment success for user: {user_id}. Executing update_premium_status...")
            update_premium_status(user_id, "monthly")
        else:
            logger.warning(f"WEBHOOK: Payment success but client_reference_id (UserID) missing in Stripe session. EventID: {event['id']}")

    elif event['type'] == 'customer.subscription.deleted':
        # Optional: Handle cancellation
        pass

    return {"status": "success"}

# Fallback to serve index.html for SPA (Must be last)
@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
    if full_path.startswith("api") or full_path.startswith("webhook") or full_path.startswith("callback") or full_path.startswith("stripe_webhook"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    possible_index = os.path.join(".", "frontend", "dist", "index.html")
    if os.path.exists("index.html"): 
        from fastapi.responses import FileResponse
        return FileResponse("index.html")
    return {"message": "API is running. Frontend static files not found."}
