import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# ================== LOAD ENV ==================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# FIREBASE CONFIGURATION - Dùng private key ĐÚNG FORMAT từ JSON gốc
# ==============================================================================

# Private key từ firebase_key.json - GIỮ NGUYÊN FORMAT VỚI \n
FIREBASE_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC3oodIGDUk0uHz
nofRhe8BYJRcqFHCFaObr/zndE1+ylfF4nJAGal9AOaneJ8AkfoPpDusq1T9xvWy
l50/MmEdJHYJkEyTvC574s0kUvE3i8rTObUH+2omyg6YO2r+23croAYAuZ5nXl0G
cDJSetMiErqK5Uza2A22Zy5tbpHolTuFOCEQpOixGIz1N80khqGgzSiyfEgB9ECc
Sx1aqQtyssHeIUcdQCS4JKYDenNXIKnaU2aR5+88fecRnjkV1U0MSAL7wsFxstDH
O5OR72F0m6xPlZjEaI3ZsVbt6jTOVu/esg5REZUG3+m4Mlp7OpVZIIRiNwqK7x9H
Zy2VYpLzAgMBAAECggEAN9KqAkINobiTpH3cNtbarZYA89vdIr12Q2Uv4eJqjnEP
VqH8bjz+13e3JlDWMROvKyMXWumoiA778MMDM8tqVzQWx9h8Vuq9TL7I8tJd7q9J
xIVF4XvNrKX+4sspPvlTVEksmfrTSwQWDld8DLO2zCRaXc/P2bUVEg5ywCR9KXD0
PLtfdpN9wgL8zfayLJzj6tiZWOBwVTk4tmDt65AxWwc2xsh2S6E/VrAiMB63fsJK
SbMb9CZpf4tzEAjWhp+DhxAmlubIGa+IZ1J4ns698e7fWvfbcuu7gIgdBy6PUXpw
xtag7w0M98YgkqgXAbGF5Nwt/0MMESOpPHKDeyFtKQKBgQDh2irp429XFr+2se4n
Nrqd8/kWQCw+DSPu7iiqEzxhEO+YQhxc5EmvP3AIg6cwm7iahLpehVpiHeXhoTYg
G0EVvo+NEDYt/PpqUx8ao/0Jpc2Vl6UkxRaVwLpjEFRPgF4uf+RqZqrXruxomr1f
Qe8fECdKFDxluxq2bnUWEKAtqQKBgQDQJbU5XJmRZ1l2aRKPL+10nys6ztwPddnF
Wk6fwjc0fRYnyo7einZFDeejDbhljiigVOEnxZd4KXwVnFqs2StDbszQD4yqeg0f
ybl9vPcK83LVDTvEThMBkiMAPHKv8gCdu/jP5e4HRu/UzvzTxxkpENNPUjmxiYNC
H4oKpc3FOwKBgQC4gUVbi0xzBgeaVaNr757m2N/dWJGMI6n+UBtyTYKe/Xnuldub
23eCrj11BzB3Wk+mE9Y4z5I145zgBZY1Bm7WN7YIFH1ednOQltUrK1rVHdlkYt0r
u8KmliruMPHffMv0CtDsR3E8AA/rqLYZ8sBJTSX7s6pfpUm+TWBjpTNl+QKBgQC6
AdiPaEb7/4WdIYyqVMQ4wbzaEt3pGwH/MRKuBdtblqTj7kn6aXYDg8eKmMo+Runb
Tb7f0d3oTfpLPaxyZqgY3L0++YZVGjj8PUL8MI/8Q05NQkQ0yyiE8NlCbsJ2pScT
zlUtRGaQLj5IyKh7gKLlZdnQOsS/+QlJX/H2TfEy3QKBgEIg+rJ/0eLyCONZDUbU
Bs6/nMXdV//l4mWFP7GbjQcDtjL5c/OgoA8uHI+RLTbZe1jROnbhhIQZSS8AgDAq
IllTstItGJ6INTVipZp2o3ipUsykjr8AcLGBU7Ssnh8YGeNend6Kes02WkTE79kt
PD5m3eot1H7CjKbTLAHo+bko
-----END PRIVATE KEY-----
"""

# Cấu hình Firebase Dict
MY_CREDENTIAL_DICT = {
    "type": "service_account",
    "project_id": "quanlykho-78a98",
    "private_key_id": "15827da1a105a3a169a99c3e50b5ff0ecff13929",
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
    if pid and data: 
        db.reference(f"products/{pid}").set(data)
        return data

def update_product(pid, data):
    if pid and data: 
        db.reference(f"products/{pid}").update(data)
        return True

def delete_product(pid):
    if pid: 
        db.reference(f"products/{pid}").delete()
        return True

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