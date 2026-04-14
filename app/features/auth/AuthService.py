from typing import Dict, Any, Union, Optional
import streamlit as st
from app.services.FirebaseAuthHandler import FirebaseAuthHandler
from app.services.FirestoreHandler import FirebaseHandler
from app.utils.SecurityHelpers import generateTempPassword
from app.core.ErrorCodes import getErrorMessage

class AuthService:
    """
    Lớp dịch vụ xác thực (Authentication Service).
    Quá trình đăng nhập và tạo người dùng bởi quản trị viên.
    """

    def __init__(self) -> None:
        self.m_authHandler = FirebaseAuthHandler()
        self.m_dbHandler = FirebaseHandler()

    def loginUser(self, email: str, password: str) -> Dict[str, Any]:
        """
        Xác thực người dùng (User login).
        
        Args:
            email (str): Địa chỉ email.
            password (str): Mật khẩu.
            
        Returns:
            Dict[str, Any]: Thông tin user nếu thành công, ngược lại trả về lỗi từ ErrorCodes.
        """
        try:
            # User authentication - Xác thực người dùng
            authResponse = self.m_authHandler.signInWithEmail(email, password)
            
            if not authResponse.get("success"):
                return {"success": False, "error": authResponse.get("error")}
                
            # Get user payload
            data = authResponse.get("data", {})
            uid = data.get("localId")
            
            if not uid:
                return {"success": False, "error": getErrorMessage("not-found")}
                
            # Retrieve User Profile from Firestore
            userProfile = self.m_dbHandler.getUserProfile(uid)
            
            if not userProfile:
                return {"success": False, "error": "Không tìm thấy hồ sơ hệ thống."}

            # Return complete User Profile
            return {
                "success": True, 
                "profile": userProfile
            }
            
        except Exception as e:
            print(f"Lỗi đăng nhập (Login Error): {e}")
            return {"success": False, "error": getErrorMessage("unavailable")}

    def adminCreateStudentAccount(self, studentEmail: str, studentName: str) -> Dict[str, Any]:
        """
        Admin tạo tài khoản sinh viên (Admin-initiated account creation).
        Tích hợp SecurityHelpers để cấp mật khẩu.
        
        Args:
            studentEmail (str): Email sinh viên.
            studentName (str): Tên hiển thị sinh viên.
            
        Returns:
            Dict[str, Any]: Kết quả khởi tạo bao gồm UID và mật khẩu tạm.
        """
        try:
            # Generate Temporary Password - Tạo mật khẩu tạm thời
            tempPassword = generateTempPassword()
            
            # Auth account registration
            uid = self.m_authHandler.createAuthUser(studentEmail, tempPassword)
            
            if not uid:
                return {"success": False, "error": "Không thể tạo tài khoản trên Auth."}
            
            # Khởi tạo hồ sơ tại Firestore (Initialize Firestore profile)
            # SCHEMA Alignment: Thêm các trường theo định nghĩa trong SCHEMA.md
            profileData = {
                "email": studentEmail,
                "full_name": studentName,
                "role": "student", # SCHEMA.md: role là "student" / "advisor" / "admin"
                "requires_password_change": True, # Force password change on first login
                "is_active": True,
                "avatar_url": "",
                "class_id": "",
                "student_id": ""
            }
            
            profileCreated = self.m_dbHandler.createUserProfile(uid, profileData)
            
            if profileCreated:
                 return {
                     "success": True, 
                     "uid": uid,
                     "temp_password": tempPassword
                 }
            else:
                 # Rollback if DB failed
                 self.m_authHandler.deleteAuthUser(uid)
                 return {"success": False, "error": "Không thể tạo hồ sơ trên CSDL."}
                 
        except Exception as e:
            print(f"Lỗi khởi tạo sinh viên (Error creating student): {e}")
            return {"success": False, "error": getErrorMessage("unavailable")}

    def logout(self, uid: Optional[str] = None) -> bool:
        """
        Điều phối đăng xuất người dùng (User logout flow).
        Gọi signOutUser từ tầng hạ tầng và xóa sạch dữ liệu bộ nhớ tạm.
        
        Args:
            uid (Optional[str]): Mã người dùng.
            
        Returns:
            bool: True báo hiệu thành công để giao diện chuyển hướng (Redirect).
        """
        try:
            # Session Termination - Chấm dứt phiên làm việc thông qua Auth Handler
            self.m_authHandler.signOutUser(uid)
            
            # Clear user session data - Xóa sạch bộ nhớ tạm của Streamlit
            for key in list(st.session_state.keys()):
                del st.session_state[key]
                
            return True
        except Exception as e:
            print(f"Lỗi điều phối đăng xuất: {e}")
            # Trong trường hợp có lỗi ở session_state, vẫn ưu tiên Redirect
            return True

