# User Service

User Profile Service được migrate từ Java Spring Boot sang Python Flask.

## Tính năng

- Quản lý thông tin profile người dùng
- Lưu trữ dữ liệu trong Neo4j
- Tích hợp với Media Service để upload avatar
- JWT authentication
- RESTful API endpoints

## Công nghệ

- Python 3.9+
- Flask
- Neo4j Database
- JWT Authentication
- Requests (HTTP Client)

## Cấu trúc thư mục

```
user-service/
├── app.py                  # Entry point
├── config.py              # Configuration
├── extensions.py          # Extensions (Neo4j)
├── application.yaml       # Application config
├── requirements.txt       # Dependencies
├── models/               # Data models
├── dto/                  # DTOs (requests/responses)
├── repositories/         # Data access layer
├── services/            # Business logic
├── routes/              # API routes
├── clients/             # HTTP clients
├── exceptions/          # Custom exceptions
└── utils/               # Utilities (JWT, etc.)
```

## API Endpoints

### Public Endpoints (Internal)
- `POST /users/internal` - Tạo user profile mới
- `GET /users/internal/{username}` - Lấy profile theo username

### Protected Endpoints
- `GET /users/{userId}` - Lấy profile theo user ID
- `GET /users/me` - Lấy profile của user hiện tại
- `PUT /users/me` - Cập nhật profile
- `PUT /users/me/avatar` - Cập nhật avatar

## Cài đặt và chạy

Xem file `HUONG_DAN_CHAY.md` để biết chi tiết.
