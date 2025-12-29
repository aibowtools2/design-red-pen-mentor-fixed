from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
secret = os.getenv("LINE_CHANNEL_SECRET")

print(f"LINE_CHANNEL_ACCESS_TOKEN_EXISTS: {bool(token)}")
print(f"LINE_CHANNEL_SECRET_EXISTS: {bool(secret)}")
if token:
    print(f"Token Length: {len(token)}")
else:
    print("Token is missing")
