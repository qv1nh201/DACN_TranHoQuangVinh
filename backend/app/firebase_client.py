# app/firebase_client.py
import os
import json
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
from pathlib import Path

# ================== LOAD ENV ==================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ================== INIT FIREBASE (FIXED) ==================

DB_URL = os.getenv("FIREBASE_DB_URL")
SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if not DB_URL:
    raise RuntimeError("Thiếu FIREBASE_DB_URL trong environment")

if not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("Thiếu FIREBASE_SERVICE_ACCOUNT_JSON trong environment")

try:
    # 1. Nếu là đường dẫn file (Chạy Local)
    if os.path.exists(SERVICE_ACCOUNT_JSON):
        print(f"🔥 [Firebase] Đang dùng file credential: {SERVICE_ACCOUNT_JSON}")
        cred = credentials.Certificate(SERVICE_ACCOUNT_JSON)
    
    # 2. Nếu là chuỗi JSON (Chạy trên Render)
    else:
        print("🔥 [Firebase] Đang đọc credential từ Environment Variable")
        try:
            cred_dict = json.loads(SERVICE_ACCOUNT_JSON)
        except json.JSONDecodeError:
             # Nếu Render bị lỗi format JSON, thử clean string
            cleaned_json = SERVICE_ACCOUNT_JSON.strip("'").strip('"')
            cred_dict = json.loads(cleaned_json)

        # ===> ĐOẠN QUAN TRỌNG NHẤT: FIX LỖI PRIVATE KEY <===
        if "private_key" in cred_dict:
            # Thay thế ký tự \\n (hai dấu gạch) thành \n (xuống dòng thật)
            key = cred_dict["private_key"]
            cred_dict["private_key"] = key.replace("\\n", "\n")
        
        cred = credentials.Certificate(cred_dict)

except Exception as e:
    # In lỗi ra logs để debug
    print(f"❌ LỖI KHỞI TẠO FIREBASE: {str(e)}")
    raise RuntimeError(f"Firebase Init Error: {str(e)}")

# Khởi tạo App (tránh duplicate)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": DB_URL
    })

# ================== CẤU HÌNH NGƯỠNG CẢNH BÁO ==================

ALERT_TEMP_MAX = 35.0   # °C
ALERT_HUM_MAX = 80.0    # %

# ================== 1. SENSOR IOT ==================

def save_sensor(device_id: str, data: dict):
    """
    Lưu dữ liệu cảm biến và tạo cảnh báo nếu vượt ngưỡng
    """
    if not device_id or not data:
        return

    ref = db.reference(f"warehouse_data/{device_id}")
    ref.push(data)

    alerts_ref = db.reference(f"alerts/{device_id}")

    temp = data.get("temperature")
    hum = data.get("humidity")
    ts = data.get("iso_ts") or datetime.now(timezone.utc).isoformat()

    if temp is not None:
        try:
            if float(temp) > ALERT_TEMP_MAX:
                alerts_ref.push({
                    "message": f"Nhiệt độ vượt ngưỡng: {temp} °C",
                    "type": "danger",
                    "ts": ts
                })
        except ValueError:
            pass

    if hum is not None:
        try:
            if float(hum) > ALERT_HUM_MAX:
                alerts_ref.push({
                    "message": f"Độ ẩm vượt ngưỡng: {hum} %",
                    "type": "danger",
                    "ts": ts
                })
        except ValueError:
            pass

# ================== 2. SALES / DEMAND ==================

def save_sale(product_id: str, data: dict):
    if not product_id or not data:
        return
    ref = db.reference(f"sales_history/{product_id}")
    ref.push(data)


def get_sales_history(product_id: str, limit: int = 30):
    """
    Trả về list lịch sử bán hàng (an toàn, không bao giờ None)
    """
    if not product_id:
        return []

    ref = db.reference(f"sales_history/{product_id}")
    snap = ref.get()

    if not snap:
        return []

    items = list(snap.items())
    items.sort(key=lambda x: x[0])  # sort theo pushId
    values = [v for _, v in items]

    if limit and len(values) > limit:
        return values[-limit:]
    return values


# ================== 3. PRODUCT ==================

def get_product(product_id: str):
    if not product_id:
        return None
    ref = db.reference(f"products/{product_id}")
    return ref.get()


def save_product(product_id: str, data: dict):
    if not product_id or not data:
        return None
    ref = db.reference(f"products/{product_id}")
    ref.set(data)
    return data


def update_product(product_id: str, data: dict):
    if not product_id or not data:
        return None

    ref = db.reference(f"products/{product_id}")
    original = ref.get()
    if not original:
        return None

    original.update(data)
    ref.update(data)
    return original


def delete_product(product_id: str):
    if not product_id:
        return False
    ref = db.reference(f"products/{product_id}")
    if not ref.get():
        return False
    ref.delete()
    return True


def list_products():
    ref = db.reference("products")
    snap = ref.get()
    if not snap:
        return {}
    return snap


# ================== 4. DEMAND FORECAST ==================

def save_demand_forecast(product_id: str, forecast: list):
    """
    Lưu kết quả dự báo (chỉ lưu khi forecast hợp lệ)
    """
    if not product_id or not forecast:
        return

    ref = db.reference(f"forecast_results/{product_id}")
    ref.set({
        "last_run": datetime.now(timezone.utc).isoformat(),
        "horizon_days": len(forecast),
        "points": forecast
    })
