import os
import sys
import glob
import datetime
import json
import argparse
import asyncio
import shutil
import google.generativeai as genai
from dotenv import load_dotenv

# Path setup
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
try:
    from gemini_client import analyze_image_design
except ImportError:
    print("Error: Could not import gemini_client. Make sure you are in the project root.")
    sys.exit(1)

# Load Env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY not found.")
    sys.exit(1)
genai.configure(api_key=API_KEY)

# Constants
PIPELINE_INPUT_DIR = "pipeline_input"
ARTICLES_DIR = "articles"
IMAGES_DIR = os.path.join(ARTICLES_DIR, "images")
ARCHIVES_DIR = "archives"

# Prompts
# Prompts
# Prompts
ARTICLE_GENERATION_PROMPT = """
You are the "AiBowTools Development Team" writing a blog post.
Your task is to compile a "Design Correction Report" based on the analysis of a specific user-submitted image.

**Input Data:**
A JSON object containing analysis results:
- Image Filename
- Detected Genre
- Design Score
- Good Points & Improvements
- Analyzing Persona

**Output Format:**
Create a Markdown article in Japanese following this EXACT structure.
Do not deviate from the fixed intro/outro text provided below.

# 【デザイン赤ペン先生】AIが「[Genre Name]」をガチ添削してみた結果

こんにちは！AiBowTools 開発担当です。
今回は、デザイン赤ペン先生を使って、
「[Genre Name]」をAIが添削しました。

---

![[Image Filename]]([Image Path placeholder])

**今回の分析結果**

![[Evaluation Image]]([Evaluation Image Path placeholder])

> **[Persona Name] ([Age] / [Occupation])**
> "[Short struggle/comment]"

**📊 デザインスコア: [Score]/100**

**✅ GOOD POINT**
- [Point 1 from analysis]
- [Point 2 from analysis]

**💡 IMPROVEMENTS**
- [Improvement 1 from analysis]
- [Improvement 2 from analysis]

**📝 まとめ**
[Brief summary of the advice]

---

🚀 まずはLINEで無料体験。
「デザイン赤ペン先生」は、
スマホから最も手軽に使えるLINE公式アカウントとして
提供を開始しました。

使い方はシンプルです。
トーク画面に、
あなたが作った画像（バナー、チラシ、サムネイル等）を送信するだけ。

数秒後には、AIメンターからの熱いフィードバックが返ってきます。

▼ デザイン赤ペン先生（LINE版）を友だち追加する
https://lin.ee/7ZGruP7

(現在はベータ版として、期間・人数限定で無料公開枠を設けています)
※１日３回無料で添削を受けられます！

---
<!-- SNS用 ドラフト (以下をコピーして使ってください) -->

## X (Twitter) 用ポスト
[Friendly/Casual Tone. Max 140 chars. Include "デザイン赤ペン先生" and link placeholder.]

## Instagram 用キャプション
[Visual/Polite Tone. Explain the before/after point concisely.
Include 15+ relevant hashtags (e.g., #デザイン #Webデザイン #駆け出しデザイナー...)]
"""

def generate_persona(analysis_data, filename):
    """
    Generates a simple persona based on the image analysis/genre.
    This is a lightweight local generation or could be an LLM call.
    For speed, we'll use a lightweight LLM call or heuristics.
    Let's use a quick LLM call to get a realistic persona.
    """
    prompt = f"""
    Based on this design analysis, create a short persona for the creator of this image.
    Image: {filename}
    Analysis: {json.dumps(analysis_data)[:500]}...

    Output JSON only:
    {{
        "name": "Name (Japanese or English)",
        "age": 25,
        "occupation": "Job Title",
        "struggle": "One sentence complaint about their design",
        "genre": "Category (e.g. VLOG Thumbnail, Portfolio, Cafe Menu)",
        "catchphrase": "A short, catchy phrase about the design (e.g. 'Standard Layout', 'Eye-catching Colors') for a thumbnail subtitle"
    }}
    """
    model = genai.GenerativeModel("gemini-2.5-pro") # Use fast model
    try:
        resp = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(resp.text)
    except:
        return {"name": "Unknown", "age": 30, "occupation": "Creator", "struggle": "Design is hard", "genre": "General", "catchphrase": "Design Review"}

