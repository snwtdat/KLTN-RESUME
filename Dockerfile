# Sử dụng Python 3.11 bản nhẹ
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết cho Tesseract OCR và xử lý PDF
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn (bao gồm file code, thư mục Model AI) vào container
COPY . .

# Mở cổng 8000 cho FastAPI
EXPOSE 8000

# Lệnh khởi chạy server
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8000"]