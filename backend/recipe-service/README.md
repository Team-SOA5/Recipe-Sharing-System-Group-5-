Recipe Service 🍳

Microservice quản lý công thức nấu ăn, sử dụng MongoDB và Python Flask.

📋 Thông tin Service

URL: http://localhost:8082/recipes

Database: MongoDB (Database: cookpad_recipe_db)

Port: 8082

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


Service sẽ chạy tại: http://localhost:8082

🔐 Cơ chế Authentication

Để test mà không cần token, set SKIP_AUTH=True trong file .env.

📡 API Endpoints

Method

Endpoint

Mô tả


GET

/recipes

Lấy danh sách (hỗ trợ search, filter)
{
    "data": [],
    "pagination": {
        "limit": 10,
        "page": 1,
        "totalItems": 0
    }
}

POST

/recipes

Tạo công thức mới
Response
{
    "author_id": "dev_user_id_123",
    "average_rating": 0.0,
    "calories": 350.0,
    "category_id": "cat_001",
    "created_at": "2025-11-29T12:09:13.968935",
    "description": "Món canh chua đậm đà hương vị miền Tây.",
    "difficulty": "Medium",
    "id": "692ae269e7ae93a47e6869b0",
    "ingredients": [
        {
            "name": "Cá lóc",
            "quantity": "500g"
        },
        {
            "name": "Dọc mùng",
            "quantity": "2 cây"
        },
        {
            "name": "Cà chua",
            "quantity": "2 quả"
        }
    ],
    "serving": 4,
    "steps": [
        {
            "content": "Sơ chế cá lóc sạch sẽ.",
            "image": "https://example.com/step1.jpg",
            "order": 1
        },
        {
            "content": "Nấu nước dùng me chua.",
            "image": "https://example.com/step2.jpg",
            "order": 2
        }
    ],
    "tags": [
        "mon-canh",
        "mien-tay"
    ],
    "thumbnail": "https://example.com/images/canh-chua.jpg",
    "title": "Canh chua cá lóc",
    "total_time": 45,
    "updated_at": "2025-11-29T12:09:13.968943",
    "views": 0
}

GET
/recipes/{id}

Xem chi tiết
{
    "author_id": "dev_user_id_123",
    "average_rating": 0.0,
    "calories": 350.0,
    "category_id": "cat_001",
    "created_at": "2025-11-29T12:09:13.968000",
    "description": "Món canh chua đậm đà hương vị miền Tây.",
    "difficulty": "Medium",
    "id": "692ae269e7ae93a47e6869b0",
    "ingredients": [
        {
            "name": "Cá lóc",
            "quantity": "500g"
        },
        {
            "name": "Dọc mùng",
            "quantity": "2 cây"
        },
        {
            "name": "Cà chua",
            "quantity": "2 quả"
        }
    ],
    "serving": 4,
    "steps": [
        {
            "content": "Sơ chế cá lóc sạch sẽ.",
            "image": "https://example.com/step1.jpg",
            "order": 1
        },
        {
            "content": "Nấu nước dùng me chua.",
            "image": "https://example.com/step2.jpg",
            "order": 2
        }
    ],
    "tags": [
        "mon-canh",
        "mien-tay"
    ],
    "thumbnail": "https://example.com/images/canh-chua.jpg",
    "title": "Canh chua cá lóc",
    "total_time": 45,
    "updated_at": "2025-11-29T12:09:13.968000",
    "views": 0
}
PUT
/recipes/{id}

Cập nhật công thức (Chỉ tác giả)
{
    "author_id": "dev_user_id_123",
    "average_rating": 0.0,
    "calories": 350.0,
    "category_id": "cat_001",
    "created_at": "2025-11-29T12:09:13.968000",
    "description": "Món canh chua đậm đà hương vị miền Tây.",
    "difficulty": "Medium",
    "id": "692ae269e7ae93a47e6869b0",
    "ingredients": [
        {
            "name": "Cá lóc",
            "quantity": "500g"
        },
        {
            "name": "Dọc mùng",
            "quantity": "2 cây"
        },
        {
            "name": "Cà chua",
            "quantity": "2 quả"
        }
    ],
    "serving": 4,
    "steps": [
        {
            "content": "Sơ chế cá lóc sạch sẽ.",
            "image": "https://example.com/step1.jpg",
            "order": 1
        },
        {
            "content": "Nấu nước dùng me chua.",
            "image": "https://example.com/step2.jpg",
            "order": 2
        }
    ],
    "tags": [
        "mon-canh",
        "mien-tay"
    ],
    "thumbnail": "https://example.com/images/canh-chua.jpg",
    "title": "Canh chua cá lóc",
    "total_time": 45,
    "updated_at": "2025-11-29T12:09:13.968000",
    "views": 0
}

DELETE

/recipes/{id}

Xóa công thức (Chỉ tác giả)
{
    "message": "Deleted"
}


GET

/recipes/user/{userId}

Xem công thức của user
{
    "data": [
        {
            "author_id": "dev_user_id_123",
            "average_rating": 0.0,
            "created_at": "2025-11-29T12:09:13.968000",
            "difficulty": "Medium",
            "id": "692ae269e7ae93a47e6869b0",
            "thumbnail": "https://example.com/images/canh-chua.jpg",
            "title": "Canh chua cá lóc",
            "total_time": 45,
            "views": 0
        }
    ]
}

POST

/recipes/{id}/view

Tăng lượt xem
{
    "views": 2
}


GET

/recipes/feed

Xem feed (các bài mới)
{
    "data": [
        {
            "author_id": "dev_user_id_123",
            "average_rating": 0.0,
            "created_at": "2025-11-29T12:09:13.968000",
            "difficulty": "Medium",
            "id": "692ae269e7ae93a47e6869b0",
            "thumbnail": "https://example.com/images/canh-chua.jpg",
            "title": "Canh chua cá lóc",
            "total_time": 45,
            "views": 2
        }
    ],
    "pagination": {
        "limit": 10,
        "page": 1,
        "totalItems": 1,
        "totalPages": 1
    }
}


GET

/recipes/trending/recipes

Xem công thức xu hướng
{
    "data": [
        {
            "author_id": "dev_user_id_123",
            "average_rating": 0.0,
            "created_at": "2025-11-29T12:09:13.968000",
            "difficulty": "Medium",
            "id": "692ae269e7ae93a47e6869b0",
            "thumbnail": "https://example.com/images/canh-chua.jpg",
            "title": "Canh chua cá lóc",
            "total_time": 45,
            "views": 2
        }
    ]
}