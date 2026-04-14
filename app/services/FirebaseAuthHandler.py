import os
import requests
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

from app.core.ErrorCodes import getErrorMessage

# Nạp các biến môi trường từ tập tin .env
load_dotenv()

class FirebaseAuthHandler:
    """
    Lớp xử lý xác thực Firebase (Firebase Auth Handler) đóng vai trò hạ tầng (Infrastructure Layer).
    Quản lý xác thực, token và vòng đời tài khoản thông qua Firebase Admin SDK và Firebase REST API.
    """

    def __init__(self) -> None:
        """
        Khởi tạo dịch vụ (Initialize services) và kết nối tới Firebase Auth.
        """
        self.m_serviceAccountPath = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        # Sử dụng cho việc xác thực người dùng bằng API Identity Toolkit
        self.m_webApiKey = os.getenv("FIREBASE_WEB_API_KEY") 
        
        if not self.m_serviceAccountPath:
            raise ValueError("Lỗi: FIREBASE_SERVICE_ACCOUNT_PATH không được tìm thấy trong tệp .env.")
            
        # Chỉ khởi tạo app nếu chưa tồn tại (Prevent multiple app initializations)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.m_serviceAccountPath)
            firebase_admin.initialize_app(cred)

    def verifyIdToken(self, idToken: str) -> Optional[Dict[str, Any]]:
        """
        Xác thực và giải mã mã định danh (Verify and Decode ID Token) gửi từ Client.
        
        Args:
            idToken (str): Token JWT lấy từ phía client.
            
        Returns:
            Optional[Dict]: Thông tin giải mã của payload nếu hợp lệ, None nếu gặp lỗi.
        """
        try:
            # Decode ID Token - Giải mã mã định danh
            decodedToken = auth.verify_id_token(idToken)
            return decodedToken
        except auth.ExpiredIdTokenError:
            # Token đã hết hạn - Expired token
            print("Lỗi: ID Token đã hết hạn.")
            return None
        except Exception as e:
            # Lỗi xác thực token chung
            print(f"Lỗi xác thực Token: {e}")
            return None

    def signInWithEmail(self, email: str, password: str) -> Dict[str, Any]:
        """
        Xác thực người dùng (User Authentication) qua Email/Password bằng Identity Toolkit REST API.
        Lý do: Firebase Admin SDK không hỗ trợ đăng nhập email/password trực tiếp từ server.
        
        Args:
           email (str): Địa chỉ email.
           password (str): Mật khẩu.
           
        Returns:
           Dict[str, Any]: Chứa 'success' (bool) và 'data' hoặc 'error' tiếng Việt.
        """
        if not self.m_webApiKey:
            return {"success": False, "error": "Lỗi cấu hình: Thiếu FIREBASE_WEB_API_KEY trong tệp .env."}
            
        # REST API endpoint cho tính năng signInWithPassword
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.m_webApiKey}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            # Gửi HTTP POST request để xác thực bằng REST API
            response = requests.post(url, json=payload)
            data = response.json()
            
            if response.status_code == 200:
                # Đăng nhập thành công (Login successful)
                return {"success": True, "data": data}
            else:
                # Trích xuất mã lỗi từ phản hồi Firebase (Extract error mapping)
                errorMsg = data.get("error", {}).get("message", "")
                
                # Ánh xạ mã lỗi REST API sang mã lỗi Firebase Admin tương đối
                if errorMsg in ["INVALID_PASSWORD", "INVALID_LOGIN_CREDENTIALS"]:
                    errorCode = "auth/wrong-password"
                elif errorMsg in ["EMAIL_NOT_FOUND", "USER_NOT_FOUND"]:
                    errorCode = "auth/user-not-found"
                elif errorMsg == "MISSING_PASSWORD":
                    errorCode = "auth/invalid-email" 
                else:
                    errorCode = errorMsg
                    
                # Chuyển đổi mã lỗi sang tiếng Việt (Convert to Vietnamese error message)
                friendlyError = getErrorMessage(errorCode)
                return {"success": False, "error": friendlyError}
                
        except Exception as e:
            return {"success": False, "error": getErrorMessage("unavailable")}

    def createAuthUser(self, email: str, tempPassword: str) -> Optional[str]:
        """
        Tạo người dùng mới (Create auth user) thông qua quyền quản trị viên (Admin-initiated).
        
        Args:
            email (str): Email sinh viên hoặc giáo viên.
            tempPassword (str): Mật khẩu khởi tạo.
            
        Returns:
            Optional[str]: Trả về UID của người dùng mới nếu thành công, None nếu thất bại.
        """
        try:
            # Đăng ký tài khoản (Register user on Firebase Auth)
            userRecord = auth.create_user(email=email, password=tempPassword)
            return userRecord.uid
        except auth.EmailAlreadyExistsError:
            print(getErrorMessage("auth/email-already-in-use"))
            return None
        except Exception as e:
            print(f"Lỗi hệ thống khi tạo tài khoản: {e}")
            return None

    def deleteAuthUser(self, uid: str) -> bool:
        """
        Xóa người dùng (Delete user account) khỏi hệ thống Firebase Auth.
        
        Args:
            uid (str): Mã định danh (UID) người dùng.
            
        Returns:
            bool: True nếu xóa thành công, False nếu xuất hiện lỗi.
        """
        try:
            # Lệnh xóa người dùng (Execute deletion request)
            auth.delete_user(uid)
            return True
        except auth.UserNotFoundError:
            print(getErrorMessage("auth/user-not-found"))
            return False
        except Exception as e:
            print(f"Lỗi hệ thống khi xóa tài khoản: {e}")
            return False

    def updatePassword(self, uid: str, newPassword: str) -> bool:
        """
        Cập nhật mật khẩu mới (Update user password) từ bảng quản trị hoặc ứng dụng.
        
        Args:
            uid (str): Mã định danh (UID) của người dùng.
            newPassword (str): Mật khẩu mới cần cập nhật.
            
        Returns:
            bool: True nếu thay đổi thành công, False nếu thất bại.
        """
        try:
            # Đổi mật khẩu (Execute password change)
            auth.update_user(uid, password=newPassword)
            return True
        except auth.UserNotFoundError:
            print(getErrorMessage("auth/user-not-found"))
            return False
        except Exception as e:
            print(f"Lỗi khi cập nhật mật khẩu: {e}")
            return False

    def generatePasswordResetLink(self, email: str) -> Optional[str]:
        """
        Tạo liên kết khôi phục mật khẩu (Generate password reset link) gửi qua email.
        Tuân thủ quy trình bảo mật (Password Reset Protocol) thay vì nhập mã OTP.
        
        Args:
            email (str): Email của người dùng đã cung cấp lúc quên mật khẩu.
            
        Returns:
            Optional[str]: Đường dẫn URL khôi phục mật khẩu, hoặc None nếu tài khoản không tồn tại.
        """
        try:
            # Tạo đường link (Generate auth reset URL)
            link = auth.generate_password_reset_link(email)
            return link
        except auth.UserNotFoundError:
            print(getErrorMessage("auth/user-not-found"))
            return None
        except Exception as e:
            print(f"Lỗi khi tạo link đặt lại mật khẩu: {e}")
            return None

    def signOutUser(self, uid: Optional[str] = None) -> bool:
        """
        Xử lý đăng xuất ở hệ thống (Session Termination).
        Thu hồi token làm mới của người dùng nếu cung cấp UID để vô hiệu hóa phiên.
        
        Args:
            uid (Optional[str]): Mã người dùng (User ID) trên Firebase.
            
        Returns:
            bool: Trạng thái thực hiện (Đã hoàn tất đăng xuất).
        """
        try:
            if uid:
                # Thu hồi toàn bộ Refresh Tokens
                auth.revoke_refresh_tokens(uid)
            return True
        except auth.UserNotFoundError:
            print(getErrorMessage("auth/user-not-found"))
            return True  # Dù lỗi cũng coi như đã đăng xuất
        except Exception as e:
            print(f"Lỗi khi thu hồi token đăng xuất: {e}")
            return True

