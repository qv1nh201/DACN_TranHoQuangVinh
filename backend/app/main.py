# app/main.py
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .firebase_client import (
    save_sensor,
    save_sale,
    get_sales_history,
    get_product,
    save_demand_forecast,
)
from .ai_client import forecast_demand


app = FastAPI(
    title="Smart Warehouse Backend",
    description="IoT giám sát kho & AI dự báo nhu cầu",
    version="1.0.0",
)

# Cho phép gọi từ các web dashboard (file html mở trực tiếp)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========= Pydantic models =========

class SensorPayload(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    iso_ts: Optional[str] = None


class SalePayload(BaseModel):
    product_id: str
    qty: float
    ts: Optional[str] = None   # nếu không gửi, server sẽ tự gán


# ========= Routes cơ bản =========

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Smart Warehouse Backend running"
    }


# ========= 1. IoT sensor API =========

@app.post("/api/sensor")
def api_sensor(payload: SensorPayload):
    ts = payload.iso_ts or datetime.now(timezone.utc).isoformat()
    data = {
        "temperature": payload.temperature,
        "humidity": payload.humidity,
        "iso_ts": ts,
    }
    save_sensor(payload.device_id, data)
    return {"status": "sensor_saved", "device_id": payload.device_id, "data": data}


# ========= 2. Bán hàng / xuất kho =========

@app.post("/api/sales")
def api_sales(payload: SalePayload):
    ts = payload.ts or datetime.now(timezone.utc).isoformat()
    data = {
        "qty": payload.qty,
        "ts": ts,
    }
    save_sale(payload.product_id, data)
    return {"status": "sale_saved", "product_id": payload.product_id, "data": data}


# ========= 3. Lấy thông tin sản phẩm =========

@app.get("/api/products/{product_id}")
def api_get_product(product_id: str):
    product = get_product(product_id)
    if not product:
        return {"status": "not_found", "product_id": product_id}
    return {"status": "ok", "product_id": product_id, "product": product}


# ========= 4. AI dự báo nhu cầu =========

@app.get("/api/demand_forecast/{product_id}")
def api_demand_forecast(product_id: str, limit: int = 30, horizon: int = 7):
    """
    Dự báo nhu cầu cho 1 sản phẩm:
    - Lấy lịch sử bán trong 'limit' ngày gần đây
    - Dùng AI (Moving Average) để dự báo 'horizon' ngày tới
    - So sánh với tồn kho hiện tại => gợi ý nhập hàng
    """

    history = get_sales_history(product_id, limit)
    forecast = forecast_demand(history, horizon_days=horizon)

    product = get_product(product_id)
    current_stock = None
    safety_stock = None
    if product:
        current_stock = float(product.get("current_stock", 0))
        safety_stock = float(product.get("safety_stock", 0))

    recommendation = None
    if current_stock is not None and forecast:
        total_demand = sum(p["expected_qty"] for p in forecast)
        if current_stock < total_demand + (safety_stock or 0):
            shortage = total_demand + (safety_stock or 0) - current_stock
            recommendation = {
                "should_reorder": True,
                "suggest_reorder_qty": round(shortage, 2),
                "reason": "Tồn kho + tồn kho an toàn < tổng nhu cầu dự báo."
            }
        else:
            recommendation = {
                "should_reorder": False,
                "reason": "Tồn kho hiện tại đủ đáp ứng nhu cầu dự báo."
            }

    # Lưu kết quả vào Firebase để dashboard khác có thể đọc
    save_demand_forecast(product_id, forecast)

    return {
        "status": "ok",
        "product_id": product_id,
        "history_len": len(history),
        "forecast": forecast,
        "current_stock": current_stock,
        "safety_stock": safety_stock,
        "recommendation": recommendation,
    }
class ProductCreate(BaseModel):
    name: str
    current_stock: float = 0
    safety_stock: float = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    current_stock: Optional[float] = None
    safety_stock: Optional[float] = None


from .firebase_client import (
    list_products,
    save_product,
    update_product,
    delete_product
)

# Lấy danh sách sản phẩm
@app.get("/api/products")
def api_list_products():
    products = list_products()
    return {
        "status": "ok",
        "total": len(products),
        "products": products
    }


# Tạo mới sản phẩm
@app.post("/api/products/{product_id}")
def api_create_product(product_id: str, payload: ProductCreate):
    data = payload.dict()
    save_product(product_id, data)
    return {
        "status": "created",
        "product_id": product_id,
        "data": data
    }


# Cập nhật sản phẩm
@app.put("/api/products/{product_id}")
def api_update_product(product_id: str, payload: ProductUpdate):
    updated = update_product(product_id, payload.dict(exclude_unset=True))
    if not updated:
        return {"status": "not_found", "product_id": product_id}
    
    return {
        "status": "updated",
        "product_id": product_id,
        "data": updated
    }


# Xóa sản phẩm
@app.delete("/api/products/{product_id}")
def api_delete_product_route(product_id: str):
    ok = delete_product(product_id)
    if not ok:
        return {"status": "not_found", "product_id": product_id}
    
    return {
        "status": "deleted",
        "product_id": product_id
    }