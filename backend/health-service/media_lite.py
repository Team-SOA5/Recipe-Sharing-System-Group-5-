import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# CẤU HÌNH
PORT = 8090
STORAGE_FOLDER = 'media-storage'
BASE_URL = "http://localhost:8090/media"

app = Flask(__name__)
CORS(app)

# Tạo thư mục lưu file nếu chưa có
if not os.path.exists(STORAGE_FOLDER):
    os.makedirs(STORAGE_FOLDER)

# 1. API Upload (Mô phỏng y hệt Media Service xịn)
@app.route('/media/upload', methods=['POST'])
def upload_file():
    print(f"📥 Receiving upload request...")
    
    # Check file
    if 'file' not in request.files:
        return jsonify({"code": 400, "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"code": 400, "message": "No selected file"}), 400

    try:
        # Lưu file vật lý
        ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(STORAGE_FOLDER, unique_name)
        
        file.save(save_path)
        
        # Tạo URL để trả về
        file_url = f"{BASE_URL}/download/{unique_name}"
        
        print(f"✅ Saved: {unique_name}")
        
        # Trả về JSON đúng cấu trúc Health Service cần
        # Health Service chỉ cần lấy key 'url' là đủ
        return jsonify({
            "originalFileName": file.filename,
            "url": file_url,
            "fileName": unique_name
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"code": 500, "message": str(e)}), 500

# 2. API Download (Để AI Service tải về được)
@app.route('/media/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(STORAGE_FOLDER, filename)

if __name__ == '__main__':
    print(f"🚀 Media Service (LITE VERSION) running on port {PORT}")
    print(f"📂 Storage: {os.path.abspath(STORAGE_FOLDER)}")
    app.run(host='0.0.0.0', port=PORT, debug=True)