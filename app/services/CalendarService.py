import datetime
from typing import Optional
from app.services.FirestoreHandler import FirestoreHandler

class CalendarService:
    """Service xử lý dữ liệu cho tính năng Lịch trình."""
    
    def __init__(self):
        self.db = FirestoreHandler()
        self.collection_name = "Calendar_events"

    def get_all_events(self):
        """Lấy tất cả các sự kiện lịch."""
        try:
            return self.db.queryDocuments(self.collection_name, filters=[])
        except Exception as e:
            print(f"[CalendarService] Lỗi khi lấy danh sách sự kiện: {e}")
            return []
            
    def create_event(self, title: str, date: str, time: str, location: str, event_type: str, user_id: str) -> Optional[str]:
        """Tạo một sự kiện mới trên Firestore."""
        event_data = {
            "title": title,
            "date": date,
            "time": time,
            "location": location,
            "type": event_type,
            "user_id": user_id,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        try:
            event_id = self.db.saveDocument(self.collection_name, event_data)
            return event_id
        except Exception as e:
            print(f"[CalendarService] Lỗi khi tạo sự kiện: {e}")
            return None

    def delete_event(self, event_id: str) -> bool:
        """Xóa một sự kiện khỏi Firestore."""
        try:
            return self.db.deleteDocument(self.collection_name, event_id)
        except Exception as e:
            print(f"[CalendarService] Lỗi khi xóa sự kiện: {e}")
            return False
