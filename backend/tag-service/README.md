# Tag Service (Python Flask)

Đây là service quản lý tag được viết lại từ Java Spring Boot sang Python Flask, giữ nguyên logic nghiệp vụ và luồng xử lý.

## Tính năng

- Tạo tag mới hoặc tăng số lượng công thức (recipes count) nếu tag đã tồn tại
- Tìm kiếm tag theo từ khóa
- Lấy danh sách tag phổ biến (theo số lượng công thức)
- JWT Authentication cho các endpoint yêu cầu xác thực
- MongoDB để lưu trữ dữ liệu

## Cấu trúc dự án

```
tag-service/
├── app.py                      # Entry point của ứng dụng
├── config.py                   # Cấu hình ứng dụng
├── extensions.py               # Flask extensions (PyMongo)
├── requirements.txt            # Dependencies
├── .env.example               # File mẫu biến môi trường
├── application.yaml           # Cấu hình (tương thích Java)
├── models/                    # Database models (Entity)
│   └── models.py             # Tag model
├── repositories/              # Data access layer
│   └── tag_repository.py     # TagRepository với MongoDB queries
├── services/                  # Business logic layer
│   └── tag_service.py        # TagService - business logic
├── routes/                    # Controllers/API endpoints
│   └── tag_routes.py         # Tag routes/endpoints
├── dto/                       # Data Transfer Objects
│   ├── requests.py           # TagRequest
│   └── responses.py          # TagResponse, TagList, ApiResponse
├── exceptions/                # Exception handling
│   ├── exceptions.py         # ErrorCode, AppException
│   └── error_handler.py      # Global error handler
├── utils/                     # Utilities
│   └── jwt_service.py        # JWT decode và validation
└── constants/                 # Constants
    └── constants.py          # PUBLIC_ENDPOINTS
```

## Cài đặt

### Yêu cầu

- Python 3.8 trở lên
- MongoDB 4.0 trở lên
- pip (Python package manager)

### Các bước cài đặt

1. Tạo virtual environment:

```bash
cd Flask_project/tag-service
python -m venv venv
```

2. Kích hoạt virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

3. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

4. Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

5. Cấu hình file `.env`:

```env
# Server Configuration
SERVER_PORT=8084

# Application
APPLICATION_NAME=tag-service

# MongoDB Configuration
MONGODB_URI=mongodb://root:root@localhost:27017/tag-service?authSource=admin
MONGODB_AUTO_INDEX_CREATION=true

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Environment
DEBUG=True
```

## Chạy ứng dụng

### Development mode

```bash
python app.py
```

Hoặc với Flask CLI:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port 8084
```

**Windows (PowerShell):**
```powershell
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
flask run --port 8084
```

### Production mode

```bash
export FLASK_ENV=production
python app.py
```

Ứng dụng sẽ chạy tại: `http://localhost:8084`

## API Endpoints

### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "UP",
  "service": "tag-service"
}
```

### 2. Tạo hoặc cập nhật tag

```http
POST /tags
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "name": "Vietnamese"
}
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "name": "Vietnamese",
  "createdAt": "2025-12-17T10:30:00Z",
  "recipesCount": 1
}
```

**Logic:**
- Nếu tag chưa tồn tại: tạo mới với `recipesCount = 1`
- Nếu tag đã tồn tại: tăng `recipesCount` lên 1

**Authentication:** Required (JWT Token)

### 3. Lấy danh sách tag phổ biến

```http
GET /tags/popular?limit=20
```

**Query Parameters:**
- `limit` (optional, default=20): Số lượng tag tối đa trả về

**Response:**
```json
{
  "tagResponseList": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Vietnamese",
      "createdAt": "2025-12-17T10:30:00Z",
      "recipesCount": 150
    },
    {
      "id": "507f1f77bcf86cd799439012",
      "name": "Italian",
      "createdAt": "2025-12-17T10:31:00Z",
      "recipesCount": 120
    }
  ]
}
```

**Sorting:** Sắp xếp theo `recipesCount` giảm dần

**Authentication:** Not required (Public endpoint)

### 4. Tìm kiếm tag theo từ khóa

```http
GET /tags?search=vietnam&limit=20
```

**Query Parameters:**
- `search` (required): Từ khóa tìm kiếm
- `limit` (optional, default=20): Số lượng tag tối đa trả về

**Response:**
```json
{
  "tagResponseList": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Vietnamese",
      "createdAt": "2025-12-17T10:30:00Z",
      "recipesCount": 150
    }
  ]
}
```

**Sorting:** Sắp xếp theo `createdAt` giảm dần

**Authentication:** Not required (Public endpoint)

## Database Schema

### Collection: `tag`

```javascript
{
  "_id": ObjectId,           // MongoDB ID
  "name": String,            // Tên tag (unique)
  "createdAt": ISODate,      // Thời gian tạo
  "recipesCount": Number     // Số lượng công thức sử dụng tag này
}
```

**Indexes:**
- `_id`: Primary key (auto-created)
- `name`: Recommended for faster lookup

## Authentication

Service sử dụng JWT (JSON Web Token) cho authentication:

- **Public endpoints:** `/tags`, `/tags/popular` (GET) - không cần token
- **Protected endpoints:** `/tags` (POST) - yêu cầu JWT token

### Cách sử dụng JWT Token

1. Lấy token từ authentication service
2. Thêm vào header của request:

```http
Authorization: Bearer <your_jwt_token>
```

### JWT Decoder

Service sử dụng custom JWT decoder (`utils/jwt_service.py`) để:
- Parse và validate JWT token
- Extract claims từ token
- Không verify signature (tương tự Java version)

## So sánh với Java Spring Boot

### Tương đồng

| Java Spring Boot | Python Flask | Mô tả |
|-----------------|--------------|-------|
| `@RestController` | `Blueprint` | Định nghĩa routes |
| `@Service` | Service class | Business logic |
| `@Repository` | Repository class | Data access |
| `@Entity` / `@Document` | Model class | Data model |
| `MongoRepository` | PyMongo collection | MongoDB operations |
| `@PostMapping` / `@GetMapping` | `@route(..., methods=[...])` | HTTP methods |
| `SecurityConfig` | `@require_auth` decorator | Authentication |
| `CustomJwtDecoder` | `decode_jwt()` | JWT decoding |
| `GlobalException` | Error handlers | Exception handling |

### Khác biệt

1. **Dependency Injection:**
   - Java: Spring's @Autowired
   - Python: Manual instantiation trong constructor

2. **Type System:**
   - Java: Strongly typed với compile-time checking
   - Python: Dynamic typing với optional type hints

3. **Data Mapping:**
   - Java: MapStruct tự động
   - Python: Manual mapping hoặc dataclasses

4. **Pagination:**
   - Java: Spring Data's Pageable
   - Python: Manual skip/limit trong MongoDB queries

## Lỗi thường gặp

### 1. MongoDB Connection Error

```
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [Errno 111] Connection refused
```

**Giải pháp:**
- Kiểm tra MongoDB đã chạy: `systemctl status mongod` (Linux) hoặc `net start MongoDB` (Windows)
- Kiểm tra connection string trong `.env`

### 2. Module Not Found

```
ModuleNotFoundError: No module named 'flask_pymongo'
```

**Giải pháp:**
- Cài đặt lại dependencies: `pip install -r requirements.txt`
- Đảm bảo virtual environment được kích hoạt

### 3. JWT Decode Error

```
AppException: UNAUTHENTICATED - you are not allowed!
```

**Giải pháp:**
- Kiểm tra JWT token có đúng format không
- Đảm bảo token chưa hết hạn
- Kiểm tra header: `Authorization: Bearer <token>`

## Testing

### Test với curl

**1. Health check:**
```bash
curl http://localhost:8084/health
```

**2. Lấy tag phổ biến:**
```bash
curl http://localhost:8084/tags/popular?limit=10
```

**3. Tìm kiếm tag:**
```bash
curl "http://localhost:8084/tags?search=vietnam&limit=5"
```

**4. Tạo tag (cần JWT token):**
```bash
curl -X POST http://localhost:8084/tags \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Vietnamese"}'
```

### Test với Postman

1. Import collection từ file hoặc tạo requests như trên
2. Thiết lập environment variables cho base URL và JWT token
3. Test các endpoints

## Deployment

### Docker

Tạo `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8084

CMD ["python", "app.py"]
```

Build và chạy:

```bash
docker build -t tag-service .
docker run -p 8084:8084 --env-file .env tag-service
```

### Production Considerations

1. **WSGI Server:** Sử dụng Gunicorn hoặc uWSGI thay vì Flask development server
2. **Environment Variables:** Không commit file `.env`, dùng secrets management
3. **Logging:** Cấu hình logging cho production
4. **MongoDB:** Sử dụng MongoDB Atlas hoặc replica set cho high availability
5. **Monitoring:** Thêm health checks và metrics

## Tác giả

Converted from Java Spring Boot to Python Flask - Tag Service

## License

MIT License
