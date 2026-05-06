from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

# Import dependencies
from app.api.deps import get_academic_service

router = APIRouter()

# ---------------------------------------------------------
# Pydantic Schemas (Model Validation)
# ---------------------------------------------------------

class SubjectScore(BaseModel):
    subject_name: str = Field(..., description="Tên môn học")
    score: float = Field(..., description="Điểm số môn học", ge=0.0, le=10.0)

class AcademicRecordBase(BaseModel):
    student_id: str = Field(..., description="UID sinh viên")
    class_id: str = Field(..., description="Mã lớp")
    subjects: List[SubjectScore] = Field(default_factory=list, description="Danh sách môn học và điểm số")
    gpa: float = Field(..., description="Điểm trung bình học kỳ/năm", ge=0.0, le=10.0)

class AcademicRecordCreate(AcademicRecordBase):
    pass

class AcademicRecordResponse(AcademicRecordBase):
    updated_at: Optional[datetime] = Field(None, description="Thời gian cập nhật")

# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@router.get("/grades/{student_id}", response_model=AcademicRecordResponse)
async def get_student_grades(
    student_id: str,
    academic_service = Depends(get_academic_service)
):
    """
    Lấy thông tin điểm số của sinh viên dựa trên student_id.
    """
    # Ghi chú: Ở bản thực tế, đoạn này sẽ gọi:
    # record = await academic_service.get_academic_record(student_id)
    # if not record:
    #     raise HTTPException(status_code=404, detail="Không tìm thấy bảng điểm")
    # return record
    
    # Mock Response
    return AcademicRecordResponse(
        student_id=student_id,
        class_id="24CTT4",
        subjects=[SubjectScore(subject_name="Toán cao cấp", score=8.5)],
        gpa=8.5,
        updated_at=datetime.utcnow()
    )

@router.post("/grades", response_model=AcademicRecordResponse, status_code=201)
async def add_student_grades(
    payload: AcademicRecordCreate,
    academic_service = Depends(get_academic_service)
):
    """
    Thêm hoặc cập nhật bảng điểm của sinh viên.
    """
    # Ghi chú: Ở bản thực tế, đoạn này sẽ gọi:
    # result = await academic_service.save_academic_record(payload.model_dump())
    # return result
    
    # Mock Response
    return AcademicRecordResponse(
        student_id=payload.student_id,
        class_id=payload.class_id,
        subjects=payload.subjects,
        gpa=payload.gpa,
        updated_at=datetime.utcnow()
    )
