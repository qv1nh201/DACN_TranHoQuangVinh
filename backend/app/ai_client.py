# app/ai_client.py
from typing import List, Dict


def forecast_demand(history_points: List[Dict], horizon_days: int = 7) -> List[Dict]:
    """
    Mô-đun 'AI' dự báo nhu cầu (qty bán) cho sản phẩm.

    history_points: danh sách bản ghi lịch sử dạng:
      { "qty": 12, "ts": "2025-11-10T00:00:00Z", ... }

    Ở đây dùng Moving Average đơn giản:
    - Lấy trung bình qty lịch sử
    - Dự báo horizon_days tiếp theo với giá trị ≈ trung bình đó
    """

    if not history_points:
        return []

    qty_list = []
    for item in history_points:
        q = item.get("qty")
        if q is None:
            continue
        try:
            qty_list.append(float(q))
        except (TypeError, ValueError):
            continue

    if not qty_list:
        return []

    avg = sum(qty_list) / len(qty_list)

    forecast = []
    for d in range(1, horizon_days + 1):
        forecast.append({
            "day_offset": d,                # ngày thứ d trong tương lai
            "expected_qty": round(avg, 2)   # nhu cầu dự kiến
        })

    return forecast
