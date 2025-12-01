# Backend Informations

##  1. Các prefix path cho từng service

- API Gateway: `http://localhost:8888/api/v1/...`
- Authentication Service: `http://localhost:8080/auth`
- User Service: `http://localhost:8081/users`
- Recipe Service: `http://localhost:8082/recipes`
- Category Service: `http://localhost:8083/categories`
- Tag Service: `http://localhost:8084/tags`
- Comment Service: `http://localhost:8085/comments`
- Rating Service: `http://localhost:8086/ratings`
- Favorite Service: `http://localhost:8087/favorites`
- Follow Service: `http://localhost:8088/follows`
- Search Service: `http://localhost:8089/search`
- Media Service: `http://localhost:8090/media`
- Health Service: `http://localhost:8091/health`
- AI Recommendation Service: `http://localhost:8092/ai`
- Notification Service: `http://localhost:8093/notifications`

## 2. Decode token cho các service:
- Verify token chỉ thực hiện ở api-gateway, các service chỉ thực hiện decode token để lấy user_id
- Mỗi service phải tạo 1 folder mới có tên là `utils` đặt bên trong folder service đó, và lấy file `jwt_service` của folder `utils` trong user-service 
- Khi 1 service muốn lấy `user_id` hiện tại đang đăng nhập, chỉ cần import: `from flask import g` và khai báo `user_id = g.get('user_id')`, user_id chính là id của người dùng hiện tại đang đăng nhập

## 3. Yêu cầu chung với mỗi service:
- Đường dẫn của service được quy ước như phần 1
- Phải có folder `utils` chứa `jwt_service` như hướng dẫn trên
- Phải có file requirements.txt
- Phải có Hướng dẫn chạy viết trong readme (bao gồm thông tin database)
- Khi test chỉ cần gọi đến port của service đó, không cần thông qua api-gateway, tôi sẽ tự cấu hình cái đó
- Do cài đặt database của mỗi người khác nhau, nên hãy chú ý tới cấu hình database trước khi chạy test 1 service nào đó
