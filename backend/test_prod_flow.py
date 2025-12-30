
import requests
import time
import os

BASE_URL = "https://design-red-pen-mentor.onrender.com"
IMAGE_PATH = "../frontend/public/sample_test.png"

def test_prod_flow():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: {IMAGE_PATH} not found.")
        return

    print(f"1. Uploading image to {BASE_URL}/analyze ...")
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": f}
        data = {
            "type": "Prod Test", 
            "target": "Debug", 
            "purpose": "Flow Check"
        }
        try:
            res = requests.post(f"{BASE_URL}/analyze", files=files, data=data, timeout=30)
            print(f"Response: {res.status_code}")
            if res.status_code != 200:
                print(f"Failed to upload: {res.text}")
                return
            
            job_data = res.json()
            job_id = job_data.get("job_id")
            print(f"Job ID received: {job_id}")
            
        except Exception as e:
            print(f"Upload Exception: {e}")
            return

    print("2. Polling status...")
    for i in range(30):
        try:
            res = requests.get(f"{BASE_URL}/status/{job_id}", timeout=10)
            status_data = res.json()
            status = status_data.get("status")
            print(f"poll {i}: {status}") 
            
            if status == "completed":
                print("SUCCESS! Production Analysis completed.")
                print(f"Score: {status_data.get('data', {}).get('design_score')}")
                return
            
            if status == "failed":
                print(f"FAILED! Error: {status_data.get('error')}")
                return
                
            time.sleep(2)
        except Exception as e:
            print(f"Polling failed: {e}")
            time.sleep(2)

    print("TIMEOUT: Production Analysis took too long.")

if __name__ == "__main__":
    test_prod_flow()
