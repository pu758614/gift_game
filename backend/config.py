import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Flask 應用配置"""

    # Flask 基本設定
    SECRET_KEY = os.getenv(
        'FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

    # 資料庫設定
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://giftgame:giftgame123@localhost:5432/giftgame_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Gemini API 設定（用於文字生成）
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # OpenAI API 設定（用於圖片生成）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    # 圖片生成引擎選擇: 'openai' 或 'gemini'
    IMAGE_GENERATION_ENGINE = os.getenv('IMAGE_GENERATION_ENGINE', 'openai')

    # MinIO 設定
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'gift-images')
    MINIO_USE_SSL = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
    MINIO_PUBLIC_URL = os.getenv('MINIO_PUBLIC_URL', 'http://localhost:9000')

    # 上傳檔案設定 (保留以向後相容)
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # CORS 設定 - 允許所有來源以支援手機瀏覽
    CORS_ORIGINS = '*'
