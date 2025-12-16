import os
import yaml

class Config:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        try:
            # [TỐI ƯU] Lấy đường dẫn tuyệt đối dựa trên vị trí file config.py
            # Giúp code chạy đúng dù bạn đứng ở bất kỳ folder nào trong terminal
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "application.yaml")
            
            with open(config_path, "r", encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    @property
    def port(self):
        return self.config.get('server', {}).get('port', 8090)

    @property
    def context_path(self):
        return self.config.get('server', {}).get('servlet', {}).get('context-path', '/media')

    @property
    def mongo_uri(self):
        uri = self.config.get('spring', {}).get('data', {}).get('mongodb', {}).get('uri')
        if not uri:
            # Fallback nếu quên config DB, tránh crash app
            return "mongodb://localhost:27017/media_db" 
        return uri

    @property
    def storage_dir(self):
        path = self.config.get('app', {}).get('file', {}).get('storage-dir', './file-storage')
        # Chuyển thành đường dẫn tuyệt đối để tránh lưu lung tung
        if not os.path.isabs(path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, path)
            
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def download_prefix(self):
        # Mặc định trả về context path nếu không cấu hình
        return self.config.get('app', {}).get('file', {}).get('download-prefix', '/media/download')

    @property
    def llama_api_key(self):
        # Lấy key từ biến môi trường (ưu tiên) hoặc file yaml
        return os.getenv("LLAMA_CLOUD_API_KEY") or \
               self.config.get('app', {}).get('llama', {}).get('api-key')

# --- KHỞI TẠO INSTANCE ---
app_config = Config()