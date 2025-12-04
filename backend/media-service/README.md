# Media Service - Python Flask


## Mô tả

Media Service cung cấp các API để:
- Upload file đơn lẻ
- Upload nhiều file cùng lúc (batch upload)
- Download file
- Quản lý metadata của file trong MongoDB


## Cấu trúc thư mục

```
media-service/
├── app.py                      # Entry point của application
├── config.py                   # Configuration class
├── extensions.py               # Flask extensions (MongoDB)
├── application.yaml            # YAML configuration file
├── requirements.txt            # Python dependencies
├── models/
│   └── models.py              # FileManagement entity
├── dto/
│   ├── requests.py            # Request DTOs (FileInfo)
│   └── responses.py           # Response DTOs (FileResponse, BatchUploadResponse, etc.)
├── repositories/
│   ├── file_management_repository.py  # MongoDB repository
│   └── file_repository.py             # File storage repository
├── services/
│   └── file_service.py        # Business logic layer
├── routes/
│   └── file_routes.py         # REST API endpoints
├── exceptions/
│   ├── exceptions.py          # Custom exceptions và error codes
│   └── error_handler.py       # Global error handler
└── utils/
    └── jwt_service.py         # JWT authentication utility
```

## Yêu cầu hệ thống

- Python 3.8+
- MongoDB 4.0+
- pip

## Cài đặt

### 1. Tạo virtual environment (khuyến nghị)

```bash
python -m venv venv
```

Kích hoạt virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình

Chỉnh sửa file `application.yaml` theo môi trường của bạn:

```yaml
server:
  port: 8090                    # Port chạy service
  servlet:
    context-path: /media        # Context path (base path cho API)

spring:
  application:
    name: media-service
  data:
    mongodb:
      uri: mongodb://root:root@localhost:27017/file-service?authSource=admin

app:
  file:
    storage-dir: "media-service/file-storage"  # Thư mục lưu file
    download-prefix: http://localhost:8888/api/v1/media/download/
```

### 4. Khởi động MongoDB

Đảm bảo MongoDB đang chạy trên `localhost:27017` với credentials trong config.

```bash
# Ví dụ với Docker
docker run -d -p 27017:27017 --name mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=root \
  mongo:latest
```

## Chạy ứng dụng

```bash
python app.py
```

Service sẽ chạy tại: `http://localhost:8090/media`

## API Endpoints

### 1. Upload single file

**Endpoint:** `POST /upload`

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`

**Body:** Form-data
- `file`: File cần upload

**Response:**
```json
{
  "originalFileName": "example.jpg",
  "url": "http://localhost:8888/api/v1/media/download/uuid-filename.jpg"
}
```

### 2. Batch upload files

**Endpoint:** `POST /batch-upload`

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`

**Body:** Form-data
- `files`: Multiple files

**Response:**
```json
{
  "uploads": [
    {
      "url": "http://localhost:8888/api/v1/media/download/uuid-file1.jpg"
    },
    {
      "url": "http://localhost:8888/api/v1/media/download/uuid-file2.jpg"
    }
  ]
}
```

### 3. Download file

**Endpoint:** `GET /download/{fileName}`

**Headers:**
- `Authorization: Bearer <JWT_TOKEN>`

**Response:** File binary với appropriate content-type

## Xác thực (Authentication)

Service sử dụng JWT token để xác thực. Token phải được gửi trong header:

```
Authorization: Bearer <YOUR_JWT_TOKEN>
```

JWT token được decode để lấy `user_id` (từ claim `sub`) và lưu cùng metadata file.



## Lưu ý

1. **JWT Signature:**  service này không verify JWT signature, chỉ decode token. Điều này phù hợp khi service nằm sau API Gateway đã verify token.

2. **File Storage:** Files được lưu trong filesystem tại thư mục được config trong `FILE_STORAGE_DIR`. Đảm bảo thư mục này có quyền ghi.

3. **MongoDB Collection:** Service sử dụng collection `file-management` để lưu metadata.

4. **Error Handling:** Tất cả lỗi được xử lý tập trung và trả về format chuẩn:
```json
{
  "code": 1009,
  "message": "file not existed"
}
```

## Development

Để chạy ở chế độ debug:

```bash
export FLASK_DEBUG=true  # Linux/Mac
set FLASK_DEBUG=true     # Windows
python app.py
```

## Troubleshooting

### Lỗi kết nối MongoDB
- Kiểm tra MongoDB đang chạy
- Kiểm tra credentials trong `application.yaml`
- Kiểm tra connection string

### Lỗi upload file
- Kiểm tra quyền ghi của thư mục `FILE_STORAGE_DIR`
- Kiểm tra dung lượng file (max 16MB)

### Lỗi JWT token
- Kiểm tra format của token trong Authorization header
- Đảm bảo token có claim `sub` chứa user_id
- Kiểm tra token chưa hết hạn

