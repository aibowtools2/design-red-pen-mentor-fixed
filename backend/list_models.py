import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load env from the same directory
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment.")
else:
    genai.configure(api_key=api_key)
    print("Listing available models that support 'generateContent' (Multimodal):")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name} (Display: {m.display_name})")
    except Exception as e:
        print(f"API Error: {e}")
