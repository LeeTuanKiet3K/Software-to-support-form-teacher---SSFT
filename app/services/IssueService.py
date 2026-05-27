from typing import Dict, Any, List

from firebase_admin import firestore

from app.core.Constants import IssuePriority, IssueStatus
from app.services.FirestoreHandler import FirestoreHandler

class IssueService:
    """
    Dịch vụ quản lý các hệ thống phiếu ghi vấn đề (Issue Ticket System).
    Hỗ trợ Giáo viên chủ nhiệm theo dõi, phân loại và can thiệp kịp thời vào các tình huống khẩn cấp.
    """

    def __init__(self) -> None:
        """
        Liên kết Database Injection (Data Access Layer).
        """
        self.m_dbHandler = FirestoreHandler()

    def createIssueFromChat(self, chatId: str, studentId: str, analysis: Dict[str, Any]) -> str:
        """
        Tự động thiết lập phiếu cảnh báo (Issue Ticket) nếu mô hình Llama phát hiện 
        độ nguy hiểm trong tín hiệu (Urgency Detection).
        
        Args:
            chatId (str): ID phiên trò chuyện.
            studentId (str): ID sinh viên gặp khó khăn.
            analysis (Dict): Kết quả trả về từ hàm callLocalLlama của Middleware (chứa intent và sentiment).
            
        Returns:
            str: Mã phiếu ghi (Ticket ID), trả về chuỗi rỗng nếu cấp độ quá thấp.
        """
        intent = analysis.get("intent", "khong_ro")
        sentiment = analysis.get("sentiment", "trung_lap")
        
        # Thuật toán nội bộ định đoạt mức độ khẩn cấp tự động (Urgency Logic Tree)
        issuePriority = IssuePriority.LOW
        
        # Phân loại độ sâu tiêu cực (Critical Assessment)
        if sentiment == "tieu_cuc":
            if intent == "tam_ly":
                issuePriority = IssuePriority.URGENT        # Khẩn cấp mức cao nhất, cần tương tác ngay
            elif intent == "khieu_nai":
                issuePriority = IssuePriority.HIGH          # Đụng chạm hệ thống, chờ giải quyết
            else:
                issuePriority = IssuePriority.MEDIUM
        elif sentiment == "trung_lap" and intent in ["khieu_nai", "tam_ly"]:
            issuePriority = IssuePriority.MEDIUM
            
        # Không tạo Ticket rác cho các cuộc hội thoại thông thường để tối ưu hóa Dashboard (DB Optimization)
        if issuePriority == IssuePriority.LOW and intent not in ["khieu_nai", "tam_ly"]:
            return ""

        # Lấy thông tin lớp học của sinh viên
        studentProfile = self.m_dbHandler.getUserProfile(studentId)
        studentClassId = studentProfile.get("class_id", "") if studentProfile else ""

        # Thiết lập Schema dữ liệu ánh xạ lên Cloud (Cloud Data Schema)
        issueData = {
            "chat_id": chatId,
            "student_id": studentId,
            "class_id": studentClassId,
            "intent": intent,
            "sentiment": sentiment,
            "priority": issuePriority,
            "status": IssueStatus.OPEN,  # Đưa vào hàng chờ Xử lý của GVCN (Pending Status)
            "is_advisor_viewed": False,   # Metric theo dõi trạng thái chưa đọc
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        try:
            # Ghi nhận vào Collection "Issues" theo đúng cấu trúc
            ticketId = self.m_dbHandler.saveDocument("Issues", issueData)
            return ticketId
        except Exception as systemErr:
            print(f"Hỏng tiến trình thiết lập phiếu (Ticket Initialization Failure): {systemErr}")
            return ""

    def createIssueFromForm(self, studentId: str, title: str, category: str, priority: str, content: str) -> str:
        """
        Khởi tạo phiếu ghi vấn đề do sinh viên chủ động nộp từ Biểu mẫu.
        
        Args:
            studentId (str): ID sinh viên nộp.
            title (str): Tiêu đề vấn đề.
            category (str): Phân loại (Học tập, Tâm lý, ...).
            priority (str): Mức độ ưu tiên do sinh viên hoặc hệ thống đánh giá.
            content (str): Nội dung chi tiết.
            
        Returns:
            str: Mã phiếu ghi (Ticket ID).
        """
        studentProfile = self.m_dbHandler.getUserProfile(studentId)
        studentClassId = studentProfile.get("class_id", "") if studentProfile else ""

        issueData = {
            "chat_id": "", # Biểu mẫu không gắn với phiên chat
            "student_id": studentId,
            "class_id": studentClassId,
            "title": title,
            "category": category,
            "intent": category,  # Lưu tạm vào intent để tương thích với hệ thống cũ
            "sentiment": "chủ động nộp", # Đánh dấu nguồn gốc
            "content": content,
            "priority": priority,
            "status": IssueStatus.OPEN,
            "is_advisor_viewed": False,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        try:
            ticketId = self.m_dbHandler.saveDocument("Issues", issueData)
            return ticketId
        except Exception as e:
            print(f"Lỗi khi gửi biểu mẫu (Form Submission Error): {e}")
            return ""

    def getPendingIssues(self, advisorClassId: str = "") -> List[Dict[str, Any]]:
        """
        Truy xuất danh mục báo động cần xử lý (Fetch Pending Pipelines) để 
        hiển thị cho Bảng điều khiển (Advisor Dashboard). Lọc theo lớp học nếu được cung cấp.
        
        Args:
            advisorClassId (str, optional): Lớp mà GVCN phụ trách để lọc issue.

        Returns:
            List[Dict]: Các phiếu còn trống hoặc đang trong vòng lặp làm việc, tự động sắp xếp theo độ ưu tiên.
        """
        pendingIssuesList = []
        try:
            # Tạo tham chiếu truy vấn Database (Ref builder)
            issuesRef = self.m_dbHandler.m_dbClient.collection("Issues")
            
            # Kết hợp truy vấn hai Status đặc thù OPEN và IN_PROGRESS
            openQuery = issuesRef.where(filter=firestore.FieldFilter('status', '==', IssueStatus.OPEN)).stream()
            inProgQuery = issuesRef.where(filter=firestore.FieldFilter('status', '==', IssueStatus.IN_PROGRESS)).stream()
            
            # Xử lý đóng gói Pipeline Object (Pipeline Mapping)
            for doc in openQuery:
                data = doc.to_dict()
                if advisorClassId and data.get("class_id") != advisorClassId:
                    continue
                data['issue_id'] = doc.id
                pendingIssuesList.append(data)
                
            for doc in inProgQuery:
                data = doc.to_dict()
                if advisorClassId and data.get("class_id") != advisorClassId:
                    continue
                data['issue_id'] = doc.id
                pendingIssuesList.append(data)
                
            # Trọng số sắp xếp ưu tiên hiển thị (Dashboard Priority Sorting Logic)
            # Hệ số càng nhỏ, báo động chìm càng bị ép lên đỉnh danh sách
            priorityWeightings = {
                IssuePriority.URGENT: 0,
                IssuePriority.HIGH: 1,
                IssuePriority.MEDIUM: 2,
                IssuePriority.LOW: 3
            }
            
            pendingIssuesList.sort(key=lambda item: priorityWeightings.get(item.get("priority"), 99))
            
            return pendingIssuesList
            
        except Exception as e:
            print(f"Lỗi truy xuất trạng thái kẹt lại (Fetch Pipeline Exception): {e}")
            return []

    def updateIssueStatus(self, issueId: str, newStatus: str) -> bool:
        """
        Hoán đổi tiến độ xử lý của phiếu tác vụ (Ticket Status Updater).
        Được gọi trực tiếp khi GVCN đã can thiệp trong Dashboard.
        
        Args:
            issueId (str): ID duy nhất xác định thẻ ghi nhận.
            newStatus (str): Mã chuyển tiếp nằm trong `Constants.IssueStatus` (vd: RESOLVED).
            
        Returns:
            bool: Tín hiệu báo hoàn thành luồng dữ liệu (Data sync complete).
        """
        try:
            updateMetadata = {
                "status": newStatus,
                "is_advisor_viewed": True, # Cờ báo đã đọc
                "updated_at": firestore.SERVER_TIMESTAMP
            }
            # Gọi API hạ tầng kế thừa từ Bước 1
            isSuccess = self.m_dbHandler.updateDocument("Issues", issueId, updateMetadata)
            return isSuccess
        except Exception as dbError:
            print(f"Sự cố hệ thống cập nhật (DB Status Update Crash): {dbError}")
            return False
