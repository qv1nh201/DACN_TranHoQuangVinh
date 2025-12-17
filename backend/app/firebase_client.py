import os
import json
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# ================== LOAD ENV (Dự phòng) ==================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# PHẦN CẤU HÌNH QUAN TRỌNG NHẤT (SỬA Ở ĐÂY)
# ==============================================================================

# 1. Dán nội dung file 'quanlykho-xxx.json' của bạn vào giữa 3 dấu nháy kép bên dưới
# (Xóa dòng "PASTE_NOI_DUNG_FILE_JSON_VAO_DAY" và dán đè lên)
RAW_KEY_JSON = """
PASTE_NOI_DUNG_FILE_JSON_VAO_DAY
"""

# 2. Điền link Realtime Database của bạn vào đây
# (Ví dụ: "https://quanlykho-78a98-default-rtdb.asia-southeast1.firebasedatabase.app/")
HARDCODED_DB_URL = "https://YOUR_PROJECT_ID-default-rtdb.asia-southeast1.firebasedatabase.app/"

# ================== INIT FIREBASE ==================

try:
    if not firebase_admin._apps:
        cred = None
        
        # Kiểm tra xem người dùng đã dán key chưa
        if "PASTE_NOI_DUNG" not in RAW_KEY_JSON and len(RAW_KEY_JSON.strip()) > 10:
            print("🔥 [Direct] Đang dùng chìa khóa dán trực tiếp trong code...")
            cred_dict = json.loads(RAW_KEY_JSON)
            cred = credentials.Certificate(cred_dict)
        else:
            # Nếu chưa dán, thử tìm file local (Dự phòng cho máy local)
            print("⚠️ Chưa dán key vào RAW_KEY_JSON, đang tìm file local...")
            local_key_path = Path(__file__).parent / "firebase_key.json"
            env_key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            
            if local_key_path.exists():
                cred = credentials.Certificate(str(local_key_path))
            elif env_key_path and os.path.exists(env_key_path):
                cred = credentials.Certificate(env_key_path)

        if cred:
            # Ưu tiên dùng URL cứng, nếu không có thì lấy từ env
            final_db_url = HARDCODED_DB_URL if "YOUR_PROJECT_ID" not in HARDCODED_DB_URL else os.getenv("FIREBASE_DB_URL")
            
            if not final_db_url:
                raise ValueError("Chưa cấu hình FIREBASE_DB_URL!")

            firebase_admin.initialize_app(cred, {
                "databaseURL": final_db_url
            })
            print("✅ Firebase kết nối thành công!")
        else:
            print("❌ LỖI: Không tìm thấy chứng chỉ Firebase nào (Chưa dán Key hoặc thiếu file)!")

except Exception as e:
    print(f"❌ FIREBASE INIT ERROR: {str(e)}")
    pass

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
    # Sort theo pushId (thời gian thêm vào)
    items.sort(key=lambda x: x[0])  
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