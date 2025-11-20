# HƯỚNG DẪN CHẠY USER SERVICE

## Yêu cầu

- Python 3.9 trở lên
- Neo4j Database (chạy trên bolt://localhost:7687)
- Media Service (chạy trên http://localhost:8090/media)

## Cài đặt

### 1. Tạo môi trường ảo

```bash
python -m venv venv
```

### 2. Kích hoạt môi trường ảo

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```bash
copy .env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

MEDIA_SERVICE_URL=http://localhost:8090/media
DEFAULT_AVATAR=http://localhost:8888/api/v1/media/download/9963eeb2-e8fd-4aef-9585-3f605adc0e7f.png
```

## Chạy ứng dụng

```bash
python app.py
```

Service sẽ chạy trên `http://localhost:8081`

## API Endpoints

### Public Endpoints (Internal - không cần authentication)

**1. Tạo user profile mới**
```
POST /users/internal
Content-Type: application/json

{
    "id": "user-id",
    "username": "username",
    "fullName": "Full Name",
    "email": "email@example.com"
}
```

**2. Lấy profile theo username**
```
GET /users/internal/{username}
```

### Protected Endpoints (Cần JWT token)

**3. Lấy profile theo user ID**
```
GET /users/{userId}
Authorization: Bearer {token}
```

**4. Lấy profile của user hiện tại**
```
GET /users/me
Authorization: Bearer {token}
```

**5. Cập nhật profile**
```
PUT /users/me
Authorization: Bearer {token}
Content-Type: application/json

{
    "fullName": "New Name",
    "bio": "My bio",
    "location": "Vietnam",
    "website": "https://example.com"
}
```

**6. Cập nhật avatar**
```
PUT /users/me/avatar
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary file]
```

## Cấu trúc dự án

```
user-service/
├── app.py                      # Entry point
├── config.py                   # Configuration
├── extensions.py               # Extensions (Neo4j)
├── application.yaml            # Application config
├── requirements.txt            # Dependencies
├── models/
│   └── models.py              # UserProfile model
├── dto/
│   ├── requests.py            # Request DTOs
│   └── responses.py           # Response DTOs
├── repositories/
│   └── repositories.py        # Neo4j operations
├── services/
│   └── user_profile_service.py # Business logic
├── routes/
│   ├── profile_routes.py      # User endpoints
│   └── internal_routes.py     # Internal endpoints
├── clients/
│   └── media_client.py        # Media service client
├── exceptions/
│   ├── exceptions.py          # Custom exceptions
│   └── error_handler.py       # Error handlers
└── utils/
    └── jwt_service.py         # JWT utilities
```

## Migration từ Java Spring Boot

Service này được migrate từ Java Spring Boot sang Python Flask với:
- ✅ Giữ nguyên logic nghiệp vụ
- ✅ Giữ nguyên API endpoints
- ✅ Giữ nguyên cấu trúc dữ liệu
- ✅ Giữ nguyên cách xác thực JWT
- ✅ Sử dụng Neo4j database
- ✅ Tích hợp với Media Service

## Lưu ý

1. Đảm bảo Neo4j đã chạy trước khi start service
2. Đảm bảo Media Service đã chạy nếu cần upload avatar
3. JWT token phải được cung cấp trong header Authorization cho các protected endpoints
4. Internal endpoints (/users/internal/*) không cần authentication

## Troubleshooting

**Lỗi kết nối Neo4j:**
- Kiểm tra Neo4j có đang chạy không
- Kiểm tra thông tin đăng nhập trong `.env`

**Lỗi upload avatar:**
- Kiểm tra Media Service có đang chạy không
- Kiểm tra MEDIA_SERVICE_URL trong `.env`

**Lỗi JWT:**
- Kiểm tra token có được gửi đúng format: `Bearer {token}`
- Kiểm tra token có hợp lệ không
