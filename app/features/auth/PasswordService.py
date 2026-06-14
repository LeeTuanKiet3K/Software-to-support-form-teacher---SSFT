from typing import Optional
from app.services.FirebaseAuthHandler import FirebaseAuthHandler
from app.services.FirestoreHandler import FirestoreHandler

class PasswordService:
    def __init__(self) -> None:
        self.m_authHandler = FirebaseAuthHandler()
        self.m_dbHandler = FirestoreHandler()

    def changePassword(self, uid: str, newPassword: str) -> bool:
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
        try:
            link = self.m_authHandler.generatePasswordResetLink(email)
            if link:
                # Có thể xử lý gửi email thực tế tại đây hoặc trả về link
                return link
            return None
            
        except Exception as e:
            print(f"Lỗi khi gửi mail reset mật khẩu (Error sending reset email): {e}")
            return None
