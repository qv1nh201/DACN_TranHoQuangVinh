import requests
import time
import json
import random # Thêm cái này để random số cho nó nhảy múa

# Thêm cái đuôi /api/sensor vào mới đúng cửa
API_URL = "https://dacn-tranhoquangvinh.onrender.com/api/sensor"

print(f"🚀 Bắt đầu gửi dữ liệu giả lập tới: {API_URL}")

while True: # Cho chạy vô tận luôn để xem biểu đồ
    # Random nhiệt độ từ 28 đến 35, độ ẩm 60-80
    temp = round(random.uniform(28.0, 35.0), 2)
    hum = round(random.randint(60, 80), 1)
    
    payload = {
        "device_id": "sim_001",
        # Backend của bạn dùng 'iso_ts', nếu không gửi nó tự lấy giờ hiện tại (tốt hơn)
        # "iso_ts": "...", 
        "temperature": temp,
        "humidity": hum
    }

    try:
        r = requests.post(API_URL, json=payload)
        
        if r.status_code == 200:
            print(f"✅ Gửi thành công: Temp={temp}, Hum={hum} | Server: {r.json()}")
        else:
            print(f"❌ Lỗi {r.status_code}: {r.text}")
            
    except Exception as e:
        print(f"⚠️ Lỗi kết nối: {e}")

    # Nghỉ 5 giây gửi 1 lần (đừng gửi nhanh quá kẻo lag server free)
    time.sleep(5)