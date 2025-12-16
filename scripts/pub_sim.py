# pub_sim.py
import requests, time, json

API_URL = "https://dacn-tranhoquangvinh.onrender.com"  # dùng endpoint test_receive

for i in range(5):
    payload = {
      "device_id":"sim_001",
      "timestamp":"2025-11-12T08:00:00Z",
      "temperature": 25 + i,
      "humidity": 60 + i,
      "weight": 50.0
    }
    r = requests.post(API_URL, json=payload)
    print("resp", r.status_code, r.text)
    time.sleep(2)
