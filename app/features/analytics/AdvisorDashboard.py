import streamlit as st
from typing import List, Dict, Any
from datetime import datetime, timezone

from app.services.FirestoreHandler import FirestoreHandler
from app.features.notifications.NotificationService import NotificationService
from app.core.Constants import IssueStatus


class AdvisorDashboardService:
    """
    Service xử lý logic Backend cho Dashboard của GVCN.
    """
    def __init__(self) -> None:
        self.m_dbHandler = FirestoreHandler()
        self.m_notificationService = NotificationService()

    def getPendingIssues(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách các vấn đề đang chờ GVCN xử lý (PENDING_ADVISOR hoặc OPEN).
        """
        # Lấy tất cả vấn đề và lọc bằng code Python để đảm bảo linh hoạt.
        # Lưu ý: Cần gắn Index trên Firebase nếu query quy mô lớn sau này.
        allIssues = self.m_dbHandler.queryDocuments(
            collectionName="Issues",
            filters=[], 
            limitCount=500
        )
        
        pendingIssues = []
        for issue in allIssues:
            # Lọc các vấn đề chưa được giải quyết
            if issue.get("status") in [IssueStatus.PENDING_ADVISOR, IssueStatus.OPEN, IssueStatus.IN_PROGRESS]:
                pendingIssues.append(issue)
                
        # Sắp xếp để đưa các vấn đề khẩn cấp lên đầu
        priority_weights = {"URGENT": 4, "P0": 4, "HIGH": 3, "P1": 3, "MEDIUM": 2, "P2": 2, "LOW": 1}
        pendingIssues.sort(key=lambda x: priority_weights.get(x.get("priority", "LOW"), 0), reverse=True)
        
        return pendingIssues

    def replyToIssue(self, issueId: str, studentId: str, replyContent: str) -> bool:
        """
        Xử lý khi GVCN gửi phản hồi cho một Issue.
        1. Cập nhật trạng thái thành RESOLVED.
        2. Lưu nội dung phản hồi.
        3. Gửi Notification cho sinh viên.
        """
        if not issueId or not studentId:
            return False

        updateData = {
            "status": IssueStatus.RESOLVED,
            "advisor_reply": replyContent,
            "replied_at": datetime.now(timezone.utc)
        }
        
        success = self.m_dbHandler.updateDocument(
            collectionName="Issues",
            documentId=issueId,
            data=updateData
        )
        
        if success:
            # Đẩy thông báo cho sinh viên
            self.m_notificationService.sendAdvisorReplyNotification(studentId, replyContent)
            return True
            
        return False

    def scheduleMeeting(self, advisorId: str, studentId: str, issueId: str, meetingDate: datetime, notes: str) -> bool:
        """
        Lên lịch hẹn gặp sinh viên.
        """
        appointmentData = {
            "advisor_id": advisorId,
            "student_id": studentId,
            "issue_id": issueId,
            "meeting_date": meetingDate,
            "notes": notes,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc)
        }
        
        try:
            self.m_dbHandler.saveDocument("Appointments", appointmentData)
            
            # Gửi thông báo cho sinh viên (Tùy chọn)
            notificationContent = f"GVCN đã xếp lịch hẹn gặp bạn vào lúc {meetingDate.strftime('%H:%M %d/%m/%Y')}. Ghi chú: {notes}"
            self.m_notificationService.sendAdvisorReplyNotification(studentId, notificationContent)
            return True
        except Exception as e:
            print(f"Lỗi khi lưu lịch hẹn: {e}")
            return False

    def getUpcomingMeetings(self, advisorId: str) -> List[Dict[str, Any]]:
        """
        Lấy danh sách các cuộc hẹn sắp tới của GVCN.
        """
        try:
            # Truy vấn cơ bản: lọc theo advisor_id và status là scheduled.
            # Việc so sánh thời gian sẽ thực hiện ở client/python để tránh cần index phức tạp trên Firebase.
            allAppointments = self.m_dbHandler.queryDocuments(
                collectionName="Appointments",
                filters=[{"field": "advisor_id", "operator": "==", "value": advisorId},
                         {"field": "status", "operator": "==", "value": "scheduled"}],
                limitCount=100
            )
            
            now = datetime.now(timezone.utc)
            upcoming = []
            for appt in allAppointments:
                # Firestore trả về Datetime với timezone
                mtgDate = appt.get("meeting_date")
                if hasattr(mtgDate, "to_datetime"):
                    mtgDate = mtgDate.to_datetime()
                elif isinstance(mtgDate, datetime) and mtgDate.tzinfo is None:
                    mtgDate = mtgDate.replace(tzinfo=timezone.utc)
                
                if isinstance(mtgDate, datetime):
                    # Nếu lịch trình diễn ra trong tương lai hoặc đã qua nhưng chưa hoàn thành (có thể nhắc nhở)
                    # Ở đây ta lấy các cuộc hẹn từ thời điểm hiện tại trở đi
                    if mtgDate >= now:
                        upcoming.append(appt)
                        
            # Sắp xếp theo thời gian sớm nhất
            upcoming.sort(key=lambda x: x.get("meeting_date", now))
            return upcoming
        except Exception as e:
            print(f"Lỗi khi lấy lịch hẹn: {e}")
            return []


def renderAdvisorDashboard() -> None:
    """
    Giao diện (UI) mẫu cho Dashboard của GVCN (Streamlit Component).
    Được import và gọi tại app/main.py.
    """
    st.title("Hộp thư Quản lý Sinh viên")
    st.markdown("---")
    
    dashboardService = AdvisorDashboardService()
    
    with st.spinner("Đang tải dữ liệu vấn đề..."):
        issues = dashboardService.getPendingIssues()
    
    if not issues:
        st.success("Tuyệt vời! Hiện không có vấn đề nào cần xử lý.")
        return
        
    st.markdown(f"**Bạn có {len(issues)} vấn đề đang chờ giải quyết.**")
    
    for issue in issues:
        priority = issue.get("priority", "LOW")
        
        # UI: Màu sắc theo độ khẩn cấp
        color = "🟢"
        if priority in ["URGENT", "P0", "HIGH", "P1"]:
            color = "🔴"
        elif priority in ["MEDIUM", "P2"]:
            color = "🟡"
            
        card_title = f"{color} [{priority}] {issue.get('category', 'Chung')} - SV: {issue.get('student_id', 'Ẩn danh')}"
        
        with st.expander(card_title):
            st.markdown("### Nội dung phản ánh:")
            st.info(issue.get("content", "Không có nội dung chi tiết."))
            
            st.markdown(f"**Trạng thái hiện tại:** `{issue.get('status')}`")
            
            # Khung nhập phản hồi
            reply_text = st.text_area(f"Nhập lời khuyên / phản hồi của bạn:", key=f"reply_{issue.get('id')}", height=100)
            
            if st.button("Gửi Phản Hồi & Đóng", key=f"btn_{issue.get('id')}", type="primary"):
                if not reply_text.strip():
                    st.warning("Vui lòng nhập nội dung trước khi gửi.")
                else:
                    success = dashboardService.replyToIssue(
                        issueId=issue.get('id'),
                        studentId=issue.get('student_id'),
                        replyContent=reply_text
                    )
                    
                    if success:
                        st.success("Đã phản hồi thành công! Sinh viên sẽ nhận được thông báo.")
                        st.rerun()
                    else:
                        st.error("Lỗi hệ thống khi gửi phản hồi. Vui lòng thử lại sau.")
