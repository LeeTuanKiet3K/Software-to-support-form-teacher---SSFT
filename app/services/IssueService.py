from typing import Dict, Any, List

from firebase_admin import firestore

from app.core.Constants import IssuePriority, IssueStatus
from app.services.FirestoreHandler import FirestoreHandler

class IssueService:
    """
    Dịch vụ quản lý các hệ thống phiếu ghi vấn đề (Issue Ticket System).
    Hỗ trợ Giáo viên chủ nhiệm theo dõi, phân loại và can thiệp kịp thời vào các tình huống khẩn cấp.
    """
    # Liên kết Database Injection (Data Access Layer).
    def __init__(self) -> None:
        self.m_dbHandler = FirestoreHandler()

    # Tự động thiết lập phiếu cảnh báo (Issue Ticket)
    def createIssueFromChat(self, chatId: str, studentId: str, analysis: Dict[str, Any]) -> str:
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
            "unread_by_advisor": 0,
            "unread_by_student": 0,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        try:
            # Ghi nhận vào Collection "Issues" theo đúng cấu trúc
            ticketId = self.m_dbHandler.saveDocument("Issues", issueData)
            return ticketId
        except Exception as systemErr:
            print(f"Hỏng tiến trình thiết lập phiếu (Ticket Initialization Failure): {systemErr}")
            return ""

    # Khởi tạo phiếu ghi vấn đề do sinh viên chủ động nộp từ Biểu mẫu.
    def createIssueFromForm(self, studentId: str, title: str, category: str, priority: str, content: str) -> str:
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
            "unread_by_advisor": 0,
            "unread_by_student": 0,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        try:
            ticketId = self.m_dbHandler.saveDocument("Issues", issueData)
            return ticketId
        except Exception as e:
            print(f"Lỗi khi gửi biểu mẫu (Form Submission Error): {e}")
            return ""

    # Truy xuất danh mục báo động cần xử lý (Fetch Pending Pipelines) để hiển thị cho Bảng điều khiển (Advisor Dashboard).
    def getPendingIssues(self, advisorClassId: str = "") -> List[Dict[str, Any]]:
        pendingIssuesList = []
        try:
            # Tạo tham chiếu truy vấn Database (Ref builder)
            issuesRef = self.m_dbHandler.m_db.collection("Issues")
            
            # Kết hợp truy vấn hai Status đặc thù OPEN và IN_PROGRESS
            openQuery = issuesRef.where(filter=firestore.FieldFilter('status', '==', IssueStatus.OPEN)).stream()
            inProgQuery = issuesRef.where(filter=firestore.FieldFilter('status', '==', IssueStatus.IN_PROGRESS)).stream()
            
            # Xử lý đóng gói Pipeline Object (Pipeline Mapping)
            for doc in openQuery:
                data = doc.to_dict()
                issue_class = data.get("class_id", "")
                if advisorClassId and issue_class != advisorClassId:
                    continue
                data['issue_id'] = doc.id
                pendingIssuesList.append(data)
                
            for doc in inProgQuery:
                data = doc.to_dict()
                issue_class = data.get("class_id", "")
                if advisorClassId and issue_class != advisorClassId:
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

    # Truy xuất các phiếu vấn đề của một sinh viên.
    def getStudentIssues(self, studentId: str) -> List[Dict[str, Any]]:
        studentIssuesList = []
        try:
            issuesRef = self.m_dbHandler.m_db.collection("Issues")
            query = issuesRef.where(filter=firestore.FieldFilter('student_id', '==', studentId)).stream()
            
            for doc in query:
                data = doc.to_dict()
                data['issue_id'] = doc.id
                studentIssuesList.append(data)
                
            # Sắp xếp mới nhất lên đầu
            studentIssuesList.sort(key=lambda item: item.get("created_at", ""), reverse=True)
            return studentIssuesList
        except Exception as e:
            print(f"Lỗi truy xuất phiếu sinh viên: {e}")
            return []
    
    # Hỗ trợ tính toán thống kê và biểu đồ cho Bảng điều khiển (Advisor Dashboard).
    def getAllIssues(self, advisorClassId: str = "") -> List[Dict[str, Any]]:
        allIssuesList = []
        try:
            issuesRef = self.m_dbHandler.m_db.collection("Issues")
            
            # Tải toàn bộ dữ liệu, lọc theo class_id ở Application Level (tiết kiệm Index)
            # hoặc tạo FieldFilter trực tiếp nếu cần tối ưu
            if advisorClassId:
                query = issuesRef.where(filter=firestore.FieldFilter('class_id', '==', advisorClassId)).stream()
            else:
                query = issuesRef.stream()
                
            for doc in query:
                data = doc.to_dict()
                data['issue_id'] = doc.id
                allIssuesList.append(data)
                
            return allIssuesList
            
        except Exception as e:
            print(f"Lỗi truy xuất toàn bộ phiếu: {e}")
            return []

    # Hoán đổi tiến độ xử lý của phiếu tác vụ (Ticket Status Updater).
    def updateIssueStatus(self, issueId: str, newStatus: str) -> bool:
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

    # Thêm tin nhắn trao đổi vào Phiếu vấn đề.
    def addMessageToIssue(self, issueId: str, senderId: str, senderRole: str, content: str) -> Dict[str, Any]:
        messageData = {
            "issue_id": issueId,
            "sender_id": senderId,
            "sender_role": senderRole,  # 'STUDENT' or 'ADVISOR'
            "content": content,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        try:
            # 1. Lưu tin nhắn vào IssueMessages
            msgId = self.m_dbHandler.saveDocument("IssueMessages", messageData)
            messageData["message_id"] = msgId
            
            # 2. Cập nhật số lượng tin chưa đọc và đổi status nếu GVCN reply
            issueData = self.m_dbHandler.getDocument("Issues", issueId)
            if issueData:
                updates = {"updated_at": firestore.SERVER_TIMESTAMP}
                if senderRole == "STUDENT":
                    updates["unread_by_advisor"] = issueData.get("unread_by_advisor", 0) + 1
                else:
                    updates["unread_by_student"] = issueData.get("unread_by_student", 0) + 1
                    # Đổi trạng thái nếu GVCN trả lời
                    if issueData.get("status") == IssueStatus.OPEN:
                        updates["status"] = IssueStatus.IN_PROGRESS

                self.m_dbHandler.updateDocument("Issues", issueId, updates)

            return messageData
        except Exception as e:
            print(f"Lỗi thêm tin nhắn vào issue (Add msg error): {e}")
            return {}

    # Lấy lịch sử trò chuyện của một phiếu.
    def getIssueMessages(self, issueId: str) -> List[Dict[str, Any]]:
        try:
            query = self.m_dbHandler.m_db.collection("IssueMessages")\
                .where(filter=firestore.FieldFilter('issue_id', '==', issueId))\
                .limit(100)
            
            result = []
            for doc in query.stream():
                data = doc.to_dict()
                data["message_id"] = doc.id
                result.append(data)
                
            # Sort in memory to avoid Firestore composite index requirement
            result.sort(key=lambda x: x.get("created_at") or 0)
            return result
        except Exception as e:
            print(f"Lỗi lấy lịch sử tin nhắn: {e}")
            return []

    # Đánh dấu là đã đọc (reset unread_count).
    def markIssueAsRead(self, issueId: str, readerRole: str) -> bool:
        try:
            updates = {}
            if readerRole == "STUDENT":
                updates["unread_by_student"] = 0
            elif readerRole == "ADVISOR":
                updates["unread_by_advisor"] = 0
                updates["is_advisor_viewed"] = True

            if updates:
                return self.m_dbHandler.updateDocument("Issues", issueId, updates)
            return False
        except Exception as e:
            print(f"Lỗi đánh dấu đã đọc (Mark read error): {e}")
            return False

