from typing import Optional
from app.services.FirebaseAuthHandler import FirebaseAuthHandler
from app.services.FirestoreHandler import FirestoreHandler

class PasswordService:
    """
    Lớp dịch vụ quản lý mật khẩu (Password Management Service).
    Tích hợp hạ tầng Firebase để cập nhật và khôi phục mật khẩu.
    """

    def __init__(self) -> None:
        self.m_authHandler = FirebaseAuthHandler()
        self.m_dbHandler = FirestoreHandler()

    def changePassword(self, uid: str, newPassword: str) -> bool:
        """
        Đổi mật khẩu người dùng (Change user password).
        Gọi FirebaseAuthHandler để cập nhật mật khẩu, sau đó update Firestore.
        
        Args:
            uid (str): ID người dùng.
            newPassword (str): Mật khẩu mới để cập nhật.
            
        Returns:
            bool: True nếu thành công, False nếu thất bại.
        """
        try:
            # Update password using Auth Handler
            success = self.m_authHandler.updatePassword(uid, newPassword)
            if not success:
                return False
                
            # Update 'requires_password_change' flag using Firestore Handler
            return self.m_dbHandler.updateDocument(
                collectionName="Users",
                documentId=uid,
                data={"requires_password_change": False}
            )
            
        except Exception as e:
            print(f"Lỗi khi đổi mật khẩu (Error changing password): {e}")
            return False

    def sendResetPasswordEmail(self, email: str) -> Optional[str]:
        """
        Gửi yêu cầu đặt lại mật khẩu (Send password reset email).
        
        Args:
            email (str): Địa chỉ email.
            
        Returns:
            str: Link phục hồi mật khẩu nếu thành công, None nếu thất bại.
        """
        try:
            link = self.m_authHandler.generatePasswordResetLink(email)
            if link:
                # Có thể xử lý gửi email thực tế tại đây hoặc trả về link
                return link
            return None
            
        except Exception as e:
            print(f"Lỗi khi gửi mail reset mật khẩu (Error sending reset email): {e}")
            return None
