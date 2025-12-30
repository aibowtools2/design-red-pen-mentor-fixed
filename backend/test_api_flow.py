
import requests
import time
import os

BASE_URL = "http://localhost:8001"
IMAGE_PATH = "../frontend/public/sample_test.png"

def test_flow():
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: {IMAGE_PATH} not found.")
        return

    print(f"1. Uploading image to {BASE_URL}/analyze ...")
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": f}
        data = {
            "type": "Test API", 
            "target": "Debug", 
            "purpose": "Flow Check"
        }
        try:
            res = requests.post(f"{BASE_URL}/analyze", files=files, data=data)
            print(f"Response: {res.status_code}")
            if res.status_code != 200:
                print(f"Failed: {res.text}")
                return
            
            job_data = res.json()
            job_id = job_data.get("job_id")
            print(f"Job ID received: {job_id}")
            
        except Exception as e:
            print(f"Upload failed: {e}")
            return

    print("2. Polling status...")
    for i in range(30):
        try:
            res = requests.get(f"{BASE_URL}/status/{job_id}")
            status_data = res.json()
            status = status_data.get("status")
            print(f"poll {i}: {status}") 
            
            if status == "completed":
                print("SUCCESS! Analysis completed.")
                print(f"Score: {status_data.get('data', {}).get('design_score')}")
                return
            
            if status == "failed":
                print(f"FAILED! Error: {status_data.get('error')}")
                return
                
            time.sleep(2)
        except Exception as e:
            print(f"Polling failed: {e}")
            time.sleep(2)

    print("TIMEOUT: Analysis took too long.")

if __name__ == "__main__":
    test_flow()
