# HƯỚNG DẪN CHẠY TAG SERVICE

## Yêu cầu hệ thống

- Python 3.8 trở lên
- MongoDB 4.0 trở lên (đã chạy tại localhost:27017)
- pip (Python package manager)

## Các bước cài đặt và chạy

### Bước 1: Tạo và kích hoạt Virtual Environment

**Trên Windows:**

```powershell
# Di chuyển vào thư mục tag-service
cd Flask_project\tag-service

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
venv\Scripts\activate
```

**Trên Linux/Mac:**

```bash
# Di chuyển vào thư mục tag-service
cd Flask_project/tag-service

# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate
```

### Bước 2: Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình môi trường

1. Copy file `.env.example` thành `.env`:

**Windows:**
```powershell
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

2. Chỉnh sửa file `.env` nếu cần:

```env
# Cổng server (mặc định: 8084)
SERVER_PORT=8084

# Tên ứng dụng
APPLICATION_NAME=tag-service

# MongoDB connection string
# Thay đổi nếu MongoDB của bạn chạy ở địa chỉ khác
MONGODB_URI=mongodb://root:root@localhost:27017/tag-service?authSource=admin
MONGODB_AUTO_INDEX_CREATION=true

# JWT Secret Key (nên thay đổi trong production)
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Chế độ debug (True cho development, False cho production)
DEBUG=True
```

### Bước 4: Đảm bảo MongoDB đang chạy

**Windows:**
```powershell
# Kiểm tra MongoDB service
net start MongoDB
```

**Linux:**
```bash
# Kiểm tra MongoDB service
sudo systemctl status mongod

# Nếu chưa chạy, khởi động MongoDB
sudo systemctl start mongod
```

**Mac:**
```bash
# Kiểm tra MongoDB service
brew services list

# Nếu chưa chạy, khởi động MongoDB
brew services start mongodb-community
```

### Bước 5: Chạy ứng dụng

```bash
python app.py
```

Nếu thành công, bạn sẽ thấy:

```
Starting Tag Service on port 8084...
Debug mode: True
MongoDB URI: mongodb://root:root@localhost:27017/tag-service?authSource=admin
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:8084
```

### Bước 6: Kiểm tra ứng dụng

Mở trình duyệt hoặc dùng curl:

```bash
# Kiểm tra health check
curl http://localhost:8084/health

# Kết quả mong đợi:
# {"service":"tag-service","status":"UP"}
```

## Các lệnh thường dùng

### Chạy ở chế độ development

```bash
python app.py
```

### Chạy với Flask CLI

```bash
# Windows PowerShell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run --port 8084

# Linux/Mac
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port 8084
```

### Tắt ứng dụng

Nhấn `Ctrl + C` trong terminal

### Tắt virtual environment

```bash
deactivate
```

## Test các API

### 1. Lấy danh sách tag phổ biến

```bash
curl http://localhost:8084/tags/popular?limit=10
```

### 2. Tìm kiếm tag

```bash
curl "http://localhost:8084/tags?search=vietnam&limit=5"
```

### 3. Tạo tag mới (cần JWT token)

```bash
curl -X POST http://localhost:8084/tags \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Vietnamese\"}"
```

**Lưu ý:** Để tạo tag, bạn cần có JWT token hợp lệ từ authentication service.

## Xử lý lỗi thường gặp

### Lỗi 1: MongoDB không kết nối được

```
pymongo.errors.ServerSelectionTimeoutError
```

**Giải pháp:**
- Kiểm tra MongoDB đã chạy chưa
- Kiểm tra connection string trong file `.env`
- Kiểm tra username/password MongoDB

### Lỗi 2: Module không tìm thấy

```
ModuleNotFoundError: No module named 'flask'
```

**Giải pháp:**
- Kiểm tra virtual environment đã được kích hoạt chưa
- Chạy lại: `pip install -r requirements.txt`

### Lỗi 3: Port đã được sử dụng

```
OSError: [Errno 98] Address already in use
```

**Giải pháp:**
- Thay đổi port trong file `.env`: `SERVER_PORT=8085`
- Hoặc dừng ứng dụng đang chạy ở port 8084

### Lỗi 4: Import error

```
ImportError: cannot import name 'mongo' from 'extensions'
```

**Giải pháp:**
- Kiểm tra tất cả file `__init__.py` đã được tạo
- Kiểm tra cấu trúc thư mục
- Chạy lại từ thư mục tag-service

## Cấu trúc thư mục

```
tag-service/
├── app.py                    # File chính để chạy
├── config.py                 # Cấu hình
├── extensions.py             # MongoDB extension
├── requirements.txt          # Danh sách thư viện
├── .env                      # Biến môi trường (tự tạo)
├── .env.example             # Mẫu file .env
├── models/                   # Định nghĩa model
├── repositories/             # Truy vấn database
├── services/                 # Logic nghiệp vụ
├── routes/                   # API endpoints
├── dto/                      # Data Transfer Objects
├── exceptions/               # Xử lý lỗi
├── utils/                    # Utilities (JWT, etc.)
└── constants/                # Hằng số
```

## Lưu ý

1. **Virtual environment:** Luôn kích hoạt virtual environment trước khi chạy
2. **MongoDB:** Đảm bảo MongoDB đang chạy trước khi start service
3. **Port:** Mặc định service chạy ở port 8084 (giống Java version)
4. **Authentication:** Endpoint POST `/tags` yêu cầu JWT token
5. **Public endpoints:** GET `/tags` và `/tags/popular` không cần authentication

## Tích hợp với các service khác

Service này được thiết kế để hoạt động với:
- **authentication-service**: Để lấy JWT token
- **API Gateway**: Để route requests
- **Other services**: Các service khác có thể gọi API của tag-service

Đảm bảo tất cả services đều sử dụng cùng JWT secret key và thuật toán.