def process_pipeline(dry_run=False):
    # Import Image Generator here to ensure path is set or relative imports work
    try:
        from image_generator import create_evaluation_card, create_thumbnail
    except ImportError:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from image_generator import create_evaluation_card, create_thumbnail

    print(f"--- Starting Content Pipeline ---\nInput: {PIPELINE_INPUT_DIR}")
    
    image_files = glob.glob(os.path.join(PIPELINE_INPUT_DIR, "*.*"))
    valid_exts = ['.jpg', '.jpeg', '.png', '.webp']
    image_files = [f for f in image_files if os.path.splitext(f)[1].lower() in valid_exts]

    if not image_files:
        print("No images found in pipeline_input/")
        return

    print(f"Found {len(image_files)} images. Processing each one...")
    
    # Ensure directories
    if not os.path.exists(ARTICLES_DIR): os.makedirs(ARTICLES_DIR)
    target_img_dir = os.path.join(ARTICLES_DIR, "images")
    if not os.path.exists(target_img_dir): os.makedirs(target_img_dir)

    # Analyze and Process EACH image individually
    for index, img_path in enumerate(image_files):
        print(f"\n[{index+1}/{len(image_files)}] Processing {img_path}...")
        filename = os.path.basename(img_path)
        
        # 1. Analyze
        # Context is generic for pipeline
        context = {"type": "Pipeline Auto", "target": "General", "purpose": "Blog Content"}
        
        if not dry_run:
            result_json = analyze_image_design(img_path, context)
            try:
                data = json.loads(result_json)
            except:
                data = {"error": "Failed to parse analysis"}
        else:
            print("[Dry Run] Simulated analysis.")
            data = {"design_score": 85, "good_points": ["Nice colors", "Good balance"], "improvements": [{"issue": "Contrast", "suggestion": "Increase it"}, {"issue": "Font", "suggestion": "Change it"}]}

        # 2. Generate Persona (and Catchphrase)
        if not dry_run:
            persona = generate_persona(data, filename)
        else:
            persona = {"name": "Test User", "genre": "Test Genre", "struggle": "Dry run test", "catchphrase": "Test Review"}

        # 3. Generate Image Assets (Evaluation Card & Thumbnail)
        print(" Generating Image Assets...")
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        ts_suffix = datetime.datetime.now().strftime("%H%M%S")
        article_id = f"auto_review_{today_str}_{index+1}_{ts_suffix}"
        
        # File paths for assets (Saved directly to articles/images/ to be ready for posting/archiving)
        # Note: post_article_script looks for assets in the same dir as the article or images dir?
        # post_article_script args.image_dir default is ARTICLES_DIR/images
        
        # Original Image
        original_dest = os.path.join(target_img_dir, f"{article_id}_original.png")
        shutil.copy2(img_path, original_dest)
        
        # Evaluation Image
        eval_path = os.path.join(target_img_dir, f"{article_id}_evaluation.png")
        if not dry_run:
            score = data.get('design_score', 0)
            good_pts = data.get('good_points', [])
            
            # Parsin improvements (handle dict or str)
            raw_imps = data.get('improvements', [])
            imps = []
            for i in raw_imps:
                if isinstance(i, dict):
                    imps.append(f"{i.get('issue', '')}\n{i.get('suggestion', '')}")
                else:
                    imps.append(str(i))
                    
            create_evaluation_card(score, good_pts, imps, img_path, eval_path)
        else:
            shutil.copy2(img_path, eval_path) # Dummy

        # Thumbnail
        thumb_path = os.path.join(target_img_dir, f"{article_id}_thumbnail.png")
        if not dry_run:
            title_text = "デザイン添削"
            sub_text = persona.get('catchphrase', 'プロ並みのクオリティへ')
            create_thumbnail(img_path, title_text, sub_text, thumb_path)
        else:
            shutil.copy2(img_path, thumb_path) # Dummy

        # 4. Synthesize Article
        print(" Synthesizing Article...")
        
        if not dry_run:
            model = genai.GenerativeModel("gemini-2.5-pro")
            
            writing_context = {
                "filename": filename,
                "genre": persona.get('genre', 'Design'),
                "persona": persona,
                "analysis_summary": data
            }
                
            full_prompt = ARTICLE_GENERATION_PROMPT + f"\n\nData:\n{json.dumps(writing_context, indent=2, ensure_ascii=False)}"
            
            resp = model.generate_content(full_prompt)
            article_content = resp.text
            
            # Post-process: Replace placeholders with relative paths for local review, but for Note.com manually?
            # Creating markdown compatible with local view
            # Note: The post script inputs text. Images need to be uploaded manually or via sophisticated script.
            # We'll set the paths in the markdown local file so user can see what goes where.
            
            article_content = article_content.replace("[Image Path placeholder]", f"images/{os.path.basename(original_dest)}")
            article_content = article_content.replace("[Evaluation Image Path placeholder]", f"images/{os.path.basename(eval_path)}")
            
        else:
            article_content = f"# [Dry Run] Auto Generated Article for {filename}\n\nContent goes here..."

        # 5. Save Article
        output_path = os.path.join(ARTICLES_DIR, f"{article_id}.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(article_content)
        print(f" Article saved to: {output_path}")

        # 6. Trigger Posting Script (Optional per loop)
        # User requested to STOP auto-launching browser for now.
        # They want to review draft and images first.
        if not dry_run:
            print(f" [Pipeline] Draft & Images created. To post, run:\n python post_article_script.py --id {article_id} --archive")
            # import subprocess
            # # Pass the image dir so it finds the assets
            # cmd = [sys.executable, "post_article_script.py", "--id", article_id, "--archive", "--image-dir", target_img_dir]
            # print(f" Running: {' '.join(cmd)}")
            # subprocess.run(cmd)

    print("\n--- All Images Processed ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    process_pipeline(args.dry_run)
