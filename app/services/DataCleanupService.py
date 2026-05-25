import asyncio
import time
from datetime import datetime, timedelta, timezone
from app.services.FirestoreHandler import FirestoreHandler

class DataCleanupService:
    """
    Dịch vụ dọn dẹp dữ liệu tự động cho các Collection sinh ra rác (chats, AI_logs).
    """

    def __init__(self) -> None:
        self.m_dbHandler = FirestoreHandler()
        self.m_collections_to_clean = ["chats", "AI_logs"]

    def cleanup_old_documents(self, days_to_keep: int = 30) -> None:
        """
        Tìm và xóa các documents cũ hơn `days_to_keep` ngày.
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        print(f"[{datetime.now().isoformat()}] Bắt đầu dọn dẹp dữ liệu Firebase cũ hơn {days_to_keep} ngày (trước {cutoff_time.isoformat()})...")

        total_deleted = 0
        for collection in self.m_collections_to_clean:
            try:
                # Firestore query for older documents
                # `created_at` field must exist and be indexed for inequality queries
                filters = [("created_at", "<", cutoff_time)]
                old_docs = self.m_dbHandler.queryDocuments(collectionName=collection, filters=filters, limitCount=500)
                
                deleted_in_col = 0
                for doc in old_docs:
                    doc_id = doc.get("id")
                    if doc_id:
                        if self.m_dbHandler.deleteDocument(collection, doc_id):
                            deleted_in_col += 1
                
                print(f" - Collection '{collection}': Đã xóa {deleted_in_col} tài liệu cũ.")
                total_deleted += deleted_in_col
            except Exception as e:
                print(f" - Collection '{collection}': Lỗi trong quá trình dọn dẹp: {e}")

        print(f"[{datetime.now().isoformat()}] Hoàn tất dọn dẹp. Tổng cộng xóa {total_deleted} tài liệu.")


async def start_periodic_cleanup_task(days_to_keep: int = 30, interval_seconds: int = 86400):
    """
    Hàm tiện ích để chạy ngầm tiến trình dọn dẹp định kỳ (Cronjob).
    Mặc định interval = 86400 giây (24 giờ).
    """
    print(f"[*] Tiến trình dọn dẹp dữ liệu định kỳ (mỗi {interval_seconds}s) đã được khởi động.")
    cleanup_service = DataCleanupService()
    
    while True:
        try:
            # Thực thi việc dọn dẹp
            cleanup_service.cleanup_old_documents(days_to_keep)
        except Exception as e:
            print(f"Lỗi không xác định trong tiến trình dọn dẹp: {e}")
        
        # Ngủ cho đến chu kỳ tiếp theo
        await asyncio.sleep(interval_seconds)
