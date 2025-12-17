import time
import json
import random
import paho.mqtt.client as mqtt

# Cấu hình y hệt file subscriber
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "/warehouse/sensor/data"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Sensor Giả Lập: Đã kết nối Broker!")
    else:
        print("❌ Lỗi kết nối:", rc)

client = mqtt.Client()
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)

client.loop_start() # Chạy ngầm

print(f"🚀 Bắt đầu bắn dữ liệu vào topic: {TOPIC}")

try:
    while True:
        # Random số liệu
        temp = round(random.uniform(28.0, 35.0), 2)
        hum = round(random.randint(60, 80), 1)

        data = {
            "device_id": "mqtt_sensor_01",
            "temperature": temp,
            "humidity": hum
            # Không cần iso_ts, Backend sẽ tự thêm
        }

        payload = json.dumps(data)
        client.publish(TOPIC, payload)
        
        print(f"📡 Đã gửi: {payload}")
        time.sleep(5) # 5 giây gửi 1 lần

except KeyboardInterrupt:
    print("Dừng giả lập.")
    client.loop_stop()