import requests
import json

API_KEY = "xbit_40gZEycIlXXF38AlKKU4I96ZnNaiDFOV"
VID_ID = "dQw4w9WgXcQ"
ENDPOINT = f"https://tgapi.xbitcode.com/info/{VID_ID}"

headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

print(f"Testing xbitcode API...")
print(f"URL: {ENDPOINT}")

try:
    response = requests.get(ENDPOINT, headers=headers, timeout=15)
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print("Response JSON:")
    print(json.dumps(data, indent=4))
    
    if data.get("status") == "success":
        print("\nSUCCESS!")
        print(f"Audio URL: {data.get('audio_url')}")
        print(f"Video URL: {data.get('video_url')}")
    else:
        print(f"\nFAILED: {data.get('message')}")
except Exception as e:
    print(f"Error: {e}")
