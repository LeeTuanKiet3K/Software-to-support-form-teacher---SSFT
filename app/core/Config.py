import os
from dotenv import load_dotenv

# Nạp file .env chứa các biến môi trường
load_dotenv()

def loadConfig() -> dict:
    """
    Nạp các biến môi trường và trả về dict cấu hình.
    """
    m_configDict = {
# Lấy đường dẫn file Key Firebase từ .env
        "FIREBASE_KEY": os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH"), 
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "AI_ENABLED": os.getenv("AI_ENABLED", "True").lower() == "true",
        "SYSTEM_VERSION": os.getenv("SYSTEM_VERSION", "1.0.0-beta")
    }
    return m_configDict

def isAiEnabled() -> bool:
    """
    Kiểm tra trạng thái bật/tắt AI.
    """
    return os.getenv("AI_ENABLED", "True").lower() == "true"

def getSystemVersion() -> str:
    """
    Trả về phiên bản hiện tại.
    """
    return os.getenv("SYSTEM_VERSION", "1.0.0")
