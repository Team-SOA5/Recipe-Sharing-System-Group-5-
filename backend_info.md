# Backend Informations

##  1. Các prefix path cho từng service

- API Gateway: `http://localhost:8888`
- Authentication Service: `http://localhost:8080/api/v1/auth`
- User Service: `http://localhost:8081/api/v1/users`
- Recipe Service: `http://localhost:8082/api/v1/recipes`
- Category Service: `http://localhost:8083/api/v1/categories`
- Tag Service: `http://localhost:8084/api/v1/tags`
- Comment Service: `http://localhost:8085/api/v1/comments`
- Rating Service: `http://localhost:8086/api/v1/ratings`
- Favorite Service: `http://localhost:8087/api/v1/favorites`
- Follow Service: `http://localhost:8088/api/v1/follows`
- Search Service: `http://localhost:8089/api/v1/search`
- Media Service: `http://localhost:8090/api/v1/media`
- Health Service: `http://localhost:8091/api/v1/health`
- AI Recommendation Service: `http://localhost:8092/api/v1/ai`
- Notification Service: `http://localhost:8093/api/v1/notifications`

## Decode token cho các service:
- Verify token chỉ thực hiện ở api-gateway, các service chỉ thực hiện decode token để lấy user_id
- Mỗi service phải tạo 1 folder mới có tên là `utils` đặt bên trong folder service đó, và lấy file `jwt_service` trong user-service 
- Khi 1 service muốn lấy `user_id` hiện tại đang đăng nhập, chỉ cần import: `from flask import g` và khai báo `user_id = g.get('user_id')`, user_id chính là id của người dùng hiện tại đang đăng nhập

## Yêu cầu chung với mỗi service:
- Phải có folder `utils` chứa `jwt_service` như hướng dẫn trên
- Phải có file requirements.txt
- Phải có Hướng dẫn chạy viết trong readme (bao gồm thông tin database)