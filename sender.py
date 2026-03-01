import requests
import time

BACKEND_URL = "http://127.0.0.1:8000/api/event"

def send_event(event_type, confidence, clip_path):
    payload = {
        "event_type": event_type,
        "confidence": confidence,
        "timestamp": int(time.time()),
        "clip_path": clip_path
    }

    try:
        res = requests.post(BACKEND_URL, json=payload, timeout=3)
        if res.status_code == 200:
            print("📡 Sent event to backend successfully.")
        else:
            print(f"⚠️ Backend error: {res.status_code}")
    except Exception as e:
        print(f"❌ Could not send event (backend offline?): {e}")