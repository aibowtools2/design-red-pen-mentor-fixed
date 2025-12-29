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
from typing import List
from dotenv import load_dotenv
import logging
import tempfile

from gemini_client import analyze_image_design

# Database Imports

# Force Reload Triggered
from db import init_db, get_db, User, AnalysisLog, SessionLocal
from sqlalchemy.orm import Session

# LINE Bot SDK
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from linebot import WebhookParser

# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Initialize DB on Startup
@app.on_event("startup")
def on_startup():
    init_db()

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
    if not SessionLocal: return False # Fallback if DB invalid
    
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
            
        if user.plan_type == "monthly":
             if user.premium_expiry and user.premium_expiry > datetime.datetime.utcnow():
                 return True
                 
        # Legacy fallback or future plans
        return False
    except Exception as e:
        logger.error(f"DB Error checking premium: {e}")
        return False
    finally:
        session.close()

def update_premium_status(user_id: str, plan_type: str = "monthly"):
    """Update or Add user to premium list with expiry in DB"""
    if not SessionLocal: return
    
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        
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
            user = User(
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

# --- LINE Bot Logic (DB Version) ---

def check_and_update_usage(user_id: str) -> bool:
    """Check daily usage limit using DB"""
    if not SessionLocal: return True # Fail open if DB issue
    
    # If premium, unlimited
    if is_premium(user_id):
        return True
        
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        
        if not user:
            # New user, create record
            user = User(user_id=user_id, last_free_usage_date=today_str)
            session.add(user)
            session.commit()
            return True
            
        if user.last_free_usage_date == today_str:
            return False # Already used today
            
        # Update usage
        user.last_free_usage_date = today_str
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
            
            if isinstance(event.message, TextMessage):
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
                    data = json.loads(result_json_str)
                    
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

# --- Stripe Webhook ---
@app.post("/stripe_webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')
        if client_reference_id:
            logger.info(f"Payment successful for user: {client_reference_id}")
            update_premium_status(client_reference_id, "monthly") # Uses DB
        else:
            logger.warning("Payment received but no client_reference_id found.")
            
    return {"status": "success"}

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
        if SessionLocal:
            with SessionLocal() as session:
                log = session.query(AnalysisLog).filter(AnalysisLog.id == job_id).first()
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
            if SessionLocal:
                with SessionLocal() as session:
                    log = session.query(AnalysisLog).filter(AnalysisLog.id == job_id).first()
                    if log:
                        log.status = "completed"
                        log.design_score = data.get("design_score", 0)
                        log.full_result = data
                        session.commit()
                        print(f"DEBUG: Job {job_id}: Saved to DB successfully")
            
            JOBS[job_id] = {"status": "completed", "data": data}
            print(f"Job {job_id}: Completed successfully.")
            
        except Exception as e:
            logger.error(f"Job {job_id} JSON Parsing Error: {e}")
            JOBS[job_id] = {"status": "failed", "error": f"JSON Parse Error: {e}", "raw": result_json_str}
            if SessionLocal:
                with SessionLocal() as session:
                    log = session.query(AnalysisLog).filter(AnalysisLog.id == job_id).first()
                    if log:
                        log.status = "failed"
                        session.commit()
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        JOBS[job_id] = {"status": "failed", "error": str(e)}
        if SessionLocal:
            with SessionLocal() as session:
                log = session.query(AnalysisLog).filter(AnalysisLog.id == job_id).first()
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
    if SessionLocal:
        with SessionLocal() as session:
            log = session.query(AnalysisLog).filter(AnalysisLog.id == job_id).first()
            if log:
                # If completed, return data
                if log.status == "completed":
                    return {"status": "completed", "data": log.full_result}
                return {"status": log.status}
    
    return {"status": "not_found"}

@app.get("/history")
def get_history():
    """Retrieve history from DB"""
    if not SessionLocal: return []
    
    session = SessionLocal()
    try:
        # Get latest 50
        logs = session.query(AnalysisLog).order_by(AnalysisLog.timestamp.desc()).limit(50).all()
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "timestamp": log.timestamp,
                "type": log.analysis_type,
                "image": log.image_filename,
                "score": log.design_score
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
    if not SessionLocal: return {"error": "DB not available"}
    
    session = SessionLocal()
    try:
        log = session.query(AnalysisLog).filter(AnalysisLog.id == analysis_id).first()
        if log:
            return log.full_result
        return {"error": "History item not found"}
    finally:
        session.close()

@app.post("/analyze")
def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    type: str = Form(""),
    target: str = Form(""),
    purpose: str = Form("")
):
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
    if SessionLocal:
        with SessionLocal() as session:
            try:
                log = AnalysisLog(
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
        session = event['data']['object']
        
        # client_reference_id contains the LINE User ID (passed from Upgrade.jsx)
        user_id = session.get('client_reference_id')
        
        if user_id:
            logger.info(f"Payment success for user: {user_id}. Upgrading to premium...")
            update_premium_status(user_id, "monthly")
        else:
            logger.warning("Payment success but client_reference_id (UserID) missing in Stripe session.")

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
