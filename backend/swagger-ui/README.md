# Swagger UI - Recipe Sharing System API Documentation

Giao diện tương tác để xem và test API của Recipe Sharing System.

## 📋 Mô tả

Service này cung cấp Swagger UI để:
- Xem tài liệu API đầy đủ
- Test các endpoint trực tiếp trên trình duyệt
- Xem request/response schema
- Thử nghiệm với authentication (JWT Bearer token)

## 🚀 Cài đặt và Chạy

### 1. Cài đặt dependencies

```bash
# Di chuyển vào thư mục swagger-ui
cd backend/swagger-ui

# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### 2. Cấu hình (Tùy chọn)

Tạo file `.env` từ `.env.example`:

```bash
copy .env.example .env  # Windows
# hoặc
cp .env.example .env    # Linux/Mac
```

Chỉnh sửa file `.env` nếu cần:

```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000
```

### 3. Chạy server

```bash
# Cách 1: Sử dụng Python trực tiếp
python app.py

# Cách 2: Sử dụng Flask CLI
flask run
```

Server sẽ chạy tại: **http://localhost:5000**

## 🌐 Truy cập Swagger UI

Sau khi chạy server, mở trình duyệt và truy cập:

```
http://localhost:5000/api/docs
```

hoặc đơn giản:

```
http://localhost:5000/
```

## 🔐 Sử dụng Authentication

Để test các endpoint yêu cầu authentication:

1. **Đăng nhập để lấy token:**
   - Mở endpoint `/auth/login` trong Swagger UI
   - Click "Try it out"
   - Nhập email và password
   - Click "Execute"
   - Copy `accessToken` từ response

2. **Thêm token vào Swagger UI:**
   - Click nút "Authorize" 🔒 ở đầu trang
   - Nhập: `Bearer <accessToken>` (thay `<accessToken>` bằng token vừa copy)
   - Click "Authorize"
   - Click "Close"

3. **Test các endpoint cần authentication:**
   - Bây giờ bạn có thể test các endpoint có biểu tượng 🔒

## 📖 Cấu trúc Project

```
swagger-ui/
├── app.py                  # Flask application chính
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables mẫu
├── README.md              # File này
└── static/
    └── openapi.yaml       # OpenAPI specification
```

## 🛠️ Tùy chỉnh

### Thay đổi port

Sửa file `.env`:

```env
PORT=8080
```

### Cập nhật OpenAPI spec

Nếu bạn thay đổi file `openapi.yaml` gốc, hãy copy lại vào thư mục static:

```bash
# Windows PowerShell
Copy-Item "../../openapi.yaml" -Destination "static/openapi.yaml"

# Linux/Mac
cp ../../openapi.yaml static/openapi.yaml
```

Sau đó refresh trình duyệt để thấy thay đổi.

## 📝 Các endpoint có sẵn

Swagger UI hiển thị tất cả các microservices:

- **Authentication Service** - Đăng ký, đăng nhập, JWT tokens
- **User Service** - Quản lý thông tin người dùng
- **Recipe Service** - CRUD công thức nấu ăn
- **Category Service** - Quản lý danh mục
- **Tag Service** - Quản lý tags
- **Comment Service** - Bình luận
- **Rating Service** - Đánh giá
- **Favorite Service** - Yêu thích
- **Follow Service** - Theo dõi người dùng
- **Search Service** - Tìm kiếm
- **Media Service** - Upload file/hình ảnh
- **Health Service** - Quản lý hồ sơ bệnh án
- **AI Recommendation Service** - Gợi ý món ăn bằng AI
- **Notification Service** - Thông báo realtime

## ⚠️ Lưu ý

1. **API Gateway:** Các endpoint trong OpenAPI spec đều route qua API Gateway tại `http://localhost:8888/api/v1`
2. **CORS:** Nếu gặp lỗi CORS khi test, đảm bảo các microservices đã cấu hình CORS đúng
3. **Token expiry:** JWT token có thể hết hạn. Nếu gặp lỗi 401, hãy đăng nhập lại để lấy token mới
4. **Microservices:** Đảm bảo các microservices backend đã chạy trước khi test

## 🐛 Troubleshooting

### Lỗi: "ModuleNotFoundError"

```bash
# Đảm bảo đã cài đặt dependencies
pip install -r requirements.txt
```

### Lỗi: "Port already in use"

```bash
# Thay đổi port trong file .env
PORT=5001
```

### Swagger UI không hiển thị

```bash
# Kiểm tra file openapi.yaml đã tồn tại
ls static/openapi.yaml  # Linux/Mac
dir static\openapi.yaml # Windows
```

## 📞 API Gateway URLs

- **API Gateway:** http://localhost:8888/api/v1
- **Swagger UI:** http://localhost:5000/api/docs
- **Health Check:** http://localhost:5000/health

## 🎯 Tips sử dụng

1. **Filtering:** Sử dụng ô search ở đầu Swagger UI để tìm endpoint nhanh
2. **Try it out:** Click "Try it out" để test endpoint với data thực
3. **Models:** Click vào các schema model để xem chi tiết cấu trúc data
4. **Copy curl:** Sau khi execute, bạn có thể copy curl command để dùng trong terminal

---

**Phát triển bởi:** Recipe Sharing System Team  
**Version:** 1.0.0  
**Last updated:** December 2025
