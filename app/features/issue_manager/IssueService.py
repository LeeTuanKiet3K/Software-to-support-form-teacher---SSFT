# /app/features/issue_manager/IssueService.py
import logging
from typing import Dict, Any
from app.features.issue_manager.PriorityLogic import PriorityLogic

class IssueService:
    def __init__(self, dbClient: Any):
        self.m_dbClient = dbClient
        self.m_priorityLogic = PriorityLogic()

    def processStudentIssue(self, studentId: str, classId: str, content: str) -> Dict[str, Any]:
        try: 
            # Phân loại độ ưu tiên của vấn đề
            priority, category, isFallback = self.m_priorityLogic.determinePriority(content)
            
            if priority == "INVALID":
                # AI từ chối phục vụ nếu là Spam
                return {
                    "status": "rejected", 
                    "message": "Chào bạn, hệ thống nhận thấy thông điệp của bạn mang tính đùa cợt. Vui lòng sử dụng kênh hỗ trợ đúng mục đích. Việc lạm dụng có thể ảnh hưởng đến điểm rèn luyện."
                }

            # Khởi tạo dữ liệu bám sát Firestore Schema
            issueData = {
                "student_id": studentId,
                "class_id": classId,
                "content": content,
                "category": category,
                "priority": priority,
                "status": "pending",
                "is_ai_handled": not isFallback,
                "is_fallback": isFallback,
                "assigned_to": "" 
            }
            
            # self.m_dbClient.saveDocument("Issues", issueData)
            
            return {"status": "success", "data": issueData}

        except Exception as e:
            # Bắt lỗi toàn cục và ghi log chi tiết
            logging.error(f"Lỗi hệ thống khi xử lý vấn đề của {studentId}: {str(e)}")
            return {"status": "error", "message": "Hệ thống đang gặp sự cố khi xử lý vấn đề."}