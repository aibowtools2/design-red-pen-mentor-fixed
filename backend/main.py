from fastapi import FastAPI, File, UploadFile, Form, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import BackgroundTasks
import os
import json
import shutil
import uuid
import time
import datetime
import stripe
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

from gemini_client import analyze_image_design

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

# Robust CORS Handling: Handle trailing slashes in env var
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [frontend_url, "http://localhost:5173"]

if frontend_url.endswith("/"):
    origins.append(frontend_url[:-1])
else:
    origins.append(frontend_url + "/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.aibowtools\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists for production
UPLOAD_DIR = "../watched_videos"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/files", StaticFiles(directory="."), name="files")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Fallback to serve index.html for SPA (React Router)
@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
    if full_path.startswith("api") or full_path.startswith("webhook") or full_path.startswith("callback") or full_path.startswith("stripe_webhook"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Try to serve index.html if it exists (for SPA)
    possible_index = os.path.join(".", "frontend", "dist", "index.html") # Render default for Vite
    if os.path.exists("index.html"): # If served from root
        from fastapi.responses import FileResponse
        return FileResponse("index.html")
    return {"message": "API is running. Frontend static files not found."}

@app.get("/")
def read_root():
    return {"message": "Naruhodo Design AI API is running"}

# --- Premium Logic ---
USAGE_FILE = "user_usage.json"
PREMIUM_FILE = "premium_users.json"

def is_premium(user_id: str) -> bool:
    """
    Check if user is premium.
    Supports old format (list) and new format (dict with expiry).
    """
    if not os.path.exists(PREMIUM_FILE):
        return False
        
    try:
        with open(PREMIUM_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Case 1: Simple List (Old format)
            if isinstance(data, list):
                return user_id in data
                
            # Case 2: Dictionary (New format)
            if isinstance(data, dict):
                user_data = data.get(user_id)
                if not user_data:
                    return False
                
                # Check Expiry
                expiry_str = user_data.get("expiry")
                if not expiry_str: 
                    # If confirmed but no expiry, assume lifetime/manual
                    return True 
                
                # Compare dates
                expiry_date = datetime.datetime.fromisoformat(expiry_str)
                if datetime.datetime.now() < expiry_date:
                    return True
                    
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        
    return False

def update_premium_status(user_id: str, plan_type: str = "monthly"):
    """
    Update or Add user to premium list with expiry.
    Monthly = +1 month (32 days to be safe).
    """
    data = {}
    if os.path.exists(PREMIUM_FILE):
        try:
            with open(PREMIUM_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, dict):
                    data = content
                elif isinstance(content, list):
                    # Migrate list to dict
                    now_str = datetime.datetime.now().isoformat()
                    for uid in content:
                        data[uid] = {"plan": "legacy", "expiry": "2099-12-31T23:59:59"}
        except:
            pass
            
    # Calculate new expiry
    now = datetime.datetime.now()
    if plan_type == "monthly":
        # Add 32 days
        expiry = now + datetime.timedelta(days=32)
    else:
        expiry = now + datetime.timedelta(days=365) # fallback
        
    data[user_id] = {
        "plan": plan_type,
        "expiry": expiry.isoformat(),
        "updated_at": now.isoformat()
    }
    
    try:
        with open(PREMIUM_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Updated premium status for {user_id}")
    except Exception as e:
        logger.error(f"Failed to write premium file: {e}")

# --- LINE Bot Logic ---

def check_and_update_usage(user_id: str) -> bool:
    if is_premium(user_id):
        return True

    today_str = time.strftime("%Y-%m-%d")
    usage_data = {}

    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r", encoding="utf-8") as f:
                usage_data = json.load(f)
        except:
            pass
    
    last_used = usage_data.get(user_id)
    
    if last_used == today_str:
        return False
    
    usage_data[user_id] = today_str
    try:
        with open(USAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(usage_data, f)
    except:
        pass
        
    return True

def handle_event_background(event):
    try:
        if isinstance(event, MessageEvent):
            user_id = event.source.user_id
            
            if isinstance(event.message, TextMessage):
                 line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="画像を送信すると、デザイン赤ペン先生が添削します！")
                )
            elif isinstance(event.message, ImageMessage):
                
                # --- Daily Limit Check ---
                if not check_and_update_usage(user_id):
                    # Pass UID to Upgrade URL
                    upgrade_url = f"https://design-sensei.aibowtools.com/upgrade?uid={user_id}"
                    
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"⚠️ 本日の無料添削は終了しました。\n(1日1回まで無料です)\n\n👇月額350円で無制限プランに参加！\n{upgrade_url}")
                    )
                    return
                # -------------------------

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
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            # Development mode without verification
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    # Handle Events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get User ID from Reference
        client_reference_id = session.get('client_reference_id')
        
        if client_reference_id:
            logger.info(f"Payment successful for user: {client_reference_id}")
            update_premium_status(client_reference_id, "monthly")
        else:
            logger.warning("Payment received but no client_reference_id found.")
            
    elif event['type'] == 'invoice.payment_succeeded':
        # Recurring payment succeeded
        invoice = event['data']['object']
        # We need to find the user via Customer ID or Subscription ID if client_ref is missing
        # However, for simple MVP, Stripe often copies client_reference_id to subscription metadata if configured.
        # Otherwise, we might need a mapping DB (Stripe Customer ID -> My User ID).
        # For MVP: Rely on checkout.session for Activation.
        # Future: Store Customer ID in premium_users.json to handle renewals robustly.
        pass
        
    return {"status": "success"}

# --- Async Analysis Job Store ---
# In-memory store for simplicity (Production should use Redis/DB)
JOBS = {}

def process_analysis_background(job_id: str, file_path: str, context: dict, filename: str):
    """
    Background Task to run Gemini Analysis
    """
    try:
        JOBS[job_id] = {"status": "processing"}
        print(f"Job {job_id}: For {filename} started...")
        
        result_json_str = analyze_image_design(file_path, context)
        
        try:
            data = json.loads(result_json_str)
            data["source_image"] = filename
            
            # History Logic
            analysis_id = str(uuid.uuid4())
            timestamp = int(time.time())
            data["id"] = analysis_id
            data["timestamp"] = timestamp
            
            # Save History Data File
            history_filename = f"history_data_{analysis_id}.json"
            with open(history_filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Update History Index
            history_entry = {
                "id": analysis_id,
                "timestamp": timestamp,
                "type": context.get("type", "Unknown"),
                "image": filename,
                "score": data.get("design_score", 0)
            }
            
            current_history = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    try: current_history = json.load(f)
                    except: pass
            
            current_history.insert(0, history_entry)
            
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(current_history, f, ensure_ascii=False, indent=2)
                
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            JOBS[job_id] = {"status": "completed", "data": data}
            print(f"Job {job_id}: Completed successfully.")
            
        except Exception as e:
            logger.error(f"Job {job_id} JSON Parsing Error: {e}")
            JOBS[job_id] = {"status": "failed", "error": f"JSON Parse Error: {e}", "raw": result_json_str}
            
    except Exception as e:
        logger.error(f"Job {job_id} Formatting Error: {e}")
        JOBS[job_id] = {"status": "failed", "error": str(e)}

@app.get("/status/{job_id}")
def get_job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job


@app.get("/history")
def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

@app.get("/history/{analysis_id}")
def get_history_item(analysis_id: str):
    filename = f"history_data_{analysis_id}.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"error": "History item not found"}

@app.get("/analysis")
def get_analysis():
    data_path = "data.json"
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {"status": "processing", "message": "Analyzing..."}
    return {"status": "waiting", "message": "No analysis yet."}

@app.post("/analyze")
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    type: str = Form(""),
    target: str = Form(""),
    purpose: str = Form("")
):
    """
    Submits an analysis job. Returns a Job ID immediately.
    Client should poll /status/{job_id} for results.
    """
    upload_dir = "../watched_videos"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    job_id = str(uuid.uuid4())
    context = {"type": type, "target": target, "purpose": purpose}
    
    # Start Background Task
    background_tasks.add_task(process_analysis_background, job_id, file_path, context, file.filename)
    
    return {"status": "accepted", "job_id": job_id}

