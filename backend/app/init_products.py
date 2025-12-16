# File: init_products.py
# Chạy file này để tạo các sản phẩm mẫu vào Firebase

from app.firebase_client import save_product

print("Đang khởi tạo sản phẩm...")

# 1. Tạo Product A (Mẫu)
save_product("productA", {
    "name": "Gạo ST25 (Mẫu)",
    "current_stock": 100,
    "safety_stock": 20,
    "price": 250000
})

# 2. Tạo Product B (Để bạn test cái lỗi trong hình)
save_product("productB", {
    "name": "Sản phẩm B (Test)",
    "current_stock": 50,
    "safety_stock": 10,
    "price": 50000
})

# 3. Tạo con Aula F75 (Như bạn muốn bán)
save_product("aula_f75", {
    "name": "Bàn phím Aula F75",
    "current_stock": 5,      # Ví dụ: bạn đang có 5 cái
    "safety_stock": 2,       # Còn 2 cái là báo nhập hàng
    "price": 850000
})

print("✅ Đã tạo xong! Giờ bạn quay lại Web F5 và test được rồi.")