from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import shutil
from dotenv import load_dotenv
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
        # Save locally
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return data
    except Exception as e:
        return {"error": str(e), "raw_response": result_json_str}
