import requests
import os
import time
from exceptions.exceptions import AppError, ErrorCode

class LlamaService:
    def __init__(self):
        self.api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        self.base_url = "https://api.cloud.llamaindex.ai/api/parsing"

    def parse_pdf_to_markdown(self, file_path):
        """Upload PDF lên LlamaCloud và nhận về Markdown"""
        try:
            # 1. Upload
            upload_url = f"{self.base_url}/upload"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            file_name = os.path.basename(file_path)
            
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f, "application/pdf")}
                data = {"language": "vi", "parsing_instruction": "Extract tables and text"}
                resp = requests.post(upload_url, headers=headers, files=files, data=data)
            
            if resp.status_code != 200: raise Exception(f"Upload failed: {resp.text}")
            job_id = resp.json().get("id")

            # 2. Polling
            job_url = f"{self.base_url}/job/{job_id}"
            for _ in range(30): # Chờ tối đa 60s
                time.sleep(2)
                job_res = requests.get(job_url, headers=headers)
                if job_res.status_code == 200:
                    status = job_res.json().get("status")
                    if status == "SUCCESS":
                        return job_res.json().get("markdown", "")
                    elif status == "FAILED":
                        raise Exception("LlamaParse Job Failed")
            
            raise Exception("LlamaParse Timeout")
        except Exception as e:
            print(f"Llama Service Error: {e}")
            raise AppError(ErrorCode.UNKNOWN_ERROR, f"PDF Parsing Error: {str(e)}")