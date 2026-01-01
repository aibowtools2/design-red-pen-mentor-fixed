from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap

# Settings
FONT_PATH = r"C:\Windows\Fonts\meiryo.ttc"
FONT_BOLD_PATH = r"C:\Windows\Fonts\meiryob.ttc"

def wrap_text(text, font, max_width):
    """Simple text wrapper"""
    lines = []
    text = text.replace('\r', '') # Remove weird returns
    for paragraph in text.split('\n'):
        current_line = []
        for char in paragraph:
            current_line.append(char)
            try:
                width = font.getlength("".join(current_line))
            except:
                bbox = font.getbbox("".join(current_line))
                width = bbox[2] - bbox[0]
                
            if width > max_width:
                current_line.pop()
                lines.append("".join(current_line))
                current_line = [char]
        lines.append("".join(current_line))
    return lines

def draw_icon_check(draw, x, y, size, color):
    """Draw check mark"""
    stroke = max(1, size // 8)
    points = [
        (x + size * 0.2, y + size * 0.5),
        (x + size * 0.4, y + size * 0.7),
        (x + size * 0.8, y + size * 0.3)
    ]
    draw.line(points, fill=color, width=stroke, joint='curve')

def draw_icon_fix(draw, x, y, size, color):
    """Draw wrench/fix icon"""
    stroke = max(1, size // 8)
    cx, cy = x + size * 0.7, y + size * 0.3
    r = size * 0.25
    draw.arc([cx-r, cy-r, cx+r, cy+r], 135, 405, fill=color, width=stroke)
    draw.line([x + size * 0.2, y + size * 0.8, cx - r * 0.5, cy + r * 0.5], fill=color, width=stroke)

def create_evaluation_card(score, good_points, improvements, image_path, output_path):
    """
    Generates the split-view evaluation card.
    Adaptive layout: Prioritizes Improvements. If space is tight, Good Points -> 1 item.
    """
    W, H = 1200, 1200
    COLOR_BG = (15, 17, 21, 255)
    COLOR_TEXT = (255, 255, 255, 255)
    COLOR_SUB = (161, 161, 170, 255)
    COLOR_ACCENT = (34, 211, 238, 255)
    COLOR_GLASS = (30, 32, 40, 230)
    COLOR_BORDER = (255, 255, 255, 30)

    img = Image.new('RGBA', (W, H), color=COLOR_BG)
    
    # Fonts
    try:
        font_b_path = FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else FONT_PATH
        font_label = ImageFont.truetype(font_b_path, 20)
        font_body = ImageFont.truetype(FONT_PATH, 18) 
        font_title = ImageFont.truetype(font_b_path, 34)
        font_score_label = ImageFont.truetype(font_b_path, 22)
        font_score = ImageFont.truetype(font_b_path, 100)
    except:
        font_label = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_score_label = ImageFont.load_default()
        font_score = ImageFont.load_default()
    
    # 1. Right Side Image Processing
    if os.path.exists(image_path):
        try:
            photo = Image.open(image_path).convert("RGBA")
            target_w = W // 2
            target_h = H
            
            # Background blur fill
            bg_photo = photo.copy()
            img_ratio = bg_photo.width / bg_photo.height
            target_ratio = target_w / target_h
            if img_ratio > target_ratio:
                new_h = target_h
                new_w = int(new_h * img_ratio)
            else:
                new_w = target_w
                new_h = int(new_w / img_ratio)
            bg_photo = bg_photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            bg_photo = bg_photo.crop((left, top, left + target_w, top + target_h))
            bg_photo = bg_photo.filter(ImageFilter.GaussianBlur(10))
            overlay_dark = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 100))
            bg_photo = Image.alpha_composite(bg_photo, overlay_dark)
            img.paste(bg_photo, (W // 2, 0))

            # Main Image Fit
            photo_fit = photo.copy()
            if img_ratio > target_ratio:
                fit_w = target_w
                fit_h = int(fit_w / img_ratio)
            else:
                fit_h = target_h
                fit_w = int(fit_h * img_ratio)
            fit_w = int(fit_w * 0.9)
            fit_h = int(fit_h * 0.9)
            photo_fit = photo_fit.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
            pos_x = (W // 2) + (target_w - fit_w) // 2
            pos_y = (target_h - fit_h) // 2
            img.paste(photo_fit, (pos_x, pos_y), photo_fit)
        except Exception as e:
            print(f"Image processing error: {e}")

    # 2. Left Side Glass Card
    draw = ImageDraw.Draw(img)
    draw.ellipse([-200, -200, 400, 400], fill=(34, 211, 238, 20))
    
    overlay = Image.new('RGBA', (W, H), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    
    margin = 40
    card_x, card_y = margin, margin
    card_w = (W // 2) - margin
    card_h = H - (margin * 2)
    
    draw_ov.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=30, fill=COLOR_GLASS, outline=COLOR_BORDER, width=2
    )
    
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    cx = card_x + 40
    cy = card_y + 50
    cw = card_w - 80

    # Draw Header (Fixed)
    draw.text((cx, cy), "DESIGN RED PEN", font=font_label, fill=COLOR_ACCENT)
    cy += 30
    draw.text((cx, cy), "AIデザイン添削結果", font=font_title, fill=COLOR_TEXT)
    cy += 70
    draw.text((cx, cy), "TOTAL SCORE", font=font_score_label, fill=COLOR_SUB)
    cy += 30
    draw.text((cx, cy), str(score), font=font_score, fill=COLOR_ACCENT)
    sw = draw.textlength(str(score), font=font_score)
    draw.text((cx + sw + 15, cy + 70), "/ 100", font=font_label, fill=COLOR_SUB)
    cy += 110
    draw.line([(cx, cy), (cx + cw, cy)], fill=(255, 255, 255, 50), width=1)
    cy += 30

    # --- Adaptive Content Calculation ---
    start_cy = cy
    footer_cy = H - margin - 60
    available_h = footer_cy - start_cy
    
    LINE_H = 28 
    ITEM_GAP = 8
    SECTION_GAP = 15
    HEADER_H = 30 
    
    # Compact Mode Settings
    ITEM_GAP_COMPACT = 4
    SECTION_GAP_COMPACT = 10

    def calc_section_height(points_list, item_gap, section_gap):
        h = HEADER_H + 30 
        for p in points_list:
            w_lines = wrap_text(p, font_body, cw - 40)
            h += (len(w_lines) * LINE_H) + item_gap
        h += section_gap
        return h

    # Check Normal Spacing
    h_good_2 = calc_section_height(good_points[:2], ITEM_GAP, SECTION_GAP)
    h_imp_2 = calc_section_height(improvements[:2], ITEM_GAP, SECTION_GAP)
    
    needed = h_good_2 + h_imp_2
    
    final_good_points = good_points[:2]
    use_compact = False
    
    if needed > available_h:
        # Try Compact Spacing
        h_good_2_c = calc_section_height(good_points[:2], ITEM_GAP_COMPACT, SECTION_GAP_COMPACT)
        h_imp_2_c = calc_section_height(improvements[:2], ITEM_GAP_COMPACT, SECTION_GAP_COMPACT)
        needed_compact = h_good_2_c + h_imp_2_c
        
        if needed_compact <= available_h:
            print(f"Space tight. Using Compact Mode (Need {needed_compact} <= Avail {available_h}).")
            use_compact = True
            ITEM_GAP = ITEM_GAP_COMPACT
            SECTION_GAP = SECTION_GAP_COMPACT
        else:
            print(f"Space very tight (Compact Need {needed_compact} > Avail {available_h}). Reducing Good Points.")
            final_good_points = good_points[:1]
            use_compact = True # Keep compact even if reducing, to be safe
            ITEM_GAP = ITEM_GAP_COMPACT
            SECTION_GAP = SECTION_GAP_COMPACT

    # Draw Good Points
    draw.text((cx, cy), "GOOD POINTS", font=font_score_label, fill=COLOR_SUB)
    cy += 30
    for point in final_good_points:
        draw_icon_check(draw, cx, cy+5, 24, (50, 255, 150, 255))
        wrapped = wrap_text(point, font_body, cw - 40)
        for line in wrapped:
            draw.text((cx + 35, cy), line, font=font_body, fill=COLOR_TEXT)
            cy += LINE_H
        cy += ITEM_GAP
    cy += SECTION_GAP

    # Draw Improvements
    draw.text((cx, cy), "IMPROVEMENTS", font=font_score_label, fill=COLOR_SUB)
    cy += 30
    for point in improvements[:2]:
        draw_icon_fix(draw, cx, cy+5, 24, (255, 100, 100, 255))
        wrapped = wrap_text(point, font_body, cw - 40)
        for line in wrapped:
            if cy > footer_cy - 5: break # Hard stop buffer reduced
            draw.text((cx + 35, cy), line, font=font_body, fill=COLOR_TEXT)
            cy += LINE_H
        cy += ITEM_GAP
        if cy > footer_cy - 5: break

    draw.text((cx, H - margin - 60), "design-sensei.aibowtools.com", font=font_label, fill=COLOR_SUB)
    
    img.save(output_path)
    print(f"Generated Evaluation Image: {output_path}")

def create_thumbnail(image_path, title, subtitle, output_path):
    """
    Generates a thumbnail with Note.com header sizing (1280x670).
    Style: "Design Red Pen" look - Blurred glass overlay.
    """
    W, H = 1280, 670
    img = Image.new('RGBA', (W, H), (0,0,0,255))
    
    # 1. Load and Resize Background
    try:
        if os.path.exists(image_path):
            photo = Image.open(image_path).convert("RGBA")
            img_ratio = photo.width / photo.height
            target_ratio = W / H
            if img_ratio > target_ratio:
                new_h = H
                new_w = int(new_h * img_ratio)
            else:
                new_w = W
                new_h = int(new_w / img_ratio)
            photo = photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - W) // 2
            top = (new_h - H) // 2
            photo = photo.crop((left, top, left + W, top + H))
            img.paste(photo, (0, 0))
    except Exception as e:
        print(f"Thumbnail image load error: {e}")

    # 2. Overlay Setup
    overlay_w = int(W * 0.70) # Wider to prevent text overflow
    overlay_h = int(H * 0.45)
    overlay_x = (W - overlay_w) // 2
    overlay_y = H - overlay_h - 50 # Slightly higher
    
    # 3. Create Blur Effect for the Glass area
    # Crop the background region
    crop_box = (overlay_x, overlay_y, overlay_x + overlay_w, overlay_y + overlay_h)
    glass_bg = img.crop(crop_box)
    glass_bg = glass_bg.filter(ImageFilter.GaussianBlur(15)) # Stronger blur
    
    # Darken the blurred background
    darkener = Image.new('RGBA', glass_bg.size, (0, 0, 0, 120)) # Dark tint
    glass_bg = Image.alpha_composite(glass_bg, darkener)
    
    # Create mask for rounded corners
    mask = Image.new('L', glass_bg.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, overlay_w, overlay_h), radius=20, fill=255)
    
    # Paste blurred bg back with mask
    img.paste(glass_bg, (overlay_x, overlay_y), mask)
    
    # 4. Draw Border
    overlay_layer = Image.new('RGBA', (W, H), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay_layer)
    draw_ov.rounded_rectangle(
        [overlay_x, overlay_y, overlay_x + overlay_w, overlay_y + overlay_h],
        radius=20, outline=(255, 255, 255, 100), width=3
    )
    img = Image.alpha_composite(img, overlay_layer)
    draw = ImageDraw.Draw(img)
    
    # 5. Text
    try:
        font_b_path = FONT_BOLD_PATH if os.path.exists(FONT_BOLD_PATH) else FONT_PATH
        font_main = ImageFont.truetype(font_b_path, 80)
        font_sub = ImageFont.truetype(FONT_PATH, 36) # Slightly smaller sub
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # Title
    text_main = title
    bbox_main = draw.textbbox((0, 0), text_main, font=font_main)
    w_main = bbox_main[2] - bbox_main[0]
    h_main = bbox_main[3] - bbox_main[1]
    
    # Subtitle (Wrap if needed)
    text_sub = subtitle
    # Check width
    max_text_w = overlay_w - 60
    
    # Simple fitting logic for subtitle
    font_size_sub = 36
    while True:
        font_sub = ImageFont.truetype(FONT_PATH, font_size_sub) if os.path.exists(FONT_PATH) else ImageFont.load_default()
        w_sub = draw.textlength(text_sub, font=font_sub)
        if w_sub < max_text_w or font_size_sub < 20:
            break
        font_size_sub -= 2
    
    bbox_sub = draw.textbbox((0, 0), text_sub, font=font_sub)
    w_sub = bbox_sub[2] - bbox_sub[0]
    h_sub = bbox_sub[3] - bbox_sub[1]
    
    total_text_h = h_main + h_sub + 30
    current_y = overlay_y + (overlay_h - total_text_h) // 2
    
    # Draw text centered
    draw.text((overlay_x + (overlay_w - w_main) // 2, current_y), text_main, font=font_main, fill=(255, 255, 255, 255))
    current_y += h_main + 30
    draw.text((overlay_x + (overlay_w - w_sub) // 2, current_y), text_sub, font=font_sub, fill=(230, 230, 230, 255))

    img.save(output_path)
    print(f"Generated Thumbnail: {output_path}")
