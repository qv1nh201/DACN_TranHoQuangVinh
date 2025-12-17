import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# ================== LOAD ENV ==================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# FIREBASE CONFIGURATION - KEY MỚI (Generated: Dec 17, 2025)
# ==============================================================================

# Private key MỚI từ Firebase Console
FIREBASE_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCjSXyasvCtLtTy
8LtcIYG4mr2AtUv5JH+xqOQUMOO3Wdq7jvoqJrkjEFlbSVaEKxxQuky6uMl2UcEQ
ZanRFBxM6dXQE1a5SS0rFRTp0EVKBwUr2uSiaLzb/tg+U2MsKbuMuxhDCaTrtTLi
IgZdu+T9StkiDirloB7PWmhfq444XxKwXSlIwBZ3qrRskte8HOQtJVt+9FES9AMO
ygqF3h/h3IuNkZi6ZykFupiwXNyA8/narokY/BuiG6Rr9ovCqiQACta7zOBNqQBT
3fgKaHVuI8Gr2N4TcjAJ/iYJtxfdCLvkVaVuFquoRiADS0QATOWwaSFpODKkDnhe
Z4RHmZhRAgMBAAECggEAGwaLsBMT0KYiqr77U6lcDhDWcpoPJAJNfDsm3Myms+8U
S9zDPPzBwbLwBzLhNejou9fJ4VG6TnIDkVIyRB+e+3/sWo8I2IvrBOltV7GX9kOp
MHP/SX4qXAMXCWHF1UZm+0jwIBBVkomgDVtyUEtMADxGKePMZ8sTrmAZTFRZqqyV
9U9QpgWKTip3t0yYf7lSFr//K3luARhpi2HDZTkdBvW0yg6z3Za4pK9RA64HAP7P
AZiDhN5CxvVd4FTJ3/T3S2R7X+dMIzfb41VQ8mg0lHMAgbF/hpA69mXoE0xXw0HK
VbfIa8Gb0CoVX6S2MD2wlf/V4eIkXL1I7BTNxCrdHQKBgQDTLuvyUnQY7UButgVJ
TJ6yCCD5oCqAaiWFmPPLV5JoGHik0/ilYfZyQz+W/1pXu+OwkxZsUwKvT8KWAPJ6
VnGukpyotVp+eC7NNDLhNlnnRtGXyJ8/P9CjC6Gdfp6GnZnlav3wL/qLMNK7E2MS
HFxftuKur8btOl1rSP0Xi6QEdwKBgQDF8Hp9qajybnoWeCsM8/Is82HYGaKUNHGg
7/0HS0QKq/FG86r7yan88IDd44ngt/47QEoJn7joCG0Y84IjxEeUvM5J3YG+1U/t
hRO0raeJiTRDH88IfKS/gi0VjfEa5fLS/h54598CqfWWmZ6ofIvkjR2pmnQrE7Kp
+XR7fErjdwKBgQCkfCZwTkJ468nEsWc6qT/twKEWbObNsF9bSD+TALla9Lx6/VLs
VXnjk3di/675KLH2ZQoRAzLTI1eXCFPUb6IJ682zJdW/LZKeZ+q9OV0a4zD6fNt0
Ixs48yVFC0sj5HrqksQJIQWPBk8MQNRoVcipEERM9UIGofADUQ04Gp58jwKBgC0y
xXWuaSK6sWwyEnqJtdIn3T7QU7yN4SiDxH6G5Emfi5/NAk0udn+Il5STYaeLvCTh
gEaET1/ElMzuxdfO+R1wo5ZgW0EtSmwNSDuor6oLR4DQYaEpfSEx44OZfuXKflFJ
r8GiCN1929OAzqbgkb0lsBFLcJ1piRGhIcUU07DvAoGAZdJOqvyVWVTEZWKzmBIP
e78VSxxRgAiT6E1/TM+ys4iZBBgdQcVL/Zn3mCdS2dSVXU1R+Cq0IwrK4qBRkdf/
huUwpPVRiaxbgLNyDszzGKaC03PF4YP3gpBCxBosMaCGrvOd5lPJvzsqs/0x9CeV
vEIizNp5ecgyEuxzYawapjs=
-----END PRIVATE KEY-----
"""

# Cấu hình Firebase Dict với KEY MỚI
MY_CREDENTIAL_DICT = {
    "type": "service_account",
    "project_id": "quanlykho-78a98",
    "private_key_id": "b2eaec624f6b0a158331b4d1d53bb661edf15f45",  # KEY MỚI
    "private_key": FIREBASE_PRIVATE_KEY,
    "client_email": "firebase-adminsdk-fbsvc@quanlykho-78a98.iam.gserviceaccount.com",
    "client_id": "118176706404501055250",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40quanlykho-78a98.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Link Database
HARDCODED_DB_URL = "https://quanlykho-78a98-default-rtdb.asia-southeast1.firebasedatabase.app/"

# ================== INIT FIREBASE ==================

try:
    if not firebase_admin._apps:
        print("🔥 [Direct] Đang khởi tạo Firebase với Key đã làm sạch...")
        
        cred = credentials.Certificate(MY_CREDENTIAL_DICT)
        
        firebase_admin.initialize_app(cred, {
            "databaseURL": HARDCODED_DB_URL
        })
        print("✅ Firebase kết nối thành công! (Key hợp lệ)")
    else:
        print("✅ Firebase đã được khởi tạo trước đó")

except Exception as e:
    print(f"❌ FIREBASE INIT ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    raise e  # Throw lại lỗi thay vì pass để debug dễ hơn

# ================== CẤU HÌNH NGƯỠNG CẢNH BÁO ==================

ALERT_TEMP_MAX = 35.0   # °C
ALERT_HUM_MAX = 80.0    # %

# ================== 1. SENSOR IOT ==================

def save_sensor(device_id: str, data: dict):
    if not device_id or not data: return
    try:
        ref = db.reference(f"warehouse_data/{device_id}")
        ref.push(data)
        
        alerts_ref = db.reference(f"alerts/{device_id}")
        temp = data.get("temperature")
        hum = data.get("humidity")
        ts = data.get("iso_ts") or datetime.now(timezone.utc).isoformat()

        if temp is not None and float(temp) > ALERT_TEMP_MAX:
             alerts_ref.push({"message": f"Nhiệt độ cao: {temp}°C", "type": "danger", "ts": ts})
        if hum is not None and float(hum) > ALERT_HUM_MAX:
             alerts_ref.push({"message": f"Độ ẩm cao: {hum}%", "type": "danger", "ts": ts})
    except Exception:
        pass

# ================== 2. SALES / DEMAND ==================

def save_sale(product_id: str, data: dict):
    if product_id and data:
        db.reference(f"sales_history/{product_id}").push(data)

def get_sales_history(product_id: str, limit: int = 30):
    if not product_id: return []
    try:
        snap = db.reference(f"sales_history/{product_id}").get()
        if not snap: return []
        items = sorted(list(snap.items()), key=lambda x: x[0])
        values = [v for _, v in items]
        return values[-limit:] if limit else values
    except Exception:
        return []

# ================== 3. PRODUCT ==================

def get_product(pid):
    if not pid:
        return None
    try:
        result = db.reference(f"products/{pid}").get()
        print(f"📦 get_product({pid}): {result}")
        return result
    except Exception as e:
        print(f"❌ Error getting product {pid}: {e}")
        return None

def save_product(pid, data):
    if not pid or not data:
        return None
    try:
        db.reference(f"products/{pid}").set(data)
        print(f"💾 save_product({pid}): Saved successfully")
        return data
    except Exception as e:
        print(f"❌ Error saving product {pid}: {e}")
        return None

def update_product(pid, data):
    if not pid or not data:
        return None
    try:
        # Update data vào Firebase
        db.reference(f"products/{pid}").update(data)
        # Lấy lại data mới nhất sau khi update
        updated_data = db.reference(f"products/{pid}").get()
        print(f"✏️ update_product({pid}): {data} → Updated successfully")
        return updated_data
    except Exception as e:
        print(f"❌ Error updating product {pid}: {e}")
        return None

def delete_product(pid):
    if not pid:
        return False
    try:
        # Kiểm tra product có tồn tại không
        exists = db.reference(f"products/{pid}").get()
        if not exists:
            return False
        db.reference(f"products/{pid}").delete()
        print(f"🗑️ delete_product({pid}): Deleted successfully")
        return True
    except Exception as e:
        print(f"❌ Error deleting product {pid}: {e}")
        return False

def list_products():
    try:
        result = db.reference("products").get() or {}
        print(f"📦 list_products: Found {len(result)} products")
        return result
    except Exception as e:
        print(f"❌ Error listing products: {e}")
        return {}

# ================== 4. DEMAND FORECAST ==================

def save_demand_forecast(product_id: str, forecast: list):
    if product_id and forecast:
        db.reference(f"forecast_results/{product_id}").set({
            "last_run": datetime.now(timezone.utc).isoformat(),
            "horizon_days": len(forecast),
            "points": forecast
        })