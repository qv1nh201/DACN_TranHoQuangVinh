# app/firebase_client.py
import os
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# ================== LOAD .ENV & KHỞI TẠO FIREBASE ==================

# Thư mục backend (parent của app/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load file .env trong thư mục backend
load_dotenv(BASE_DIR / ".env")

# Lấy path service account & URL DB
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
db_url = os.getenv("FIREBASE_DB_URL")

if not cred_path:
    raise RuntimeError("Chưa set GOOGLE_APPLICATION_CREDENTIALS trong file .env")

if not db_url:
    raise RuntimeError("Chưa set FIREBASE_DB_URL trong file .env")

# Nếu cred_path là đường dẫn tương đối -> convert sang tuyệt đối trong backend
cred_path = Path(cred_path)
if not cred_path.is_absolute():
    cred_path = (BASE_DIR / cred_path).resolve()

if not cred_path.is_file():
    raise RuntimeError(f"Không tìm thấy file service account: {cred_path}")

# Khởi tạo Firebase Admin SDK
cred = credentials.Certificate(str(cred_path))
firebase_admin.initialize_app(cred, {
    "databaseURL": db_url
})

# ================== CÁC NGƯỠNG CẢNH BÁO CƠ BẢN ==================

ALERT_TEMP_MAX = 35.0   # °C
ALERT_HUM_MAX = 80.0    # %

# ================== 1. HÀM LIÊN QUAN ĐẾN SENSOR IOT ==================

def save_sensor(device_id: str, data: dict):
    """
    Lưu dữ liệu cảm biến từ ESP32 vào:
      warehouse_data/{device_id}/...
    Đồng thời tạo cảnh báo nếu vượt ngưỡng nhiệt độ / độ ẩm.
    """
    # Lưu data sensor
    ref = db.reference(f"warehouse_data/{device_id}")
    ref.push(data)

    # Chuẩn bị node cảnh báo
    alerts_ref = db.reference(f"alerts/{device_id}")

    temp = data.get("temperature")
    hum = data.get("humidity")
    ts = data.get("iso_ts") or datetime.now(timezone.utc).isoformat()

    # Cảnh báo nhiệt độ
    if temp is not None and float(temp) > ALERT_TEMP_MAX:
        alerts_ref.push({
            "message": f"Nhiệt độ vượt ngưỡng: {temp} °C",
            "type": "danger",
            "ts": ts
        })

    # Cảnh báo độ ẩm
    if hum is not None and float(hum) > ALERT_HUM_MAX:
        alerts_ref.push({
            "message": f"Độ ẩm vượt ngưỡng: {hum} %",
            "type": "danger",
            "ts": ts
        })


# ================== 2. HÀM LIÊN QUAN ĐẾN BÁN HÀNG / NHU CẦU ==================

def save_sale(product_id: str, data: dict):
    """
    Lưu một bản ghi bán hàng / xuất kho vào:
      sales_history/{product_id}/...
    data ví dụ: { "qty": 10, "ts": "2025-11-14T10:00:00Z" }
    """
    ref = db.reference(f"sales_history/{product_id}")
    ref.push(data)


def get_sales_history(product_id: str, limit: int = 30):
    """
    Lấy lịch sử bán/nhu cầu gần đây của một sản phẩm.
    Vì Firebase Admin SDK không có limit_to_last nên ta lấy hết rồi cắt cuối cùng.
    """
    ref = db.reference(f"sales_history/{product_id}")
    snap = ref.get()
    if not snap:
        return []

    # snap là dict {pushId: {...}}, chuyển sang list và sort theo key cho ổn định
    items = list(snap.items())
    items.sort(key=lambda x: x[0])       # sort theo pushId (xấp xỉ theo thời gian)
    values = [v for _, v in items]

    if limit and len(values) > limit:
        return values[-limit:]          # lấy limit bản ghi cuối cùng
    return values


def get_product(product_id: str):
    """
    Lấy thông tin sản phẩm tại:
      products/{product_id}
    Ví dụ:
      { "name": "Gạo ST25", "current_stock": 200, "safety_stock": 100 }
    """
    ref = db.reference(f"products/{product_id}")
    return ref.get()


def save_demand_forecast(product_id: str, forecast: list):
    """
    Lưu kết quả dự báo nhu cầu của AI vào:
      forecast_results/{product_id}
    """
    ref = db.reference(f"forecast_results/{product_id}")
    ref.set({
        "last_run": datetime.now(timezone.utc).isoformat(),
        "horizon_days": len(forecast),
        "points": forecast,
    })
def save_product(product_id: str, data: dict):
    """
    Tạo hoặc cập nhật 1 sản phẩm:
      products/{product_id}
    """
    ref = db.reference(f"products/{product_id}")
    ref.set(data)
    return data


def update_product(product_id: str, data: dict):
    """
    Cập nhật một phần sản phẩm.
    """
    ref = db.reference(f"products/{product_id}")
    original = ref.get()
    if not original:
        return None

    original.update(data)
    ref.update(data)
    return original


def delete_product(product_id: str):
    ref = db.reference(f"products/{product_id}")
    if not ref.get():
        return False
    ref.delete()
    return True


def list_products():
    """
    Lấy tất cả sản phẩm trong /products
    """
    ref = db.reference("products")
    snap = ref.get()
    if not snap:
        return {}
    return snap
