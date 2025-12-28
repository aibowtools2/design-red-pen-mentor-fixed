from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import shutil
import uuid
import time
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
from gemini_client import analyze_image_design

# LINE Bot SDK
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage

load_dotenv()

app = FastAPI()

# LINE Config
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = None
handler = None

if LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET:
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Robust CORS Handling: Handle trailing slashes in env var
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [frontend_url, "http://localhost:5173"]

# Add variations to ensure matching (with and without slash)
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

@app.get("/")
def read_root():
    return {"message": "Naruhodo Design AI API is running"}

# --- LINE Bot Webhook ---
from fastapi import Request, Header

@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    if not handler:
        return {"status": "error", "message": "LINE Bot not configured"}
        
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        return {"status": "error", "message": "Invalid signature"}
    return "OK"

# LINE Message Handler
if handler:
    @handler.add(MessageEvent, message=ImageMessage)
    def handle_image_message(event):
        message_id = event.message.id
        message_content = line_bot_api.get_message_content(message_id)
        
        # Save temp image
        temp_filename = f"line_{message_id}.jpg"
        temp_path = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(temp_path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
                
        # Reply "Processing..."
        # Note: LINE only allows one reply per token usually, or push. 
        # Using reply_message for the final result is safer if processing is fast (<30s).
        # But Gemini might take 10s.
        
        try:
            # Sync analysis (simplest for MVP)
            context = {"type": "LINE Upload", "target": "Unknown", "purpose": "General Check"}
            result_json_str = analyze_image_design(temp_path, context)
            data = json.loads(result_json_str)
            
            # Format Reply Text
            score = data.get('design_score', 0)
            good_points = "\n".join([f"✅ {p}" for p in data.get('good_points', [])[:2]])
            improvements = "\n".join([f"🔧 {i.get('issue','')} -> {i.get('suggestion','')}" for i in data.get('improvements', [])[:2]])
            
            reply_text = f"【添削完了】\n🏆 デザインスコア: {score}点\n\n{good_points}\n\n{improvements}\n\n詳細はWebで: https://design-sensei.aibowtools.com/"
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            
            # (Optional) Save to History logic here if we had User ID...
            
        except Exception as e:
            print(f"LINE Analysis Error: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="申し訳ありません。分析中にエラーが発生しました。")
            )

    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="画像を送信すると、デザイン赤ペン先生が添削します！")
        )

HISTORY_FILE = "history_log.json"

@app.get("/history")
def get_history():
    """Returns list of past analyses"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

@app.get("/history/{analysis_id}")
def get_history_item(analysis_id: str):
    """Returns specific analysis data"""
    # Look for history_data_{id}.json
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
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"status": "processing", "message": "Analyzing..."}
    return {"status": "waiting", "message": "No analysis yet."}

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    type: str = Form(""),
    target: str = Form(""),
    purpose: str = Form("")
):
    upload_dir = "../watched_videos"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    print(f"Received Upload: {file.filename}")
    print(f"Context: {type}, {target}, {purpose}")
    
    # Analyze with Context
    context = {"type": type, "target": target, "purpose": purpose}
    result_json_str = analyze_image_design(file_path, context)
    
    try:
        data = json.loads(result_json_str)
        data["source_image"] = file.filename
        
        # --- History Implementation ---
        analysis_id = str(uuid.uuid4())
        timestamp = int(time.time())
        data["id"] = analysis_id
        data["timestamp"] = timestamp
        
        # Save individual record
        history_filename = f"history_data_{analysis_id}.json"
        with open(history_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Update Index
        history_entry = {
            "id": analysis_id,
            "timestamp": timestamp,
            "type": context.get("type", "Unknown"),
            "image": file.filename,
            "score": data.get("design_score", 0)
        }
        
        current_history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    current_history = json.load(f)
                except:
                    pass
        
        # Prepend new entry
        current_history.insert(0, history_entry)
        
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(current_history, f, ensure_ascii=False, indent=2)
            
        # Save locally (legacy support)
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return data
    except Exception as e:
        return {"error": str(e), "raw_response": result_json_str}
