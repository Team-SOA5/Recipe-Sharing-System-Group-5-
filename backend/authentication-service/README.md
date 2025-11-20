# Authentication Service (Python Flask)

Đây là service xác thực được viết lại từ Java Spring Boot sang Python Flask, giữ nguyên logic nghiệp vụ và luồng xử lý.

## Tính năng

- Đăng ký tài khoản mới
- Đăng nhập (Authentication)
- Làm mới token (Refresh Token)
- Xác thực token (Introspect)
- Đăng xuất (Logout)
- JWT Authentication với Access Token và Refresh Token

## Cấu trúc dự án

```
authentication-service/
├── app.py                      # Entry point của ứng dụng
├── config.py                   # Cấu hình ứng dụng
├── extensions.py               # Flask extensions (SQLAlchemy, Bcrypt)
├── requirements.txt            # Dependencies
├── .env.example               # File mẫu biến môi trường
├── models/                    # Database models (Entity)
│   └── models.py
├── repositories/              # Data access layer
│   └── repositories.py
├── services/                  # Business logic layer
│   ├── authentication_service.py
│   └── user_service.py
├── routes/                    # Controllers/API endpoints
│   └── auth_routes.py
├── dto/                       # Data Transfer Objects
│   ├── requests.py
│   └── responses.py
├── exceptions/                # Exception handling
│   ├── exceptions.py
│   └── error_handler.py
├── utils/                     # Utilities
│   ├── jwt_service.py
│   ├── validators.py
│   └── init_data.py
├── clients/                   # HTTP clients
│   └── user_profile_client.py
└── constants/                 # Constants
    └── constants.py
```

## Cài đặt

1. Tạo virtual environment:
```bash
python -m venv venv
```

2. Kích hoạt virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Tạo file `.env` từ `.env.example` và cấu hình:
```bash
cp .env.example .env
```

5. Chỉnh sửa file `.env` với thông tin database của bạn:
```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/cookpad-identity
```

## Chạy ứng dụng

```bash
python app.py
```

Service sẽ chạy tại: `http://localhost:8080`

## API Endpoints

### 1. Đăng ký
```
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "username": "username",
    "fullName": "Full Name"
}
```

### 2. Đăng nhập
```
POST /auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}
```

### 3. Làm mới token
```
POST /auth/refresh-token
Content-Type: application/json

{
    "accessToken": "...",
    "refreshToken": "..."
}
```

### 4. Xác thực token
```
POST /auth/introspect
Content-Type: application/json

{
    "accessToken": "..."
}
```

### 5. Đăng xuất
```
POST /auth/logout
Content-Type: application/json

{
    "accessToken": "...",
    "refreshToken": "..."
}
```

## Cấu hình mặc định

- **Database**: MySQL `cookpad-identity`
- **Port**: 8080
- **Access Token Duration**: 1000 giây
- **Refresh Token Duration**: 30000 giây
- **Admin User**: 
  - Email: `admin@gmail.com`
  - Password: `admin12345` (Nên thay đổi sau khi khởi tạo)

## Lưu ý

- Service này cần kết nối với `user-service` (profile service) để tạo profile người dùng
- Đảm bảo MySQL đã được cài đặt và database `cookpad-identity` đã được tạo
- JWT signer key nên được thay đổi trong môi trường production
- Logic nghiệp vụ và luồng xử lý giữ nguyên như phiên bản Java Spring Boot

## Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: MySQL với SQLAlchemy ORM
- **Authentication**: JWT (PyJWT)
- **Password Hashing**: Bcrypt
- **HTTP Client**: Requests
