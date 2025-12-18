import os
import yaml


class Config:
    # Đọc configuration từ application.yaml
    @staticmethod
    def load_yaml_config():
        """Load configuration từ application.yaml file"""
        config_path = os.path.join(os.path.dirname(__file__), 'application.yaml')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        return {}

    # Load yaml config
    yaml_config = load_yaml_config()
    SQLALCHEMY_DATABASE_URI: str = yaml_config['database']['url']
    