Category Service 📂

Microservice quản lý danh mục món ăn (Port 8083).


Database: MongoDB (Database: cookpad_recipe_db)

Port: 8083

🛠️ Cài đặt & Chạy

1. Tạo môi trường ảo & Cài đặt thư viện

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt


2. Cấu hình Database

Đảm bảo MongoDB đang chạy tại localhost:27017 (hoặc cấu hình trong .env).

Tạo file .env từ file mẫu .env.example.
copy .env.example .env
3. Chạy Service

python app.py


Service sẽ chạy tại: http://localhost:8083

🔐 Cơ chế Authentication

Để test mà không cần token, set SKIP_AUTH=True trong file .env.
# Việc check role 'admin' nên được thực hiện thêm trong middleware hoặc controller nếu cần chặt chẽ hơn.

📡 API Endpoints

GET

/categories

Lấy tất cả danh mục
{
    "data": [
        {
            "createdAt": "2025-11-29T16:28:14.067000",
            "description": "Các món ăn thanh đạm, tốt cho sức khỏe",
            "icon": "https://example.com/icons/vegetarian.png",
            "id": "692b1f1e0c53424fd7206673",
            "name": "Món Chay",
            "recipesCount": 0
        }
    ]
}

POST

/categories

Tạo danh mục mới
{
    "createdAt": "2025-11-29T16:28:14.067729",
    "description": "Các món ăn thanh đạm, tốt cho sức khỏe",
    "icon": "https://example.com/icons/vegetarian.png",
    "id": "692b1f1e0c53424fd7206673",
    "name": "Món Chay",
    "recipesCount": 0
}

GET

/categories/{id}

Xem chi tiết danh mục
{
    "createdAt": "2025-11-29T16:28:14.067000",
    "description": "Các món ăn thanh đạm, tốt cho sức khỏe",
    "icon": "https://example.com/icons/vegetarian.png",
    "id": "692b1f1e0c53424fd7206673",
    "name": "Món Chay",
    "recipesCount": 0
}

PUT

/categories/{id}

Cập nhật danh mục
{
    "createdAt": "2025-11-29T16:28:14.067000",
    "description": "Cập nhật mô tả mới xịn hơn",
    "icon": "https://example.com/icons/vegetarian.png",
    "id": "692b1f1e0c53424fd7206673",
    "name": "Món Chay & Healthy",
    "recipesCount": 0
}

DELETE

/categories/{id}

Xóa danh mục
{
    "message": "Xóa thành công"
}