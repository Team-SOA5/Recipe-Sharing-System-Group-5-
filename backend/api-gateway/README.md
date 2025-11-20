# API Gateway - Python Flask

API Gateway được viết bằng Python Flask, chuyển đổi từ Spring Cloud Gateway.

## Tính năng

- **API Routing**: Route requests đến các microservices (authentication, user, media)
- **Authentication Filter**: Xác thực JWT token cho các endpoint không public
- **CORS Support**: Hỗ trợ Cross-Origin Resource Sharing
- **Request Proxying**: Proxy requests đến các backend services

## Cấu trúc

```
api-gateway/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Cài đặt

1. Tạo virtual environment:
```bash
python -m venv venv
```

2. Kích hoạt virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Cấu hình

Chỉnh sửa file `config.py` để thay đổi:
- Port (mặc định: 8888)
- Service URLs
- Public endpoints
- CORS settings

## Chạy ứng dụng

```bash
python app.py
```

Server sẽ chạy tại: `http://localhost:8888`

## API Routes

### Authentication Service
- Base URL: `http://localhost:8888/api/v1/auth/*`
- Proxy to: `http://localhost:8080`
- Public endpoints: Tất cả endpoints `/auth/*` là public

### User Service
- Base URL: `http://localhost:8888/api/v1/users/*`
- Proxy to: `http://localhost:8081`
- Requires authentication

### Media Service
- Base URL: `http://localhost:8888/api/v1/media/*`
- Proxy to: `http://localhost:8090`
- Requires authentication

## Authentication

Các endpoint không public yêu cầu JWT token trong header:

```
Authorization: Bearer <your-token>
```

Token được xác thực thông qua authentication service endpoint `/auth/introspect`.

## Sự khác biệt so với Java version

### Giữ nguyên:
- Logic routing và authentication
- API prefix và endpoints
- Service URLs và ports
- Public endpoints patterns
- Response format (ApiResponse)

### Thay đổi kỹ thuật:
- Reactive programming (Mono/Flux) → Synchronous requests
- Spring Cloud Gateway filters → Flask decorators
- WebClient → Python requests library
- YAML configuration → Python config class

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: CORS support
- **requests**: HTTP client for proxying requests

## Health Check

```
GET /health
```

Returns: `{"code": 0, "message": "API Gateway is running"}`
