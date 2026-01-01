from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import json
import traceback
import sys

# 設定
OUTPUT_DIR = r"c:\Users\81905\Desktop\なるほどデザイン\backend\generated_ogp_samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# フォントパス
FONT_PATH = r"C:\Windows\Fonts\meiryo.ttc"

def wrap_text(text, font, max_width):
    """シンプルなテキスト折り返し処理"""
    lines = []
    for paragraph in text.split('\n'):
        current_line = []
        for char in paragraph:
            current_line.append(char)
            width = font.getlength("".join(current_line))
            if width > max_width:
                current_line.pop() 
                lines.append("".join(current_line))
                current_line = [char]
        lines.append("".join(current_line))
    return lines

def draw_icon_check(draw, x, y, size, color):
    """チェックマークアイコンを描画"""
    stroke = size // 8
    points = [
        (x + size * 0.2, y + size * 0.5),
        (x + size * 0.4, y + size * 0.7),
        (x + size * 0.8, y + size * 0.3)
    ]
    draw.line(points, fill=color, width=stroke, joint='curve')

def draw_icon_fix(draw, x, y, size, color):
    """改善アイコン（レンチ風）を描画"""
    stroke = size // 8
    cx, cy = x + size * 0.7, y + size * 0.3
    r = size * 0.25
    draw.arc([cx-r, cy-r, cx+r, cy+r], 135, 405, fill=color, width=stroke)
    draw.line([x + size * 0.2, y + size * 0.8, cx - r * 0.5, cy + r * 0.5], fill=color, width=stroke)

