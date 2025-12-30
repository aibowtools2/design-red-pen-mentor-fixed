import os
from gemini_client import analyze_image_design
from dotenv import load_dotenv

# Force load env from current dir (backend)
load_dotenv()

# Path provided by user
image_path = r"../frontend/public/sample_test.png"

if not os.path.exists(image_path):
    print(f"Error: File not found at {image_path}")
    exit(1)

print(f"Testing Gemini 2.0 Flash Exp with: {image_path}")

try:
    context = {"type": "Test", "target": "Test", "purpose": "Model Verification"}
    result = analyze_image_design(image_path, context)
    print("--- RESPONSE ---")
    print(result[:500] + "..." if len(result) > 500 else result)
    print("--- END ---")
except Exception as e:
    print(f"FAILED: {e}")
