from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import get_auth_handler
from app.features.auth.AuthService import AuthService
from app.features.auth.PasswordService import PasswordService
from app.services.FirebaseAuthHandler import FirebaseAuthHandler
import re

router = APIRouter()


def get_auth_service() -> AuthService:
    """Dependency cung cấp AuthService instance."""
    return AuthService()

def get_password_service() -> PasswordService:
    return PasswordService()



class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email người dùng")
    password: str = Field(..., min_length=8, description="Mật khẩu đăng nhập")


class LoginResponse(BaseModel):
    success: bool
    profile: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CreateStudentRequest(BaseModel):
    student_email: EmailStr = Field(..., description="Email sinh viên")
    student_name: str = Field(..., min_length=2, max_length=100, description="Họ tên sinh viên")
    student_id: str = Field(..., min_length=5, max_length=20, description="Mã số sinh viên (MSSV)")


class CreateStudentResponse(BaseModel):
    success: bool
    uid: Optional[str] = None
    temp_password: Optional[str] = None
    error: Optional[str] = None

class CreateAdvisorRequest(BaseModel):
    advisor_email: EmailStr = Field(..., description="Email giáo viên")
    advisor_name: str = Field(..., min_length=2, max_length=100, description="Họ tên giáo viên")

class CreateAdvisorResponse(BaseModel):
    success: bool
    uid: Optional[str] = None
    temp_password: Optional[str] = None
    error: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Đăng nhập người dùng qua AuthService."""
    result = auth_service.loginUser(payload.email, payload.password)
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Đăng nhập thất bại"))

    return LoginResponse(success=True, profile=result.get("profile"))


@router.post("/students", response_model=CreateStudentResponse, status_code=201)
async def create_student_account(
    payload: CreateStudentRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Admin tạo tài khoản sinh viên qua AuthService."""
    result = auth_service.adminCreateStudentAccount(
        studentEmail=payload.student_email,
        studentName=payload.student_name,
        studentId=payload.student_id,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Không thể tạo tài khoản"))

    return CreateStudentResponse(
        success=True,
        uid=result.get("uid"),
        temp_password=result.get("temp_password"),
    )

@router.post("/advisors", response_model=CreateAdvisorResponse, status_code=201)
async def create_advisor_account(
    payload: CreateAdvisorRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Admin tạo tài khoản giáo viên qua AuthService."""
    result = auth_service.adminCreateAdvisorAccount(
        advisorEmail=payload.advisor_email,
        advisorName=payload.advisor_name,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Không thể tạo tài khoản"))

    return CreateAdvisorResponse(
        success=True,
        uid=result.get("uid"),
        temp_password=result.get("temp_password"),
    )

# ---------------------------------------------------------
# Logout — Thu hồi refresh token Firebase
# ---------------------------------------------------------

class LogoutRequest(BaseModel):
    uid: str = Field(..., min_length=1, description="UID người dùng cần đăng xuất")


class LogoutResponse(BaseModel):
    success: bool
    message: str


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    payload: LogoutRequest,
    auth_handler: FirebaseAuthHandler = Depends(get_auth_handler),
):
    """
    Đăng xuất người dùng — thu hồi toàn bộ refresh token Firebase.
    Frontend cần xóa token cục bộ (sessionStorage/cookie) sau khi gọi endpoint này.

    Tương đương nút 'Thoát (Sign Out)' trong sidebar của main.py cũ.
    """
    print(f"[auth/logout] Đăng xuất UID: {payload.uid}")
    success = auth_handler.signOutUser(payload.uid)

    if not success:
        # Không raise 500 — có thể UID không tồn tại, vẫn nên xóa session phía client
        return LogoutResponse(
            success=False,
            message="Không thể thu hồi token trên server. Vui lòng xóa session thủ công."
        )

    return LogoutResponse(
        message="Đăng xuất thành công. Tất cả phiên đăng nhập đã bị thu hồi."
    )

# ---------------------------------------------------------
# Change Password
# ---------------------------------------------------------

class ChangePasswordRequest(BaseModel):
    uid: str = Field(..., min_length=1, description="UID người dùng cần đổi mật khẩu")
    new_password: str = Field(..., min_length=8, description="Mật khẩu mới")

class ChangePasswordResponse(BaseModel):
    success: bool
    message: str

@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    payload: ChangePasswordRequest,
    password_service: PasswordService = Depends(get_password_service)
):
    """
    Đổi mật khẩu người dùng (Bắt buộc thỏa mãn quy tắc mạnh).
    """
    pwd = payload.new_password
    # Quy tắc: Tối thiểu 8 ký tự, 1 hoa, 1 thường, 1 số
    if len(pwd) < 8 or not re.search(r"[a-z]", pwd) or not re.search(r"[A-Z]", pwd) or not re.search(r"[0-9]", pwd):
        raise HTTPException(
            status_code=400, 
            detail="Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số."
        )
        
    success = password_service.changePassword(payload.uid, payload.new_password)
    if not success:
        raise HTTPException(status_code=500, detail="Đổi mật khẩu thất bại. Vui lòng thử lại.")
        
    return ChangePasswordResponse(success=True, message="Đổi mật khẩu thành công.")
