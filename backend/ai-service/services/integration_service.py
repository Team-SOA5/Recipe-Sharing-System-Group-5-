import requests
import os
import tempfile

class IntegrationService:
    def __init__(self):
        # Lưu ý: Trong .env nên để http://127.0.0.1:8091 (không có dấu / ở cuối)
        self.health_url = os.getenv('HEALTH_SERVICE_URL', 'http://127.0.0.1:8091')
        self.media_url = os.getenv('MEDIA_SERVICE_URL', 'http://127.0.0.1:8888')
        self.recipe_url = os.getenv('RECIPE_SERVICE_URL', 'http://127.0.0.1:8082')

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
            # Gọi trực tiếp Recipe Service
            # Recipe service blueprint được register với url_prefix='/recipes'
            # Vậy endpoint là: http://localhost:8082/recipes (không có /api/v1)
            url = f"{self.recipe_url}/recipes"
            params = {'limit': 20}  # Lấy nhiều món hơn để AI có nhiều lựa chọn
            
            if keywords:
                params['q'] = keywords
                
            print(f"🍳 [Integration] Calling Recipe Service: {url} | Params: {params}")
            
            # Không cần authentication cho GET /recipes (public route)
            resp = requests.get(url, params=params, timeout=10)
            
            print(f"📊 [Integration] Recipe Service Response Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"📊 [Integration] Recipe Service Response Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                recipes = data.get('data', [])
                
                print(f"✅ [Integration] Received {len(recipes)} recipes from Recipe Service")
                if len(recipes) > 0:
                    print(f"📋 [Integration] First recipe sample (keys): {list(recipes[0].keys()) if recipes[0] else 'empty'}")
                    print(f"📋 [Integration] First recipe ID: {recipes[0].get('id') if recipes[0] else 'none'}")
                else:
                    pagination = data.get('pagination', {})
                    total_items = pagination.get('totalItems', 'unknown')
                    print(f"⚠️ [Integration] No recipes in response. Total items in DB: {total_items}, Current page: {pagination.get('page', 'unknown')}, Limit: {pagination.get('limit', 'unknown')}")
                
                # Trả về đầy đủ thông tin để AI có thể đánh giá
                simplified_recipes = []
                for r in recipes:
                    # Lấy ingredients từ detail nếu có, hoặc từ summary
                    ingredients_list = r.get("ingredients", [])
                    if isinstance(ingredients_list, list) and len(ingredients_list) > 0:
                        # Nếu là list of objects, lấy name
                        if isinstance(ingredients_list[0], dict):
                            ingredients_str = ", ".join([ing.get("name", "") for ing in ingredients_list])
                        else:
                            ingredients_str = ", ".join(ingredients_list)
                    else:
                        ingredients_str = ""
                    
                    simplified_recipes.append({
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "description": r.get("description", ""),
                        "ingredients": ingredients_str,
                        "difficulty": r.get("difficulty", ""),
                        "cookingTime": r.get("cookingTime", 0),
                        "nutritionInfo": r.get("nutritionInfo", {})
                    })
                return simplified_recipes
            else:
                print(f"❌ [Integration] Recipe Service error response (Status {resp.status_code}): {resp.text}")
                return []
            
        except requests.exceptions.RequestException as e:
            print(f"❌ [Integration] Request error calling Recipe Service: {e}")
            import traceback
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"❌ [Integration] Unexpected error calling Recipe Service: {e}")
            import traceback
            traceback.print_exc()
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