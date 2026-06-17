import time
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
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
# Endpoints dành cho Sinh viên (Student-facing API)
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
# Endpoints dành cho Giáo viên chủ nhiệm (Advisor-facing API)
# ---------------------------------------------------------
@router.get("/class/{class_id}/grades")
async def get_class_grades(
    class_id: str,
    db_handler: FirestoreHandler = Depends(get_firestore_handler)
):
    """Lấy danh sách điểm của toàn bộ lớp (Dành cho trang Quản lý Học vụ)"""
    print(f"[academic/class] Truy xuất bảng điểm lớp: {class_id}")
    
    users = db_handler.queryDocuments(
        collectionName="Users",
        filters=[("role", "==", "student"), ("class_id", "==", class_id)]
    )
    
    students_data = []
    for user in users:
        student_id = user.get("student_id")
        full_name = user.get("full_name", "Ẩn danh")
        
        gpa = 0.0
        is_low_score = False
        
        if student_id:
            record = db_handler.getDocument("Academic_records", documentId=student_id)
            if record:
                gpa = float(record.get("gpa", 0.0))
                is_low_score = bool(record.get("is_low_score", gpa < 2.0))
                
        students_data.append({
            "student_id": student_id or user.get("id", ""),
            "name": full_name,
            "gpa": gpa,
            "is_low_score": is_low_score
        })
        
    return students_data

@router.get("/class/{class_id}/students")
async def get_class_students(
    class_id: str,
    db_handler: FirestoreHandler = Depends(get_firestore_handler)
):
    """Lấy danh sách sinh viên tổng quan (Dành cho trang Quản lý Sinh viên)"""
    users = db_handler.queryDocuments(
        collectionName="Users",
        filters=[("role", "==", "student"), ("class_id", "==", class_id)]
    )
    
    students_data = []
    for user in users:
        student_id = user.get("student_id")
        full_name = user.get("full_name", "Ẩn danh")
        
        gpa = 0.0
        if student_id:
            record = db_handler.getDocument("Academic_records", documentId=student_id)
            if record:
                gpa = float(record.get("gpa", 0.0))
                
        status = "An toàn"
        stress = "Thấp"
        
        if record is None:
            status = "Chưa có điểm"
            stress = "Thấp"
        elif gpa < 2.0:
            status = "Nguy cơ"
            stress = "Cao"
        elif gpa < 2.5:
            status = "Cảnh báo"
            stress = "Vừa"
            
        students_data.append({
            "id": student_id or user.get("id", ""),
            "name": full_name,
            "class": class_id,
            "status": status,
            "gpa": gpa,
            "stress": stress
        })
        
    return students_data

@router.post("/grades/upload")
async def upload_grades_file(
    file: UploadFile = File(...),
    class_id: Optional[str] = Form(None),
    db_handler: FirestoreHandler = Depends(get_firestore_handler),
    academic_service: AcademicService = Depends(get_academic_service)
):
    """Nhận file Excel/CSV bảng điểm từ GVCN tải lên và cập nhật điểm"""
    print(f"[academic/upload] Nhận file: {file.filename}")
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .csv hoặc .xlsx")
    
    try:
        import pandas as pd
        import io
        
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
        # Chuẩn hóa tên cột để dễ tìm kiếm (viết thường, bỏ khoảng trắng dư thừa)
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Tìm cột chứa MSSV và GPA hoặc Điểm TB
        mssv_col = next((col for col in df.columns if "mssv" in col or "mã sinh viên" in col or "student_id" in col), None)
        gpa_col = next((col for col in df.columns if "gpa" in col or "điểm trung bình" in col or "điểm tb" in col), None)
        
        if not mssv_col or not gpa_col:
            raise HTTPException(status_code=400, detail="File phải chứa cột Mã sinh viên (MSSV) và Điểm trung bình (GPA)")
            
        updated_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            mssv = str(row[mssv_col]).strip()
            
            # Xử lý gpa (bỏ qua nếu gpa bị rỗng hoặc không phải số)
            try:
                gpa = float(row[gpa_col])
            except (ValueError, TypeError):
                skipped_count += 1
                continue
                
            if not mssv or pd.isna(gpa) or mssv == "nan":
                skipped_count += 1
                continue
                
            # Kiểm tra xem sinh viên có tồn tại trong hệ thống (role = student)
            user = db_handler.queryOne("Users", "student_id", mssv)
            
            if user and user.get("role") == "student":
                # Lấy class_id từ form truyền lên, nếu không có thì lấy từ database
                target_class_id = class_id if class_id else user.get("class_id", "")
                
                # Dữ liệu cập nhật
                data = {
                    "student_id": mssv,
                    "class_id": target_class_id,
                    "gpa": gpa,
                    # Tương lai có thể map thêm môn học từ file vào mảng subjects
                }
                
                success = academic_service.inputGrade(data)
                if success:
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # Không tìm thấy sinh viên trong hệ thống
                skipped_count += 1
                
        return {
            "success": True,
            "message": f"Đã xử lý file {file.filename}. Cập nhật thành công {updated_count} sinh viên, bỏ qua {skipped_count} dòng.",
            "updated_count": updated_count,
            "skipped_count": skipped_count
        }
        
    except ImportError:
        print("[academic/upload] Thiếu thư viện pandas hoặc openpyxl")
        raise HTTPException(status_code=500, detail="Hệ thống thiếu thư viện xử lý Excel. Vui lòng cài đặt pandas và openpyxl.")
    except Exception as e:
        print(f"[academic/upload] Lỗi xử lý file: {e}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi đọc và xử lý file: {str(e)}")