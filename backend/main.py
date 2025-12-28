from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import shutil
import uuid
import time
from typing import List
from pydantic import BaseModelfrom dotenv import load_dotenv
from gemini_client import analyze_image_design

load_dotenv()

app = FastAPI()

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
