import requests
import os
import tempfile

class IntegrationService:
    def __init__(self):
        # Lưu ý: Trong .env nên để http://127.0.0.1:8091 (không có dấu / ở cuối)
        self.health_url = os.getenv('HEALTH_SERVICE_URL', 'http://127.0.0.1:8091')
        self.media_url = os.getenv('MEDIA_SERVICE_URL', 'http://127.0.0.1:8888')
        self.recipe_url = os.getenv('RECIPE_SERVICE_URL', 'http://127.0.0.1:8080')

    def get_medical_record_meta(self, record_id, token):
        try:
            # --- SỬA LẠI ĐƯỜNG DẪN CHO KHỚP VỚI HEALTH SERVICE ---
            # Route bên Health: /health/medical-records/<id>
            url = f"{self.health_url}/health/medical-records/{record_id}"
            
            print(f"📥 [Integration] Fetching Meta: {url}") # Log để kiểm tra
            
            headers = {'Authorization': token}
            resp = requests.get(url, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"❌ Fetch Meta Failed: {resp.status_code} - {resp.text}")
                return None
        except Exception as e:
            print(f"❌ Get Meta Error: {e}")
            return None

    def download_file(self, file_url):
        try:
            print(f"📥 Raw file URL: {file_url}")

            # 1. Fix lỗi localhost trên Windows
            if 'localhost' in file_url:
                file_url = file_url.replace('localhost', '127.0.0.1')
            
            # 2. --- FIX LẠI LOGIC URL ---
            
            # Bước A: Đổi Port Gateway (8888) sang Port Service (8090)
            if ':8888' in file_url:
                print("⚠️ Detected wrong port 8888, switching to 8090...")
                file_url = file_url.replace(':8888', ':8090')
            
            # Bước B: Đổi Path Gateway sang Path Service (QUAN TRỌNG)
            # Cũ (Sai): replace(..., '/download/') -> Mất chữ media
            # Mới (Đúng): replace(..., '/media/download/')
            if '/api/v1/media/download/' in file_url:
                print("⚠️ Detected gateway path, switching to internal /media/download/...")
                file_url = file_url.replace('/api/v1/media/download/', '/media/download/')

            # Xử lý trường hợp URL tương đối
            if not file_url.startswith('http'):
                file_url = f"{self.media_url}/{file_url.lstrip('/')}"
            
            print(f"📥 Downloading from (REAL URL): {file_url}")
            
            # ... Các đoạn code download bên dưới giữ nguyên ...
            resp = requests.get(file_url, stream=True, timeout=15)
            
            if resp.status_code != 200:
                print(f"❌ Download failed code: {resp.status_code}")
                return None
            
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            for chunk in resp.iter_content(8192): 
                temp.write(chunk)
            temp.close()
            return temp.name
            
        except Exception as e:
            print(f"❌ Download Exception: {e}")
            return None

    def search_recipes(self, keywords=None):
        try:
            url = f"{self.recipe_url}/api/v1/recipes" if '/api/v1' not in self.recipe_url else f"{self.recipe_url}/recipes"
            params = {'limit': 5} # Lấy 5 món mẫu
            
            if keywords:
                params['q'] = keywords
                
            print(f"🍳 Calling Recipe Service: {url} | Keywords: {keywords}")
            resp = requests.get(url, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                recipes = data.get('data', [])
                
                simplified_recipes = []
                for r in recipes:
                    simplified_recipes.append({
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "ingredients": r.get("ingredients"),
                        "nutrition": r.get("nutrition", {})
                    })
                return simplified_recipes
            
            print(f"⚠️ Recipe Service returned {resp.status_code}")
            return []
            
        except Exception as e:
            print(f"⚠️ Error calling Recipe Service: {e}")
            return [] 

    def update_medical_record(self, record_id, token, update_data):
        """
        Gọi Health Service để cập nhật kết quả.
        Sử dụng Route riêng biệt: PATCH /medical-records/{id}/ai-callback
        """
        try:
            # --- SỬA LẠI ĐƯỜNG DẪN CALLBACK ---
            # Route bên Health: /health/medical-records/<id>/ai-callback
            url = f"{self.health_url}/health/medical-records/{record_id}/ai-callback"
            
            headers = {
                'Authorization': token, 
                'Content-Type': 'application/json'
            }
            
            print(f"🔄 [Integration] Callback to: {url}")
            
            resp = requests.patch(url, json=update_data, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                print(f"✅ Callback Success for {record_id}")
                return True
            else:
                print(f"❌ Callback Failed: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Callback Connection Error: {e}")
            return False