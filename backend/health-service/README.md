# 🏥 Health Service

Microservice quản lý hồ sơ bệnh án điện tử, đóng vai trò trung gian giữa người dùng, Media Service (lưu file) và AI Service (phân tích dữ liệu).

## 🚀 Tính năng chính
- Upload hồ sơ bệnh án (PDF/Ảnh) -> Tự động gửi sang Media Service.
- Quản lý trạng thái xử lý (Pending -> Processing -> Processed/Failed).
- Lưu trữ kết quả phân tích y tế (chỉ số xét nghiệm, bệnh lý...) từ AI.
- Trigger quá trình phân tích AI (gọi sang AI Service).
- Nhận Callback từ AI Service để cập nhật dữ liệu.

## 🛠️ Yêu cầu hệ thống
- **Python:** 3.10+
- **MongoDB:** Running at `localhost:27017`
- **Các Service phụ trợ:**
  - Media Service (Port 8090)
  - AI Service (Port 8092)

## ⚙️ Cài đặt & Chạy

### 1. Thiết lập môi trường
```bash
# Tại thư mục health-service
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt