import os
from dotenv import load_dotenv

# Nạp file .env chứa các biến môi trường
load_dotenv()

# Lớp cấu hình ứng dụng (Application Configuration) lấy dữ liệu từ biến môi trường.
class AppConfig:
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_DATAHELPER_API_KEY=os.getenv("GROQ_DATAHELPER_API_KEY")
