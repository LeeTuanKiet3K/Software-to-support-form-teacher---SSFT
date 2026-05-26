import time
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.api.deps import get_academic_service, get_firestore_handler
from app.features.academic.AcademicService import AcademicService
from app.services.FirestoreHandler import FirestoreHandler

router = APIRouter()

# ---------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------
class SubjectScore(BaseModel):
    subject_name: str = Field(..., description="Tên môn học")
    score: float = Field(..., description="Điểm số môn học (thang 10)", ge=0.0, le=10.0)

class AcademicRecordBase(BaseModel):
    student_id: str = Field(..., description="UID sinh viên")
    class_id: str = Field(..., description="Mã lớp")
    subjects: List[SubjectScore] = Field(default_factory=list, description="Danh sách môn học và điểm số")
    gpa: float = Field(..., description="Điểm trung bình học kỳ/năm (thang 10)", ge=0.0, le=10.0)

class AcademicRecordCreate(AcademicRecordBase):
    pass

class AcademicRecordResponse(AcademicRecordBase):
    is_low_score: Optional[bool] = Field(None, description="True nếu GPA dưới ngưỡng cảnh báo")
    ai_check_sent: Optional[bool] = Field(None, description="True nếu đã gửi cảnh báo AI cho GVCN")
    updated_at: Optional[datetime] = Field(None, description="Thời gian cập nhật cuối")

class AcademicSaveResponse(BaseModel):
    success: bool
    student_id: str
    message: str


# ---------------------------------------------------------
# Endpoints Cũ (Cá nhân)
# ---------------------------------------------------------
@router.get("/grades/{student_id}", response_model=AcademicRecordResponse)
async def get_student_grades(
    student_id: str,
    db_handler: FirestoreHandler = Depends(get_firestore_handler),
):
    print(f"[academic/grades] Truy xuất bảng điểm SV: {student_id}")
    try:
        record = db_handler.getDocument(
            collectionName="Academic_records",
            documentId=student_id,
        )
    except Exception as e:
        print(f"[academic/grades] Lỗi truy xuất Firestore (DB read error): {e}")
        raise HTTPException(status_code=500, detail="Không thể truy xuất bảng điểm.")

    if not record:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bảng điểm: {student_id}")

    raw_subjects = record.get("subjects", [])
    subjects = [
        SubjectScore(subject_name=s.get("subject_name", ""), score=float(s.get("score", 0.0)))
        for s in raw_subjects
    ]

    return AcademicRecordResponse(
        student_id=record.get("student_id", student_id),
        class_id=record.get("class_id", ""),
        subjects=subjects,
        gpa=float(record.get("gpa", 0.0)),
        is_low_score=record.get("is_low_score"),
        ai_check_sent=record.get("ai_check_sent"),
        updated_at=record.get("updated_at"),
    )

@router.post("/grades", response_model=AcademicSaveResponse, status_code=201)
async def add_or_update_student_grades(
    payload: AcademicRecordCreate,
    academic_service: AcademicService = Depends(get_academic_service),
):
    print(f"[academic/grades] Nhập điểm SV: {payload.student_id}, GPA: {payload.gpa}")
    data = {
        "student_id": payload.student_id,
        "class_id": payload.class_id,
        "subjects": [s.model_dump() for s in payload.subjects],
        "gpa": payload.gpa,
    }
    try:
        success = academic_service.inputGrade(data)
    except Exception as e:
        print(f"[academic/grades] Lỗi nhập điểm: {e}")
        raise HTTPException(status_code=500, detail="Không thể lưu bảng điểm.")

    if not success:
        raise HTTPException(status_code=422, detail="Dữ liệu không hợp lệ")

    return AcademicSaveResponse(success=True, student_id=payload.student_id, message="Đã lưu bảng điểm.")


# ---------------------------------------------------------
# CÁC ENDPOINT MỚI (Đồng bộ với Frontend Dashboard)
# ---------------------------------------------------------
@router.get("/class/{class_id}/grades")
async def get_class_grades(class_id: str):
    """Lấy danh sách điểm của toàn bộ lớp (Dành cho trang Quản lý Học vụ)"""
    print(f"[academic/class] Truy xuất bảng điểm lớp: {class_id}")
    # Mock data phase 1 - Phase 2 thay bằng query Firestore
    mock_students = [
        {"student_id": "24120101", "name": "Trần Quang Tuấn", "gpa": 1.8, "is_low_score": True},
        {"student_id": "24120102", "name": "Nguyễn Thị Bé", "gpa": 3.2, "is_low_score": False},
        {"student_id": "24120103", "name": "Lê Văn Cường", "gpa": 2.5, "is_low_score": False},
        {"student_id": "24120104", "name": "Phạm Minh Đức", "gpa": 3.8, "is_low_score": False},
        {"student_id": "24120105", "name": "Hoàng Thị Yến", "gpa": 2.0, "is_low_score": True},
    ]
    return mock_students

@router.get("/class/{class_id}/students")
async def get_class_students(class_id: str):
    """Lấy danh sách sinh viên tổng quan (Dành cho trang Quản lý Sinh viên)"""
    mock_data = [
        {"id": "24120101", "name": "Trần Quang Tuấn", "class": class_id, "status": "Nguy cơ", "gpa": 1.8, "stress": "Cao"},
        {"id": "24120102", "name": "Nguyễn Thị Bé", "class": class_id, "status": "An toàn", "gpa": 3.2, "stress": "Thấp"},
        {"id": "24120103", "name": "Lê Văn Cường", "class": class_id, "status": "Cảnh báo", "gpa": 2.5, "stress": "Vừa"},
        {"id": "24120104", "name": "Phạm Minh Đức", "class": class_id, "status": "An toàn", "gpa": 3.8, "stress": "Thấp"},
    ]
    return mock_data

@router.post("/grades/upload")
async def upload_grades_file(file: UploadFile = File(...)):
    """Nhận file Excel/CSV bảng điểm từ GVCN tải lên"""
    print(f"[academic/upload] Nhận file: {file.filename}")
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .csv hoặc .xlsx")
    
    # Giả lập thời gian hệ thống AI phân tích file
    time.sleep(1.5)
    
    return {
        "success": True,
        "message": f"Đã tải lên và xử lý file {file.filename}",
    }