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

GET
/recipes
Lấy danh sách (hỗ trợ search, filter)


POST
/recipes


GET
/recipes/{id}

PUT
/recipes/{id}
Cập nhật công thức (Chỉ tác giả)

DELETE
/recipes/{id}

Xóa công thức (Chỉ tác giả)


GET

/recipes/user/{userId}

Xem công thức của user



POST

/recipes/{id}/view

Tăng lượt xem



GET

/recipes/feed

Xem feed (các bài mới)



GET

/recipes/trending/recipes

Xem công thức xu hướng
