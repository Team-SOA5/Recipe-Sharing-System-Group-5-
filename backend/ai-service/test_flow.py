import requests
import time
import json
import os
import sys

# --- CẤU HÌNH ---
HEALTH_URL = "http://localhost:8091/health"
AI_URL = "http://localhost:8092/ai"
HEADERS = {"Authorization": "Bearer dev_token_123"}

# [QUAN TRỌNG] Đặt tên file PDF bạn muốn test ở đây
# Hãy chắc chắn file này đang nằm cùng thư mục với script này
PDF_FILE_PATH = "test_llama_input.pdf" 

def print_header(msg):
    print(f"\n{'='*60}")
    print(f"🚀 {msg}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

# --- LUỒNG CHÍNH ---
def run_test():
    # 0. CHECK FILE TỒN TẠI
    if not os.path.exists(PDF_FILE_PATH):
        print_error(f"Không tìm thấy file: {PDF_FILE_PATH}")
        print_info("Vui lòng copy file PDF cần test vào cùng thư mục với script này.")
        return

    try:
        # 1. UPLOAD
        print_header(f"BƯỚC 1: Upload hồ sơ PDF ({PDF_FILE_PATH})")
        upload_url = f"{HEALTH_URL}/medical-records"
        
        file_name = os.path.basename(PDF_FILE_PATH)

        # [SỬA] Mở file binary (rb) và dùng content-type application/pdf
        with open(PDF_FILE_PATH, "rb") as f:
            files = {"file": (file_name, f, "application/pdf")}
            data = {
                "title": f"Hồ sơ Test PDF - {file_name}",
                "notes": "Test integration với LlamaParse"
            }
            
            print_info("Đang gửi request upload...")
            resp = requests.post(upload_url, headers=HEADERS, files=files, data=data)

        if resp.status_code != 201:
            print_error(f"Upload thất bại: {resp.text}")
            return
            
        result = resp.json()
        # Tùy vào cấu trúc response của Health Service
        record_id = result.get('medicalRecord', {}).get('id') or result.get('data', {}).get('id')
        print_success(f"Upload OK. ID: {record_id}")

        # 2. POLLING
        print_header("BƯỚC 2: Chờ AI xử lý (LlamaParse)")
        status = "pending"
        
        # [SỬA] Tăng thời gian chờ lên (60 lần * 3s = 3 phút)
        # Vì PDF parse qua LlamaCloud có thể mất 30s - 1p
        max_retries = 60
        
        for i in range(max_retries):
            time.sleep(3)
            
            try:
                resp = requests.get(f"{HEALTH_URL}/medical-records/{record_id}", headers=HEADERS)
                if resp.status_code != 200:
                    print(f"   Lỗi mạng/Server ({resp.status_code})... thử lại")
                    continue

                data = resp.json()
                status = data.get("status") # pending | processing | processed | failed
                print(f"   Wait {i*3}s... Status: {status}")
                
                if status == "processed":
                    print_success("AI Xử lý xong!")
                    print("\n📦 Dữ liệu trích xuất (Markdown/Json):")
                    # In thử một phần extractedData để kiểm tra
                    extracted = data.get("extractedData", "")
                    print(str(extracted)[:500] + "...\n(Đã cắt bớt)") 
                    break
                
                if status == "failed":
                    print_error(f"AI Failed: {data.get('errorMessage')}")
                    return
            except Exception as e:
                print(f"   Lỗi khi polling: {e}")

        if status != "processed":
            print_error("Timeout! AI xử lý quá lâu.")
            return

        # 3. RECOMMENDATIONS
        print_header("BƯỚC 3: Gợi ý món ăn (Dựa trên kết quả PDF)")
        resp = requests.get(f"{AI_URL}/recommendations", headers=HEADERS, params={"medicalRecordId": record_id})
        
        if resp.status_code == 200:
            recs = resp.json().get("data", [])
            print_success(f"Nhận được {len(recs)} gợi ý.")
            if recs:
                print_json(recs[0])
        else:
            print_error(f"Lỗi gợi ý: {resp.text}")

        # 4. CHAT
        print_header("BƯỚC 4: Chat với nội dung PDF")
        payload = {
            "message": "Dựa vào kết quả xét nghiệm vừa rồi, chỉ số nào của tôi đáng lo ngại nhất?",
            "context": {"medicalRecordId": record_id}
        }
        resp = requests.post(f"{AI_URL}/chat", headers=HEADERS, json=payload)
        
        if resp.status_code == 200:
            print(f"🤖 AI: {resp.json().get('message')}")
        else:
            print_error(f"Lỗi chat: {resp.text}")

    except Exception as e:
        print_error(f"Lỗi script: {e}")

if __name__ == "__main__":
    run_test()