from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.features.auth.AuthService import AuthService

router = APIRouter()


def get_auth_service() -> AuthService:
    """Dependency cung cấp AuthService instance."""
    return AuthService()


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


class CreateStudentResponse(BaseModel):
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
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Không thể tạo tài khoản"))

    return CreateStudentResponse(
        success=True,
        uid=result.get("uid"),
        temp_password=result.get("temp_password"),
    )
