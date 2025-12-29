import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model_name = "gemini-2.5-pro"
print(f"Testing model: {model_name}")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello")
    print("Success!")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
    
    print("\n--- Listing Available Models ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
