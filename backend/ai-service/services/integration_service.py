import requests
import os
import tempfile

class IntegrationService:
    def __init__(self):
        self.health_url = os.getenv('HEALTH_SERVICE_URL')
        self.media_url = os.getenv('MEDIA_SERVICE_URL')
        self.recipe_url = os.getenv('RECIPE_SERVICE_URL')

    def get_medical_record_meta(self, record_id, token):
        try:
            headers = {'Authorization': token}
            resp = requests.get(f"{self.health_url}/medical-records/{record_id}", headers=headers)
            return resp.json() if resp.status_code == 200 else None
        except: return None

    def download_file(self, file_url):
        try:
            # Xử lý URL (nếu là localhost/relative)
            if not file_url.startswith('http'):
                file_url = f"{self.media_url}/{file_url.lstrip('/')}"
            
            resp = requests.get(file_url, stream=True)
            if resp.status_code != 200: return None
            
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
            for chunk in resp.iter_content(8192): temp.write(chunk)
            temp.close()
            return temp.name
        except Exception as e:
            print(f"Download Error: {e}")
            return None

    def callback_health_update(self, record_id, extracted_data, text):
        """Cập nhật dữ liệu trích xuất về lại Health DB"""
        try:
            url = f"{self.health_url}/internal/medical-records/{record_id}/update"
            payload = {"status": "processed", "extractedData": extracted_data, "extractedText": text}
            requests.put(url, json=payload)
            print("✅ Callback to Health Service success")
        except Exception as e:
            print(f"❌ Callback Error: {e}")

    def search_recipes(self, keywords=None):
        try:
            # self.recipe_url ví dụ: http://localhost:8080/api/v1/recipes
            url = self.recipe_url 
            params = {'limit': 20} # Lấy 20 món để AI lựa chọn
            
            if keywords:
                params['q'] = keywords
                
            print(f"DEBUG: Calling Recipe Service: {url} with params {params}")
            resp = requests.get(url, params=params, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                recipes = data.get('data', [])
                
                # Filter nhẹ để giảm tải payload cho Gemini (chỉ lấy field cần thiết)
                simplified_recipes = []
                for r in recipes:
                    simplified_recipes.append({
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "ingredients": r.get("ingredients"),
                        "nutrition": r.get("nutrition", {}) # Quan trọng
                    })
                return simplified_recipes
            
            print(f"Recipe Service returned {resp.status_code}")
            return []
            
        except Exception as e:
            print(f"Error calling Recipe Service: {e}")
            return [] # Trả về rỗng nếu lỗi kết nối