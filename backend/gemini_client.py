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
IMAGE_MODEL_NAME = "gemini-1.5-pro"

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

    # Build Context String
    context_str = ""
    if context:
        c_type = context.get('type', 'N/A')
        c_target = context.get('target', 'General')
        c_purpose = context.get('purpose', 'N/A')
        
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
    You are a world-class Art Director and Design Mentor. The user has uploaded a creative visual.
    {context_str}
    
    Your task is to provide a "Tensaku" (Correction) report to improve this design.
    You MUST provide specific, quantitative, and actionable advice.
    You MUST leverage Google's design data (Fonts, Material Design) to back up your claims.

    Output a JSON object with the following structure:
    {{
        "status": "success",
        "design_score": 85,
        "good_points": [
            "Your use of whitespace around the logo is excellent.",
            "The color palette (#FF5500) effectively conveys energy."
        ],
        "google_data_insights": {{
            "google_fonts_recommendation": {{
                "current_mood": "Friendly and Round",
                "suggested_font_name": "Zen Maru Gothic",
                "reason": "Your current font feels too rigid. 'Zen Maru Gothic' from Google Fonts would align 30% better with your friendly imagery."
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
            }}
        ],
        "overall_comment": "A brief, encouraging summary in Japanese."
    }}
    
    Ensure ALL text values (comments, suggestions) are in **Japanese**.
    """
    
    model = genai.GenerativeModel(model_name=IMAGE_MODEL_NAME)
    
    print(f"Analyzing Image with {IMAGE_MODEL_NAME}...")
    try:
        response = model.generate_content(
            [image_file, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text
    except Exception as e:
        print(f"Analysis failed: {e}")
        return json.dumps({"error": str(e)})

# ... keep existing functions if needed, or comment them out ...

if __name__ == "__main__":
    # Test run
    # analyze_video_design("path/to/test.mp4")
    pass
