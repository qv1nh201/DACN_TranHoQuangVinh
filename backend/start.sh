#!/bin/bash

# Script khởi động cho Render
echo "🚀 Starting Smart Warehouse Backend..."

# Di chuyển vào thư mục backend
cd backend

# Kiểm tra Python version
python --version

# Cài đặt dependencies
echo "📦 Installing dependencies..."
pip install -r requirement.txt

# Khởi động server
echo "🔥 Starting Uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
