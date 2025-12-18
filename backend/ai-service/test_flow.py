import requests
import time
import json
import os
import sys

# --- CẤU HÌNH ---
# Đảm bảo các port khớp với 3 service bạn đang chạy
HEALTH_URL = "http://localhost:8091/health"
AI_URL = "http://localhost:8092/ai"
HEADERS = {"Authorization": "Bearer dev_token_123"}

# File PDF test (Đảm bảo file này nằm cùng thư mục với script)
PDF_FILE_PATH = "test_llama_input.pdf"

def print_header(msg):
    print(f"\n{'='*60}")
    print(f"🚀 {msg}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def run_test():
    # 0. CHECK FILE
    if not os.path.exists(PDF_FILE_PATH):
        print_error(f"Không tìm thấy file: {PDF_FILE_PATH}")
        return

    try:
        # ==========================================
        # BƯỚC 1: UPLOAD (Health Service sẽ tự gọi AI sau khi lưu xong)
        # ==========================================
        print_header(f"BƯỚC 1: Upload hồ sơ & Tự động kích hoạt AI")
        upload_url = f"{HEALTH_URL}/medical-records"
        file_name = os.path.basename(PDF_FILE_PATH)

        with open(PDF_FILE_PATH, "rb") as f:
            files = {"file": (file_name, f, "application/pdf")}
            data = {
                "title": f"Test Auto-Trigger {int(time.time())}", 
                "notes": "Kiểm tra tính năng tự động phân tích"
            }
            
            print(f"ℹ️  Đang upload file '{file_name}' lên Health Service...")
            resp = requests.post(upload_url, headers=HEADERS, files=files, data=data)

        if resp.status_code != 201:
            print_error(f"Upload thất bại: {resp.text}")
            return
            
        result = resp.json()
        # Lấy ID từ response (Cấu trúc linh hoạt)
        record = result.get('medicalRecord') or result.get('data') or {}
        record_id = record.get('id')
        
        print_success(f"Upload thành công! Record ID: {record_id}")
        print(f"ℹ️  Trạng thái ban đầu: {record.get('status')} (Hy vọng là 'pending')")

        # BƯỚC 2: POLLING (Chờ AI callback về Health Service)
        # ==========================================
        print_header("BƯỚC 2: Theo dõi trạng thái (Polling)")
        print("⏳ Đang chờ AI Service tải file, phân tích và cập nhật lại DB...")
        
        status = "pending"
        max_retries = 40 
        
        for i in range(max_retries):
            time.sleep(3) 
            
            try:
                # Gọi API lấy chi tiết
                resp = requests.get(f"{HEALTH_URL}/medical-records/{record_id}", headers=HEADERS)
                
                # [DEBUG] In ra status code nếu lỗi
                if resp.status_code != 200:
                    print(f"⚠️ API trả về lỗi {resp.status_code}: {resp.text}")
                    continue

                data = resp.json()
                
                # [FIX LỖI] Logic lấy data linh hoạt hơn + Debug
                # Thử tìm trong medicalRecord, nếu không có tìm trong data, nếu không có thì lấy chính nó
                rec_data = data.get("medicalRecord") or data.get("data") or data
                
                if not rec_data:
                    print(f"\n❌ [DEBUG] JSON trả về không có dữ liệu mong đợi: {data}")
                    continue

                # Lấy status an toàn hơn
                status = rec_data.get("status")
                
                # Hiển thị log
                sys.stdout.write(f"\r   ⏱️  Giây thứ {i*3}: Status = {status}   ")
                sys.stdout.flush()
                
                if status == "processed":
                    print("\n")
                    print_success("🎉 HOÀN TẤT! AI đã xử lý xong.")
                    
                    print("\n📦 DỮ LIỆU TRÍCH XUẤT (EXTRACTED DATA):")
                    extracted = rec_data.get("extractedData")
                    print(json.dumps(extracted, indent=2, ensure_ascii=False))
                    break
                
                if status == "failed":
                    print("\n")
                    print_error("💀 AI Xử lý thất bại!")
                    print(f"Lý do: {rec_data.get('errorMessage')}")
                    return

            except Exception as e:
                print(f"\n❌ Lỗi khi polling: {e}")
                # In chi tiết lỗi để debug
                import traceback
                traceback.print_exc()

        if status != "processed":
            print_error("\nTimeout! Quá thời gian chờ mà chưa thấy xong.")
            return

        # ==========================================
        # BƯỚC 3: KIỂM TRA GỢI Ý (RECOMMENDATION)
        # ==========================================
        print_header("BƯỚC 3: Kiểm tra API Gợi ý món ăn")
        rec_url = f"{AI_URL}/recommendations"
        print(f"ℹ️  Gọi GET {rec_url}?medicalRecordId={record_id}")
        
        resp = requests.get(rec_url, headers=HEADERS, params={"medicalRecordId": record_id})
        
        if resp.status_code == 200:
            recs = resp.json().get("data", [])
            print_success(f"AI đã gợi ý {len(recs)} món ăn dựa trên hồ sơ này.")
            if len(recs) > 0:
                print(f"   Món đầu tiên: {recs[0].get('recipeName', 'Unknown')} - Lý do: {recs[0].get('reason')}")
        else:
            print_error(f"Lỗi lấy gợi ý: {resp.text}")

    except Exception as e:
        print_error(f"Lỗi script: {e}")

if __name__ == "__main__":
    run_test()