def create_split_ogp(score, good_points, improvements, image_path, filename):
    # キャンバスサイズ
    W, H = 1200, 1200
    
    # 配色 (Dark Mode)
    COLOR_BG = (15, 17, 21, 255)       # 背景
    COLOR_TEXT = (255, 255, 255, 255)  # 白文字
    COLOR_SUB = (161, 161, 170, 255)   # グレー文字
    COLOR_ACCENT = (34, 211, 238, 255) # シアン
    COLOR_GLASS = (30, 32, 40, 230)    # グラスモーフィズム背景
    COLOR_BORDER = (255, 255, 255, 30) # 枠線

    # ベース画像 (RGBA)
    img = Image.new('RGBA', (W, H), color=COLOR_BG)
    
    # --- 右側：画像エリア (Fit with Blur) ---
    if os.path.exists(image_path):
        try:
            photo = Image.open(image_path).convert("RGBA")
            target_w = W // 2
            target_h = H
            
            # 1. 背景用：画像を拡大してぼかす
            bg_photo = photo.copy()
            # アスペクト比維持で「埋める」サイズに
            img_ratio = bg_photo.width / bg_photo.height
            target_ratio = target_w / target_h
            if img_ratio > target_ratio:
                new_h = target_h
                new_w = int(new_h * img_ratio)
            else:
                new_w = target_w
                new_h = int(new_w / img_ratio)
            bg_photo = bg_photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # 中央クロップ
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            bg_photo = bg_photo.crop((left, top, left + target_w, top + target_h))
            # ぼかし (簡易: 縮小して拡大)
            bg_photo = bg_photo.resize((target_w // 10, target_h // 10), Image.Resampling.BILINEAR)
            bg_photo = bg_photo.resize((target_w, target_h), Image.Resampling.NEAREST)
            # 暗くする
            overlay_dark = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 100))
            bg_photo = Image.alpha_composite(bg_photo, overlay_dark)
            img.paste(bg_photo, (W // 2, 0))

            # 2. メイン画像：全体が入るようにリサイズ (Fit)
            photo_fit = photo.copy()
            # 幅または高さに合わせて縮小
            if img_ratio > target_ratio:
                # 横長 -> 幅を合わせる
                fit_w = target_w
                fit_h = int(fit_w / img_ratio)
            else:
                # 縦長 -> 高さを合わせる
                fit_h = target_h
                fit_w = int(fit_h * img_ratio)
            
            # 少しマージンを入れる (90%)
            fit_w = int(fit_w * 0.9)
            fit_h = int(fit_h * 0.9)
            
            photo_fit = photo_fit.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
            
            # センター配置
            pos_x = (W // 2) + (target_w - fit_w) // 2
            pos_y = (target_h - fit_h) // 2
            
            # 影をつける
            shadow = Image.new('RGBA', (fit_w, fit_h), (0, 0, 0, 0))
            # 簡易影: ずらして黒半透明
            # (Pillowでの影描画は少し手間なので、ここではそのまま貼り付け or 枠線)
            # 画像貼り付け
            img.paste(photo_fit, (pos_x, pos_y), photo_fit)
            
        except Exception as e:
            print(f"Image loading error: {e}")

    # --- 左側：グラスモーフィズムカード ---
    draw_bg = ImageDraw.Draw(img)
    # 左上の円（シアン）は残す
    draw_bg.ellipse([-200, -200, 400, 400], fill=(34, 211, 238, 20))
    # 右下の円（赤）は削除
    
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    margin = 40
    card_x, card_y = margin, margin
    card_w = (W // 2) - margin
    card_h = H - (margin * 2)
    
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=30, fill=COLOR_GLASS, outline=COLOR_BORDER, width=2
    )

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    try:
        font_path_bold = r"C:\Windows\Fonts\meiryob.ttc"
        if not os.path.exists(font_path_bold): font_path_bold = FONT_PATH   
        font_label = ImageFont.truetype(font_path_bold, 20)
        font_body = ImageFont.truetype(FONT_PATH, 20)       # 24 -> 20 (User Request)
        font_title = ImageFont.truetype(font_path_bold, 30)
        font_score_label = ImageFont.truetype(font_path_bold, 22) # 24 -> 22
        font_score = ImageFont.truetype(font_path_bold, 100) # 120 -> 100
    except:
        font_body = ImageFont.load_default()
        font_score = ImageFont.load_default() 

    cx = card_x + 40
    cy = card_y + 40 # 50 -> 40
    cw = card_w - 80

    # Draw Content
    draw.text((cx, cy), "DESIGN RED PEN", font=font_label, fill=COLOR_ACCENT)
    cy += 30
    draw.text((cx, cy), "AIデザイン添削結果", font=font_title, fill=COLOR_TEXT)
    cy += 60

    draw.text((cx, cy), "TOTAL SCORE", font=font_score_label, fill=COLOR_SUB)
    cy += 20
    draw.text((cx, cy), f"{score}", font=font_score, fill=COLOR_ACCENT)
    sw = draw.textlength(f"{score}", font=font_score)
    draw.text((cx + sw + 15, cy + 65), "/ 100", font=font_label, fill=COLOR_SUB)
    
    cy += 110
    draw.line([(cx, cy), (cx + cw, cy)], fill=(255, 255, 255, 50), width=1)
    cy += 30

    # Good Points
    draw.text((cx, cy), "GOOD POINTS", font=font_score_label, fill=COLOR_SUB)
    cy += 35
    for point in good_points[:2]: # Max 2 items
        draw_icon_check(draw, cx, cy+5, 24, (50, 255, 150, 255))
        # 文字数制限を撤廃し、折り返し表示に任せる
        
        wrapped = wrap_text(point, font_body, cw - 40)
        for line in wrapped:
            draw.text((cx + 35, cy), line, font=font_body, fill=COLOR_TEXT)
            cy += 35
        cy += 10
    cy += 15

    # Improvements
    draw.text((cx, cy), "IMPROVEMENTS", font=font_score_label, fill=COLOR_SUB)
    cy += 35
    for point in improvements[:2]:
        draw_icon_fix(draw, cx, cy+5, 24, (255, 100, 100, 255))
        # 文字数制限を撤廃
        
        wrapped = wrap_text(point, font_body, cw - 40)
        for line in wrapped:
            draw.text((cx + 35, cy), line, font=font_body, fill=COLOR_TEXT)
            cy += 35
        cy += 10

    draw.text((cx, H - margin - 60), "design-sensei.aibowtools.com", font=font_label, fill=COLOR_SUB)

    save_path = os.path.join(OUTPUT_DIR, filename)
    img.save(save_path)
    print(f"Generated: {save_path}")

if __name__ == "__main__":
    # --- Real Analysis Execution ---
    try:
        from gemini_client import analyze_image_design
    except ImportError:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from gemini_client import analyze_image_design

    TARGET_IMAGE = r"C:\Users\81905\.gemini\antigravity\brain\02062e6f-b45e-4afd-9eb0-a31c492330fa\uploaded_image_1767198482772.png"
    OUTPUT_FILENAME = "ogp_result_screenshot_analysis.png"

    if not os.path.exists(TARGET_IMAGE):
        print(f"Error: Target image not found at {TARGET_IMAGE}")
        # Fallback Test
        create_split_ogp(0, ["Test"], ["Image Not Found"], TARGET_IMAGE, OUTPUT_FILENAME)
    else:
        print(f"Analyzing {TARGET_IMAGE}...")
        try:
            context = {"type": "UI/UX Screenshot", "target": "General", "purpose": "Design Check"}
            result_json = analyze_image_design(TARGET_IMAGE, context)
            
            try:
                data = json.loads(result_json)
                score = data.get("design_score", 0)
                good_points = data.get("good_points", [])[:2]
                raw_improvements = data.get("improvements", [])
                improvements = []
                for i in raw_improvements[:2]:
                    if isinstance(i, dict):
                        improvements.append(f"{i.get('issue', '')} -> {i.get('suggestion', '')}")
                    else:
                        improvements.append(str(i))
                        
                create_split_ogp(score, good_points, improvements, TARGET_IMAGE, OUTPUT_FILENAME)
                
            except json.JSONDecodeError:
                print("JSON Decode Failed. Raw output:")
                print(result_json)
                create_split_ogp("?", ["解析失敗"], ["JSON Error"], TARGET_IMAGE, OUTPUT_FILENAME)
                
        except Exception as e:
            traceback.print_exc()
            print(f"Analysis failed: {e}")
