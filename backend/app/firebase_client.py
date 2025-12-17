import os
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# ================== LOAD ENV ==================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# CẤU HÌNH TRỰC TIẾP (ĐÃ ĐIỀN SẴN DỮ LIỆU CỦA BẠN)
# ==============================================================================

# 1. Cấu hình thông tin xác thực (Chuyển từ JSON sang Python Dict để tránh lỗi)
MY_CREDENTIAL_DICT = {
  "type": "service_account",
  "project_id": "quanlykho-78a98",
  "private_key_id": "15827da1a105a3a169a99c3e50b5ff0ecff13929",
  # Private key được dán trực tiếp, code sẽ tự xử lý xuống dòng
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC3oodIGDUk0uHz\nnofRhe8BYJRcqFHCFaObr/zndE1+ylfF4nJAGal9AOaneJ8AkfoPpDusq1T9xvWy\nl50/MmEdJHYJkEyTvC574s0kUvE3i8rTObUH+2omyg6YO2r+23croAYAuZ5nXl0G\ncDJSetMiErqK5Uza2A22Zy5tbpHolTuFOCEQpOixGIz1N80khqGgzSiyfEgB9ECc\nSx1aqQtyssHeIUcdQCS4JKYDenNXIKnaU2aR5+88fecRnjkV1U0MSAL7wsFxstDH\nO5OR72F0m6xPlZjEaI3ZsVbt6jTOVu/esg5REZUG3+m4Mlp7OpVZIIRiNwqK7x9H\nZy2VYpLzAgMBAAECggEAN9KqAkINobiTpH3cNtbarZYA89vdIr12Q2Uv4eJqjnEP\nVqH8bjz+13e3JlDWMROvKyMXWumoiA778MMDM8tqVzQWx9h8Vuq9TL7I8tJd7q9J\nxIVF4XvNrKX+4sspPvlTVEksmfrTSwQWDld8DLO2zCRaXc/P2bUVEg5ywCR9KXD0\nPLtfdpN9wgL8zfayLJzj6tiZWOBwVTk4tmDt65AxWwc2xsh2S6E/VrAiMB63fsJK\nSbMb9CZpf4tzEAjWhp+DhxAmlubIGa+IZ1J4ns698e7fWvfbcuu7gIgdBy6PUXpw\nxtag7w0M98YgkqgXAbGF5Nwt/0MMESOpPHKDeyFtKQKBgQDh2irp429XFr+2se4n\nNrqd8/kWQCw+DSPu7iiqEzxhEO+YQhxc5EmvP3AIg6cwm7iahLpehVpiHeXhoTYg\nG0EVvo+NEDYt/PpqUx8ao/0Jpc2Vl6UkxRaVwLpjEFRPgF4uf+RqZqrXruxomr1f\nQe8fECdKFDxluxq2bnUWEKAtqQKBgQDQJbU5XJmRZ1l2aRKPL+10nys6ztwPddnF\nWk6fwjc0fRYnyo7einZFDeejDbhljiigVOEnxZd4KXwVnFqs2StDbszQD4yqeg0f\nybl9vPcK83LVDTvEThMBkiMAPHKv8gCdu/jP5e4HRu/UzvzTxxkpENNPUjmxiYNC\nH4oKpc3FOwKBgQC4gUVbi0xzBgeaVaNr757m2N/dWJGMI6n+UBtyTYKe/Xnuldub\n23eCrj11BzB3Wk+mE9Y4z5I145zgBZY1Bm7WN7YIFH1ednOQltUrK1rVHdlkYt0r\nu8KmliruMPHffMv0CtDsR3E8AA/rqLYZ8sBJTSX7s6pfpUm+TWBjpTNl+QKBgQC6\nAdiPaEb7/4WdIYyqVMQ4wbzaEt3pGwH/MRKuBdtblqTj7kn6aXYDg8eKmMo+Runb\nTb7f0d3oTfpLPaxyZqgY3L0++YZVGjj8PUL8MI/8Q05NQkQ0yyiE8NlCbsJ2pScT\nzlUtRGaQLj5IyKh7gKLlZdnQOsS/+QlJX/H2TfEy3QKBgEIg+rJ/0eLyCONZDUbU\nBs6/nMXdV//l4mWFP7GbjQcDtjL5c/OgoA8uHI+RLTbZe1jROnbhhIQZSS8AgDAq\nIllTstItGJ6INTVipZp2o3ipUsykjr8AcLGBU7Ssnh8YGeNend6Kes02WkTE79kt\nPD5m3eot1H7CjKbTLAHo+bko\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@quanlykho-78a98.iam.gserviceaccount.com",
  "client_id": "118176706404501055250",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40quanlykho-78a98.iam.gserviceaccount.com",
}

# 2. Link Realtime Database (Đã tự điền đúng theo Project ID của bạn)
HARDCODED_DB_URL = "https://quanlykho-78a98-default-rtdb.asia-southeast1.firebasedatabase.app/"

# ================== INIT FIREBASE ==================

try:
    if not firebase_admin._apps:
        print("🔥 [Direct] Đang khởi tạo Firebase từ cấu hình cứng...")
        
        # QUAN TRỌNG: Fix lỗi xuống dòng trong Private Key
        if "private_key" in MY_CREDENTIAL_DICT:
             MY_CREDENTIAL_DICT["private_key"] = MY_CREDENTIAL_DICT["private_key"].replace("\\n", "\n")

        cred = credentials.Certificate(MY_CREDENTIAL_DICT)
        
        firebase_admin.initialize_app(cred, {
            "databaseURL": HARDCODED_DB_URL
        })
        print("✅ Firebase kết nối thành công!")

except Exception as e:
    print(f"❌ FIREBASE INIT ERROR: {str(e)}")
    pass

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
    return db.reference(f"products/{pid}").get() if pid else None

def save_product(pid, data):
    if pid and data: db.reference(f"products/{pid}").set(data); return data

def update_product(pid, data):
    if pid and data: db.reference(f"products/{pid}").update(data); return True

def delete_product(pid):
    if pid: db.reference(f"products/{pid}").delete(); return True

def list_products():
    return db.reference("products").get() or {}

# ================== 4. DEMAND FORECAST ==================

def save_demand_forecast(product_id: str, forecast: list):
    if product_id and forecast:
        db.reference(f"forecast_results/{product_id}").set({
            "last_run": datetime.now(timezone.utc).isoformat(),
            "horizon_days": len(forecast),
            "points": forecast
        })