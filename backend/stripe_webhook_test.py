
import json
import time
import hmac
import hashlib
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
WEBHOOK_URL = "http://localhost:8000/stripe-webhook"
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET") or "whsec_test_secret"
TEST_USER_ID = "U_test_stripe_automation"

def generate_stripe_signature(payload, secret):
    timestamp = str(int(time.time()))
    signed_payload = timestamp + "." + payload
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"

def simulate_stripe_webhook():
    print(f"Testing Stripe Webhook at {WEBHOOK_URL}...")
    
    # Payload matching Stripe's checkout.session.completed
    payload_dict = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_abc",
                "client_reference_id": TEST_USER_ID,
                "payment_status": "paid",
                "customer": "cus_test_xyz"
            }
        }
    }
    
    payload_str = json.dumps(payload_dict)
    signature = generate_stripe_signature(payload_str, WEBHOOK_SECRET)
    
    headers = {
        "stripe-signature": signature,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload_str, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\x1b[32mSUCCESS: Webhook call accepted!\x1b[0m")
        else:
            print("\x1b[31mFAILURE: Webhook call failed.\x1b[0m")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simulate_stripe_webhook()
