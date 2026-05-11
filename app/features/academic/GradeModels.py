from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class SubjectGrade:
    """
    SubjectGrade (Thông tin điểm của từng môn học)
    """

    subjectName: str
    score: float

    def toDict(self) -> Dict[str, Any]:
        """
        Chuyển object thành dictionary để lưu Firestore.
        """
        return {
            "subject_name": self.subjectName,
            "score": self.score
        }


@dataclass
class AcademicRecord:
    """
    AcademicRecord (Hồ sơ học vụ sinh viên)
    """

    studentId: str
    classId: str
    subjects: List[SubjectGrade] = field(default_factory=list)
    gpa: float = 0.0

    # Các trạng thái phục vụ Observer logic
    isLowScore: bool = False
    aiCheckSent: bool = False
    studentResponded: bool = False

    def toDict(self) -> Dict[str, Any]:
        """
        Convert model sang dictionary để lưu Firestore.
        """

        return {
            "student_id": self.studentId,
            "class_id": self.classId,
            "subjects": [subject.toDict() for subject in self.subjects],
            "gpa": self.gpa,
            "is_low_score": self.isLowScore,
            "ai_check_sent": self.aiCheckSent,
            "student_responded": self.studentResponded
        }