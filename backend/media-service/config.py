import yaml
import os

class Config:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        try:
            # Đảm bảo file application.yaml nằm cùng cấp với app.py
            with open("application.yaml", "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("Warning: application.yaml not found")
            return {}

    @property
    def port(self):
        return self.config.get('server', {}).get('port', 8090)

    @property
    def context_path(self):
        return self.config.get('server', {}).get('servlet', {}).get('context-path', '/media')

    @property
    def mongo_uri(self):
        return self.config.get('spring', {}).get('data', {}).get('mongodb', {}).get('uri')

    @property
    def storage_dir(self):
        path = self.config.get('app', {}).get('file', {}).get('storage-dir', './file-storage')
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def download_prefix(self):
        return self.config.get('app', {}).get('file', {}).get('download-prefix')

# --- QUAN TRỌNG: DÒNG NÀY PHẢI CÓ ĐỂ CÁC FILE KHÁC IMPORT ĐƯỢC ---
app_config = Config()