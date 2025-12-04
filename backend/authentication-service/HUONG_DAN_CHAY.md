# 🚀 HƯỚNG DẪN CHẠY AUTHENTICATION-SERVICE (Python Flask)

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- MySQL Server 5.7 trở lên
- pip (Python package manager)

## 🔧 Các bước cài đặt và chạy

### Bước 1: Chuẩn bị Database

Mở MySQL và tạo database:

```sql
CREATE DATABASE `cookpad-identity` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Bước 2: Di chuyển vào thư mục dự án

```powershell
cd d:\KTHDV\demo_project\Flask_project\authentication-service
```

### Bước 3: Tạo Python Virtual Environment

```powershell
python -m venv venv
```

### Bước 4: Kích hoạt Virtual Environment

**Trên Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

Nếu gặp lỗi về Execution Policy, chạy lệnh này trước:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Trên Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

### Bước 5: Cài đặt các thư viện cần thiết

```powershell
pip install -r requirements.txt
```

### Bước 6: Cấu hình biến môi trường

Tạo file `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Sau đó mở file `.env` và chỉnh sửa thông tin kết nối database (nếu cần):

```env
DATABASE_URL=mysql+pymysql://root:12345678@localhost:3306/cookpad-identity
JWT_SIGNER_KEY=4vCM6CA5NXhXhG+LjHY+PfQRZYGjm13cHoNxVPuDyEYz2XB5SO/8Ko2vCxBkqHeT
JWT_ACCESS_TOKEN_DURATION=1000
JWT_REFRESH_TOKEN_DURATION=30000
PROFILE_SERVICE_URL=http://localhost:8081/users
SECRET_KEY=dev-secret-key-change-in-production
```



### Bước 7: Chạy ứng dụng

```powershell
python app.py
```

Ứng dụng sẽ khởi động tại: **http://localhost:8080**

Khi khởi động lần đầu, hệ thống sẽ tự động:
- Tạo các bảng trong database
- Tạo 2 roles: USER và ADMIN
- Tạo tài khoản admin mặc định:
  - Email: `admin@gmail.com`
  - Password: `admin12345`

## 📝 Test API bằng cURL hoặc Postman

### 1. Test Đăng ký (Register)

```powershell
curl -X POST http://localhost:8080/auth/register `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"password\":\"test12345\",\"username\":\"testuser\",\"fullName\":\"Test User\"}'
```

**Lưu ý:** Endpoint này cần user-service đang chạy tại `http://localhost:8081`

### 2. Test Đăng nhập (Login)

```powershell
curl -X POST http://localhost:8080/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"admin@gmail.com\",\"password\":\"admin12345\"}'
```

Kết quả sẽ trả về:
```json
{
  "message": "Thành công",
  "accessToken": "eyJhbGc...",
  "refreshToken": "eyJhbGc..."
}
```

### 3. Test Introspect Token

```powershell
curl -X POST http://localhost:8080/auth/introspect `
  -H "Content-Type: application/json" `
  -d '{\"accessToken\":\"YOUR_ACCESS_TOKEN_HERE\"}'
```

### 4. Test Logout

```powershell
curl -X POST http://localhost:8080/auth/logout `
  -H "Content-Type: application/json" `
  -d '{\"accessToken\":\"YOUR_ACCESS_TOKEN\",\"refreshToken\":\"YOUR_REFRESH_TOKEN\"}'
```

### 5. Test Refresh Token

```powershell
curl -X POST http://localhost:8080/auth/refresh-token `
  -H "Content-Type: application/json" `
  -d '{\"accessToken\":\"YOUR_ACCESS_TOKEN\",\"refreshToken\":\"YOUR_REFRESH_TOKEN\"}'
```

## 🐛 Xử lý lỗi thường gặp

### Lỗi kết nối MySQL

```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server...")
```

**Giải pháp:**
- Kiểm tra MySQL đã chạy chưa
- Kiểm tra username/password trong file `.env`
- Kiểm tra database `cookpad-identity` đã được tạo chưa

### Lỗi import module

```
ModuleNotFoundError: No module named 'flask'
```

**Giải pháp:**
- Đảm bảo đã kích hoạt virtual environment
- Chạy lại `pip install -r requirements.txt`

### Lỗi port đã được sử dụng

```
OSError: [WinError 10048] Only one usage of each socket address...
```

**Giải pháp:**
- Tắt ứng dụng đang chạy ở port 8080
- Hoặc thay đổi port trong file `app.py`:
  ```python
  app.run(host='0.0.0.0', port=8081, debug=True)
  ```

## 🔍 Kiểm tra Database

Sau khi chạy ứng dụng, kiểm tra các bảng đã được tạo:

```sql
USE `cookpad-identity`;
SHOW TABLES;

-- Xem roles đã được tạo
SELECT * FROM role;

-- Xem admin user
SELECT * FROM user_entity;

-- Xem quan hệ user-role
SELECT * FROM user_entity_role;
```

## 🛠️ Development Mode

Để chạy ở chế độ development với auto-reload:

File `app.py` đã được cấu hình sẵn:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

## 📊 Logs

Ứng dụng sẽ ghi log ra console. Quan sát logs để theo dõi:
- Kết nối database
- Khởi tạo roles và admin user
- Request/Response của API
- Lỗi nếu có

## 🔐 Lưu ý bảo mật

- **Đổi mật khẩu admin** sau khi khởi tạo lần đầu
- **Thay đổi JWT_SIGNER_KEY** trong production
- **Không commit file .env** vào git (đã có trong .gitignore)
- **Sử dụng HTTPS** trong production

## 🚦 Kiểm tra service đang chạy

```powershell
# Kiểm tra port 8080
netstat -ano | findstr :8080

# Hoặc dùng curl
curl http://localhost:8080/auth/login
```

## 📦 Dependencies chính

- **Flask 3.0.0**: Web framework
- **Flask-SQLAlchemy 3.1.1**: ORM
- **Flask-Bcrypt 1.0.1**: Password hashing
- **PyJWT 2.8.0**: JWT token
- **PyMySQL 1.1.0**: MySQL connector
- **requests 2.31.0**: HTTP client

---

**Chúc bạn chạy ứng dụng thành công! 🎉**
