# Hướng dẫn Deploy Backend lên Render

## Bước 1: Chuẩn bị

1. Push code lên GitHub (nếu chưa có)
2. Đảm bảo các file sau tồn tại:
   - `backend/requirement.txt`
   - `backend/app/main.py`
   - `backend/app/firebase_client.py`

## Bước 2: Tạo Web Service trên Render

1. Truy cập https://render.com và đăng nhập
2. Click **"New +"** → **"Web Service"**
3. Kết nối với GitHub repository của bạn

## Bước 3: Cấu hình Web Service

### Build & Start Commands:

**Build Command:**
```bash
cd backend && pip install -r requirement.txt
```

**Start Command:**
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment:
- **Environment**: `Python 3`
- **Region**: `Singapore` (gần Việt Nam nhất)
- **Plan**: `Free`

### Advanced Settings (nếu cần):
- **Python Version**: `3.11.0`
- **Auto-Deploy**: Bật để tự động deploy khi push code mới

## Bước 4: Kiểm tra Logs

Sau khi deploy, kiểm tra logs để đảm bảo Firebase kết nối thành công:

✅ Logs tốt:
```
🔥 [Direct] Đang khởi tạo Firebase với Key đã làm sạch...
✅ Firebase kết nối thành công! (Key hợp lệ)
```

❌ Nếu có lỗi:
```
❌ FIREBASE INIT ERROR: ...
```
→ Copy full error message và debug

## Bước 5: Test API

Sau khi deploy xong, lấy URL từ Render (ví dụ: `https://your-app.onrender.com`)

**Test các endpoints:**

1. **Health Check:**
   ```bash
   curl https://your-app.onrender.com/
   ```

2. **List Products:**
   ```bash
   curl https://your-app.onrender.com/api/products
   ```

3. **Get Product:**
   ```bash
   curl https://your-app.onrender.com/api/products/PRODUCT001
   ```

## Bước 6: Cập nhật CORS trong code

Sau khi có URL Render, cập nhật trong `backend/app/main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.vercel.app",  # Frontend của bạn
    "https://your-backend.onrender.com", # Backend Render (nếu cần)
],
```

## Common Issues (Lỗi thường gặp)

### 1. "Module not found"
- Kiểm tra `requirement.txt` có đầy đủ dependencies
- Build command phải `cd backend` trước khi `pip install`

### 2. "Firebase connection failed"
- Kiểm tra logs xem có message lỗi Firebase
- Đảm bảo private key trong code không bị lỗi format

### 3. "Product not found" nhưng có trong Firebase
- Kiểm tra Firebase Rules: phải allow read/write
- Kiểm tra Database URL có đúng region không (asia-southeast1)

### 4. API trả về lỗi CORS
- Cập nhật `allow_origins` với URL chính xác của frontend
- Không có dấu `/` ở cuối URL

## Tips

- **Free tier của Render sẽ sleep sau 15 phút không hoạt động**
  → Request đầu tiên sẽ mất ~30s để wake up
  → Dùng UptimeRobot.com để ping giữ cho service luôn active

- **Logs realtime:**
  → Render Dashboard → Your Service → Logs

- **Redeploy:**
  → Push code mới lên GitHub → Auto deploy
  → Hoặc click "Manual Deploy" trên Render
