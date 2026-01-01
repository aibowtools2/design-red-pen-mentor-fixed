import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    # Fallback or warning
    pass

if API_KEY:
    genai.configure(api_key=API_KEY)

# Model constants
# "gemini-1.5-pro-latest" is the stable multimodal workhorse.
# "gemini-exp-1206" (Gemini 2.0 Flash) is faster if available.
# ... existing code ...
IMAGE_MODEL_NAME = "gemini-2.5-pro"

def analyze_image_design(image_path, context=None):
    """
    Analyzes a static image for design feedback (Tensaku).
    Includes specific quantitative advice and Google Data integration.
    Context: { "type": "", "target": "", "purpose": "" }
    """
    print(f"Uploading image {image_path}...")
    try:
        image_file = genai.upload_file(path=image_path)
    except Exception as e:
        return json.dumps({"error": f"Upload failed: {e}"})

    # Wait for processing
    while image_file.state.name == "PROCESSING":
        time.sleep(1)
        image_file = genai.get_file(image_file.name)

    # Build Context String (Sanitized with character limits)
    context_str = ""
    if context:
        c_type = str(context.get('type', 'N/A'))[:100]
        c_target = str(context.get('target', 'General'))[:100]
        c_purpose = str(context.get('purpose', 'N/A'))[:100]
        
        context_str = f"""
    CONTEXT OF THIS DESIGN:
    - Type: {c_type}
    - Target Audience: {c_target}
    - Purpose: {c_purpose}
    
    IMPORTANT GUIDELINES:
    1. Evaluate the design specifically against this context.
    2. If Type is 'Video' or 'CM' or 'Thumbnail':
       - Focus on Cinematography (Lighting, Color Grading, Composition).
       - Check for 'Safe Areas' (text shouldn't be too close to edges).
       - Evaluate 'Readability' of on-screen text (Telop) on small screens (mobile).
       - Assess 'Storytelling' elements in the frame.
    3. If Type starts with 'Photography':
       - Focus on Composition (Rule of Thirds, Leading Lines, Symmetry).
       - Analyze Lighting (Hard/Soft, Direction, Shadow quality, Golden Hour).
       - Evaluate Subject Focus (Sharpness) and Background separation (Bokeh).
       - Check for Post-Processing (Color Balance, exposure, over-sharpening).
    """

    prompt = f"""
    You are a world-class Art Director and Design Mentor (Design Sensei). 
    The user has uploaded a creative visual.
    {context_str}
    
    Your goal is to provide a "Tensaku" (Correction) report that is **extremely actionable, specific, and data-driven**.
    Avoid vague feedback like "make it better". instead say "increase font size by 20%".
    
    You MUST leverage Google's design data (Fonts, Material Design, Color Theory) to back up your claims.
    
    Output a JSON object with the following structure:
    {{
        "status": "success",
        "design_score": 85,
        "detailed_metrics": {{
            "color_palette": {{"score": 8, "comment": "Base color is solid, but accent color contrast ratio is only 3.5:1. Aim for 4.5:1."}},
            "composition": {{"score": 7, "comment": "Main subject is centered. Try shifting to the left third line (Rule of Thirds) for dynamic tension."}},
            "typography": {{"score": 9, "comment": "Font choice is professional. Line-height is a bit tight; increase from 1.2 to 1.5."}},
            "contrast": {{"score": 6, "comment": "Text on background is hard to read. Darken the background overlay opacity by 20%."}},
            "balance": {{"score": 8, "comment": "Visual weight is well distributed."}},
            "hierarchy": {{"score": 7, "comment": "The Headline competes with the CTA. Reduce CTA size by 10% or bold the Headline."}},
            "clarity": {{"score": 9, "comment": "Message is instantly understood."}},
            "originality": {{"score": 5, "comment": "Layout is standard. Try breaking the grid or using a non-standard crop."}},
            "relevance": {{"score": 9, "comment": "Perfectly matches the target audience."}},
            "impact": {{"score": 7, "comment": "Good first impression, but lacks a 'hook' element."}}
        }},
        "good_points": [
            "Your use of whitespace around the logo (approx 40px) is professional.",
            "The color palette (#FF5500) effectively conveys energy and aligns with the purpose."
        ],
        "google_data_insights": {{
            "google_fonts_recommendation": {{
                "current_mood": "Friendly and Round",
                "suggested_font_name": "Zen Maru Gothic",
                "reason": "Your current font feels 20% too rigid. 'Zen Maru Gothic' (Google Fonts) would align better with the friendly imagery."
            }},
            "material_design_check": {{
                "metric": "Touch Target Size / Spacing",
                "observation": "Main button padding is approx 8px.",
                "verdict": "Warning",
                "advice": "Material Design recommends a minimum touch target of 48dp. Increase vertical padding to at least 12px-16px."
            }}
        }},
        "improvements": [
            {{
                "priority": "High",
                "issue": "The headline lacks impact.",
                "suggestion": "Increase the headline font size by 150% (approx 2.5x current size).",
                "quantitative_value": "150%",
                "naruhodo_principle": "Importance Scale (Daiji-do Tenbin)"
            }},
            {{
                 "priority": "Medium",
                 "issue": "Margins are inconsistent.",
                 "suggestion": "Align all left-side text elements to a strict 48px grid line.",
                 "quantitative_value": "48px",
                 "naruhodo_principle": "Alignment (Soroe)"
            }}
        ],
        "overall_comment": "A brief, encouraging summary in Japanese."
    }}
    
    Ensure "detailed_metrics" contains exactly these 10 keys: 
    color_palette, composition, typography, contrast, balance, hierarchy, clarity, originality, relevance, impact.
    All scores 1-10. 
    
    **CRITICAL**: All values (comments, suggestions, reason) MUST be in **Japanese**.
    Be specific. Use numbers (px, %, ratio).
    
    **SCORING RULES**:
    - "design_score" (0-100) MUST be calculated as the AVERAGE of the 10 "detailed_metrics" (each 1-10) multiplied by 10.
    - BE CRITICAL. Do not give high scores easily.
    - 60 = Standard / Average.
    - 80 = Professional level.
    - 90+ = Exceptional / World Class.
    - If there are clear flows (e.g. text readability issues), the score MUST be below 80.
    """
    
    model = genai.GenerativeModel(model_name=IMAGE_MODEL_NAME)
    
    print(f"Analyzing Image with {IMAGE_MODEL_NAME}...")
    try:
        # Try with JSON mode first
        try:
            response = model.generate_content(
                [image_file, prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            return response.text
        except Exception as json_mode_err:
            print(f"JSON mode failed, falling back to text: {json_mode_err}")
            # Fallback: remove JSON mode if not supported
            response = model.generate_content([image_file, prompt])
            # Extract JSON from code blocks if present
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return text
            
    except Exception as e:
        print(f"Analysis failed: {e}")
        return json.dumps({"error": str(e)})

# ... keep existing functions if needed, or comment them out ...

if __name__ == "__main__":
    # Test run
    # analyze_video_design("path/to/test.mp4")
    pass
