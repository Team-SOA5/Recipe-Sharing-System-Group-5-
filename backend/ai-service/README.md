# 🧠 AI Recommendation Service

Microservice "Bộ não" của hệ thống. Sử dụng **LlamaParse** để đọc tài liệu phức tạp và **Google Gemini 1.5 Flash** để trích xuất dữ liệu y tế và đưa ra gợi ý món ăn thông minh.

## 🚀 Tính năng chính
- **OCR thông minh:** Đọc tốt cả PDF bảng biểu (xét nghiệm máu) và Ảnh chụp (nhờ Groq Vision).
- **Trích xuất dữ liệu:** Chuyển đổi văn bản y tế lộn xộn thành JSON có cấu trúc.
- **Tư vấn dinh dưỡng:** Kết hợp dữ liệu sức khỏe + Dữ liệu món ăn (từ Recipe Service) để gợi ý thực đơn cá nhân hóa.
- **Chatbot:** Trả lời câu hỏi dinh dưỡng theo ngữ cảnh.

## 🛠️ Yêu cầu hệ thống
- **Python:** 3.10 hoặc 3.11 (⚠️ Không dùng 3.14)
- **MongoDB:** Running at `localhost:27017`
- **API Keys (Bắt buộc):**
  - [Groq API Key](https://aistudio.google.com/)
  - [LlamaCloud API Key](https://cloud.llamaindex.ai/)

## ⚙️ Cài đặt & Chạy

### 1. Thiết lập môi trường
```bash
# Tại thư mục ai-service
python -m venv venv
# Windows:
.\venv\Scripts\activate

# Cài đặt thư viện (Lưu ý: Không cài llama-parse SDK để tránh lỗi xung đột)
pip install -r requirements.txt