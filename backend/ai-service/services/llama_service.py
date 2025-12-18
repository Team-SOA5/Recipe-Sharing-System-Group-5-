import requests
import os
import time
import json
from exceptions.exceptions import AppError, ErrorCode

class LlamaService:
    def __init__(self):
        self.api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not self.api_key:
            raise AppError(ErrorCode.CONFIG_ERROR, "Missing LLAMA_CLOUD_API_KEY")
        
        # Cập nhật Base URL theo tài liệu mới nhất (v1)
        self.base_url = "https://api.cloud.llamaindex.ai/api/v1/parsing"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    def parse_pdf_to_markdown(self, file_path):
        """
        Quy trình chuẩn 3 bước theo API docs:
        1. Upload File -> lấy Job ID
        2. Check Job Status -> đợi SUCCESS
        3. Get Result -> lấy Markdown
        """
        
        # 0. Validate file
        if not os.path.exists(file_path):
            raise AppError(ErrorCode.FILE_NOT_FOUND, f"File not found: {file_path}")
        if not file_path.lower().endswith('.pdf'):
            raise AppError(ErrorCode.INVALID_FILE_TYPE, "Only .pdf files are supported")

        try:
            # --- BƯỚC 1: UPLOAD FILE ---
            upload_url = f"{self.base_url}/upload"
            file_name = os.path.basename(file_path)
            
            with open(file_path, "rb") as f:
                # Requests tự động xử lý boundary cho multipart/form-data
                files = {"file": (file_name, f, "application/pdf")}
                # Có thể thêm options nếu cần: data={"language": "vi"}
                response = requests.post(upload_url, headers=self.headers, files=files)

            if response.status_code != 200:
                raise Exception(f"Upload failed ({response.status_code}): {response.text}")
            
            job_id = response.json().get("id")
            print(f"-> Job started with ID: {job_id}")

            # --- BƯỚC 2: CHECK STATUS (POLLING) ---
            job_url = f"{self.base_url}/job/{job_id}"
            
            max_retries = 60  # Tối đa 2 phút (60 * 2s)
            is_success = False

            for _ in range(max_retries):
                time.sleep(2) # Đợi 2s mỗi lần check
                
                status_res = requests.get(job_url, headers=self.headers)
                
                if status_res.status_code != 200:
                    continue # Nếu lỗi mạng tạm thời thì thử lại
                
                status_data = status_res.json()
                status = status_data.get("status")

                if status == "SUCCESS":
                    is_success = True
                    break
                elif status == "FAILED":
                    err_msg = status_data.get("error_message", "Unknown error")
                    raise Exception(f"Parsing Job Failed: {err_msg}")
                # Nếu PENDING hoặc STARTED thì vòng lặp tiếp tục
            
            if not is_success:
                raise Exception("Job timed out after 2 minutes")

            # --- BƯỚC 3: RETRIEVE RESULT (Markdown) ---
            # Đây là bước quan trọng mà tài liệu nhấn mạnh
            result_url = f"{self.base_url}/job/{job_id}/result/markdown"
            result_res = requests.get(result_url, headers=self.headers)

            if result_res.status_code != 200:
                raise Exception(f"Failed to retrieve markdown ({result_res.status_code})")

            # Result trả về thường là JSON có key 'markdown'
            result_json = result_res.json()
            return result_json.get("markdown", "")

        except requests.exceptions.RequestException as req_err:
            # Lỗi liên quan đến mạng/kết nối
            raise AppError(ErrorCode.NETWORK_ERROR, f"Network error: {str(req_err)}")
        except Exception as e:
            # Các lỗi logic khác
            print(f"Llama Service Error: {e}")
            raise AppError(ErrorCode.UNKNOWN_ERROR, f"PDF Parsing Error: {str(e)}")