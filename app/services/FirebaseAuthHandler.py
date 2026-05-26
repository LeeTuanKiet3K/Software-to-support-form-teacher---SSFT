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

    def signInWithEmail(self, email: str, password: str) -> Dict[str, Any]:
        """
        Đăng nhập người dùng (User Sign In) bằng Identity Toolkit REST API.
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
                from app.core.ErrorCodes import getErrorMessage
                errorMsg = data.get("error", {}).get("message", "")
                # Map standard REST API errors to custom error codes if needed, otherwise fallback
                mappedError = getErrorMessage(errorMsg)
                if mappedError == "Đã xảy ra lỗi không xác định.":
                    mappedError = f"Lỗi xác thực (Auth Error): {errorMsg}"
                return {"success": False, "error": mappedError}
                
        except Exception as e:
            return {"success": False, "error": f"Lỗi kết nối (Connection Error): {e}"}

    def signIn(self, email: str, password: str) -> Dict[str, Any]:
        """
        Alias tương thích ngược cho lớp UI cũ.
        """
        return self.signInWithEmail(email, password)

    def signOutUser(self, uid: str) -> bool:
        """
        Đăng xuất người dùng (User Sign Out).
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

    def signOut(self, uid: str) -> bool:
        """
        Alias tương thích ngược cho lớp UI cũ.
        """
        return self.signOutUser(uid)

    def getCurrentUser(self, idToken: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin người dùng hiện tại.
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

    def createAuthUser(self, email: str, password: str) -> Optional[str]:
        """
        Tạo người dùng mới trên Firebase Auth.
        """
        try:
            userRecord = auth.create_user(email=email, password=password)
            return userRecord.uid
        except Exception as e:
            from app.core.ErrorCodes import getErrorMessage
            print(f"Lỗi tạo tài khoản Auth (Auth creation error): {e}")
            return None

    def deleteAuthUser(self, uid: str) -> bool:
        """
        Xóa tài khoản người dùng trên Firebase Auth.
        """
        try:
            auth.delete_user(uid)
            return True
        except Exception as e:
            print(f"Lỗi xóa tài khoản Auth (Auth deletion error): {e}")
            return False

    def updatePassword(self, uid: str, newPassword: str) -> bool:
        """
        Cập nhật mật khẩu người dùng.
        """
        try:
            auth.update_user(uid, password=newPassword)
            return True
        except Exception as e:
            print(f"Lỗi cập nhật mật khẩu (Password update error): {e}")
            return False

    def generatePasswordResetLink(self, email: str) -> Optional[str]:
        """
        Tạo link đặt lại mật khẩu.
        """
        try:
            link = auth.generate_password_reset_link(email)
            return link
        except Exception as e:
            print(f"Lỗi tạo link đặt lại mật khẩu (Reset link error): {e}")
            return None
