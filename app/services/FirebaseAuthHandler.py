import os
import requests
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from app.core.Config import AppConfig

class FirebaseAuthHandler:
    """
    Lớp xử lý xác thực (Authentication Handler Layer) hoạt động hoàn hảo với Dependency Injection.
    Quản lý đăng nhập, đăng xuất và phiên hoạt động của người dùng.
    """

    def __init__(self) -> None:
        """
        Khởi tạo dịch vụ xác thực (Initialize Firebase Authentication).
        """
        self.m_serviceAccountPath = AppConfig.FIREBASE_SERVICE_ACCOUNT_JSON
        self.m_webApiKey = os.getenv("FIREBASE_WEB_API_KEY") 
        
        if not self.m_serviceAccountPath:
            raise ValueError("Lỗi: FIREBASE_SERVICE_ACCOUNT_JSON không được tìm thấy trong cấu hình.")
            
        # Chỉ khởi tạo app nếu chưa tồn tại (Prevent multiple app initializations)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.m_serviceAccountPath)
            firebase_admin.initialize_app(cred)

    def signIn(self, email: str, password: str) -> Dict[str, Any]:
        """
        Đăng nhập người dùng (User Sign In) bằng Identity Toolkit REST API.
        
        Args:
           email (str): Địa chỉ email.
           password (str): Mật khẩu.
           
        Returns:
           Dict[str, Any]: Payload xác thực chứa 'success', và 'data'/token nếu thành công.
        """
        if not self.m_webApiKey:
            return {"success": False, "error": "Lỗi cấu hình: Thiếu FIREBASE_WEB_API_KEY."}
            
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.m_webApiKey}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            
            if response.status_code == 200:
                return {"success": True, "data": data}
            else:
                errorMsg = data.get("error", {}).get("message", "Lỗi không xác định")
                return {"success": False, "error": f"Lỗi xác thực (Auth Error): {errorMsg}"}
                
        except Exception as e:
            return {"success": False, "error": f"Lỗi kết nối (Connection Error): {e}"}

    def signOut(self, uid: str) -> bool:
        """
        Đăng xuất người dùng (User Sign Out).
        Thu hồi token refresh của người dùng.
        
        Args:
            uid (str): Mã người dùng (User ID) trên Firebase.
            
        Returns:
            bool: Trạng thái thu hồi thành công.
        """
        try:
            auth.revoke_refresh_tokens(uid)
            return True
        except auth.UserNotFoundError:
            print("Lỗi (Error): Người dùng không tồn tại.")
            return False
        except Exception as e:
            print(f"Lỗi khi thu hồi token đăng xuất (Log out error): {e}")
            return False

    def getCurrentUser(self, idToken: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin người dùng hiện tại (Get Current User) dựa trên mã ID Token.
        
        Args:
            idToken (str): Token được cấp khi người dùng signIn thành công.
            
        Returns:
            Optional[Dict]: Dữ liệu giải mã của phiên hoạt động, hoặc None nếu Token không hợp lệ.
        """
        try:
            decodedToken = auth.verify_id_token(idToken)
            return decodedToken
        except auth.ExpiredIdTokenError:
            print("Lỗi (Error): Phiên hoạt động đã hết hạn (Token expired).")
            return None
        except Exception as e:
            print(f"Lỗi xác thực Token (Invalid token): {e}")
            return None
