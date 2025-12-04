# HƯỚNG DẪN CHẠY MEDIA SERVICE

## Bước 1: Chuẩn bị môi trường

### Cài đặt Python
Đảm bảo đã cài Python 3.8 trở lên:
```bash
python --version
```

### Cài đặt MongoDB
Service cần MongoDB để lưu metadata của file. Có thể dùng Docker:
```bash
docker run -d -p 27017:27017 --name mongodb-media \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=root \
  mongo:latest
```

Hoặc cài đặt MongoDB local theo hướng dẫn tại: https://www.mongodb.com/try/download/community

## Bước 2: Cài đặt dependencies

### Tạo virtual environment (khuyến nghị)
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

## Bước 3: Cấu hình

Kiểm tra file `application.yaml` và điều chỉnh nếu cần:

```yaml
server:
  port: 8090                    # Port service sẽ chạy
  servlet:
    context-path: /media

spring:
  application:
    name: media-service
  data:
    mongodb:
      # Thay đổi connection string nếu MongoDB của bạn khác
      uri: mongodb://root:root@localhost:27017/file-service?authSource=admin

app:
  file:
    # Thư mục lưu file - sẽ tự tạo nếu chưa có
    storage-dir: "media-service/file-storage"
    # URL prefix cho download - thay đổi theo domain của bạn
    download-prefix: http://localhost:8888/api/v1/media/download/
```

## Bước 4: Chạy service

```bash
python app.py
```

Service sẽ khởi động tại: **http://localhost:8090**

Bạn sẽ thấy log:
```
Starting media-service on port 8090
Context path: /media
 * Running on http://0.0.0.0:8090
```

## Bước 5: Test API

### Lấy JWT Token
Trước tiên, bạn cần có JWT token từ authentication service. Giả sử token là:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Test Upload File

**Sử dụng curl:**
```bash
curl -X POST http://localhost:8090/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/your/file.jpg"
```

**Sử dụng Postman:**
1. Method: POST
2. URL: http://localhost:8090/upload
3. Headers:
   - Authorization: Bearer YOUR_JWT_TOKEN
4. Body:
   - Chọn form-data
   - Key: file (chọn type là File)
   - Value: Chọn file từ máy

**Response:**
```json
{
  "originalFileName": "file.jpg",
  "url": "http://localhost:8888/api/v1/media/download/uuid-generated-name.jpg"
}
```

### Test Batch Upload

**Sử dụng curl:**
```bash
curl -X POST http://localhost:8090/batch-upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "files=@/path/to/file1.jpg" \
  -F "files=@/path/to/file2.jpg"
```

**Sử dụng Postman:**
1. Method: POST
2. URL: http://localhost:8090/batch-upload
3. Headers:
   - Authorization: Bearer YOUR_JWT_TOKEN
4. Body:
   - Chọn form-data
   - Key: files (chọn type là File, và cho phép multiple files)
   - Value: Chọn nhiều files

### Test Download File

```bash
curl -X GET http://localhost:8090/download/uuid-generated-name.jpg \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  --output downloaded-file.jpg
```

## Các vấn đề thường gặp

### 1. Lỗi "ModuleNotFoundError"
```
Nguyên nhân: Chưa cài đặt dependencies
Giải pháp: pip install -r requirements.txt
```

### 2. Lỗi kết nối MongoDB
```
Nguyên nhân: MongoDB chưa chạy hoặc connection string sai
Giải pháp: 
- Kiểm tra MongoDB đang chạy: docker ps hoặc service mongodb status
- Kiểm tra connection string trong application.yaml
```

### 3. Lỗi "Permission denied" khi lưu file
```
Nguyên nhân: Không có quyền ghi vào thư mục storage
Giải pháp: 
- Windows: Chạy terminal as Administrator
- Linux/Mac: chmod 777 media-service/file-storage
```

### 4. Lỗi JWT "unauthenticated"
```
Nguyên nhân: Token không hợp lệ hoặc thiếu
Giải pháp:
- Kiểm tra format header: "Authorization: Bearer <token>"
- Đảm bảo token chưa hết hạn
- Token phải có claim 'sub' chứa user_id
```

### 5. Port 8090 đã được sử dụng
```
Nguyên nhân: Có service khác đang chạy trên port 8090
Giải pháp: Thay đổi port trong application.yaml
```

## Kiểm tra service đang chạy

### Kiểm tra process
```bash
# Windows
netstat -ano | findstr :8090

# Linux/Mac
lsof -i :8090
```

### Kiểm tra MongoDB
```bash
# Kết nối MongoDB
mongo mongodb://root:root@localhost:27017/admin

# Kiểm tra database
use file-service
db.getCollectionNames()
```

## Tắt service

- Nhấn `Ctrl + C` trong terminal đang chạy service
- Hoặc kill process theo PID

## Môi trường Production

Khi deploy lên production, nên:

1. **Sử dụng WSGI server** thay vì Flask development server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8090 app:app
```

2. **Set environment variables:**
```bash
export FLASK_DEBUG=false
export SECRET_KEY=your-production-secret-key
```

3. **Sử dụng reverse proxy** như Nginx

4. **Cấu hình MongoDB authentication** đúng cách

5. **Backup định kỳ** thư mục file-storage và MongoDB

## Liên hệ

Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ team dev.
