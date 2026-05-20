from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
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
# Endpoints
# ---------------------------------------------------------

@router.get("/grades/{student_id}", response_model=AcademicRecordResponse)
async def get_student_grades(
    student_id: str,
    db_handler: FirestoreHandler = Depends(get_firestore_handler),
):
    """
    Lấy thông tin điểm số của sinh viên từ Firestore.
    Trả về bảng điểm đầy đủ bao gồm GPA và trạng thái cảnh báo học vụ.
    """
    print(f"[academic/grades] Truy xuất bảng điểm SV: {student_id}")
    try:
        record = db_handler.getDocument(
            collectionName="Academic_records",
            documentId=student_id,
        )
    except Exception as e:
        print(f"[academic/grades] Lỗi truy xuất Firestore (DB read error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Không thể truy xuất bảng điểm. Vui lòng thử lại."
        )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy bảng điểm của sinh viên: {student_id}"
        )

    # Chuyển đổi subjects từ Firestore (list of dict) sang schema SubjectScore
    raw_subjects = record.get("subjects", [])
    subjects = [
        SubjectScore(
            subject_name=s.get("subject_name", ""),
            score=float(s.get("score", 0.0))
        )
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
    """
    Thêm hoặc cập nhật bảng điểm của sinh viên.
    AcademicService sẽ tự động kích hoạt AcademicObserver để:
    - Kiểm tra ngưỡng GPA
    - Gửi cảnh báo học vụ nếu GPA giảm dưới mức cho phép
    - Tạo thông báo cho GVCN nếu cần thiết
    """
    print(f"[academic/grades] Nhập điểm SV: {payload.student_id}, GPA: {payload.gpa}")

    # Chuyển đổi sang dict để AcademicService xử lý
    data = {
        "student_id": payload.student_id,
        "class_id": payload.class_id,
        "subjects": [s.model_dump() for s in payload.subjects],
        "gpa": payload.gpa,
    }

    try:
        success = academic_service.inputGrade(data)
    except Exception as e:
        print(f"[academic/grades] Lỗi nhập điểm (grade input error): {e}")
        raise HTTPException(
            status_code=500,
            detail="Không thể lưu bảng điểm. Vui lòng thử lại."
        )

    if not success:
        raise HTTPException(
            status_code=422,
            detail=f"Dữ liệu không hợp lệ hoặc thiếu student_id: {payload.student_id}"
        )

    return AcademicSaveResponse(
        success=True,
        student_id=payload.student_id,
        message=f"Đã lưu bảng điểm cho sinh viên {payload.student_id}. Observer học vụ đã được kích hoạt.",
    )
