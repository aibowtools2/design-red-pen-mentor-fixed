import requests
url = "https://design-red-pen-mentor.onrender.com/callback"
print(f"Checking {url}...")
try:
    resp = requests.post(url, json={}, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Response Body: {resp.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
