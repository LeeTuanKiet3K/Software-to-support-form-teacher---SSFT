import os
import sys
from typing import List

# Đảm bảo có thể import được các module từ thư mục app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.FirestoreHandler import FirestoreHandler

class CommonDataUpdater:
    """
    Công cụ quản lý và cập nhật kho tri thức (Common_data) cho hệ thống AI.
    Phiên bản sử dụng Keyword Search truyền thống.
    """
    def __init__(self):
        self.m_dbHandler = FirestoreHandler()
        self.m_collectionName = "Common_data"

    def addSingleDocument(self, documentId: str, sourceUrl: str, keywordsList: List[str], textContent: str) -> bool:
        """
        Thêm hoặc cập nhật một tài liệu đơn lẻ vào kho tri thức.
        """
        # Khởi tạo ID tự động một cách an toàn thông qua hàm bảo mật của Handler
        if not documentId:
            documentId = self.m_dbHandler.generateDocumentId(self.m_collectionName)
            print(f"   => Firestore đã cấp ID tự động: {documentId}")

        # Chuẩn hóa keywords về chữ thường (lowercase) để Firestore dễ tìm kiếm
        cleanKeywords = [k.lower() for k in keywordsList]

        dataPayload = {
            "doc_id": documentId,
            "source": sourceUrl,
            "keywords": cleanKeywords,
            "content": textContent
        }
        
        try:
            savedId = self.m_dbHandler.saveDocument(
                collectionName=self.m_collectionName, 
                data=dataPayload, 
                documentId=documentId
            )
            print(f"Đã lưu thành công lên Firestore với ID: {savedId}\n")
            return True
        except Exception as e:
            print(f"Error saving document {documentId}: {e}\n")
            return False

def interactiveUpload():
    """Hàm tương tác qua Terminal giúp nhập liệu liên tục."""
    updater = CommonDataUpdater()
    print("="*60)
    print("CÔNG CỤ NHẬP LIỆU TRI THỨC (COMMON DATA) CHO AI")
    print("Mẹo: Nhập 'quit' ở bất kỳ bước nào để thoát chương trình.")
    print("="*60)
    
    uploadCount = 0
    while True:
        print(f"\n--- Đang nhập tài liệu thứ {uploadCount + 1} ---")
        
        docId = input("1. Nhập doc_id (Nhấn Enter để hệ thống TỰ ĐỘNG TẠO): ").strip()
        if docId.lower() == 'quit': break
            
        sourceLink = input("2. Nhập URL nguồn tham khảo (Nhấn Enter để bỏ qua): ").strip()
        if sourceLink.lower() == 'quit': break
        if not sourceLink: sourceLink = "N/A"
        
        rawKeywords = input("3. Nhập từ khóa, cách nhau bằng dấu phẩy: ").strip()
        if rawKeywords.lower() == 'quit': break
        
        keywordArray = [k.strip() for k in rawKeywords.split(",") if k.strip()]
            
        mainContent = input("4. Nhập nội dung tri thức: ").strip()
        if mainContent.lower() == 'quit': break
        if not mainContent:
            print("Nội dung không được để trống. Vui lòng nhập lại tài liệu này!")
            continue
        
        print("Đang đẩy dữ liệu lên Firestore...")
        isSuccess = updater.addSingleDocument(docId, sourceLink, keywordArray, mainContent)
        if isSuccess:
            uploadCount += 1
        
        shouldContinue = input("Bạn có muốn thêm tài liệu khác không? (y/n): ").strip().lower()
        if shouldContinue != 'y':
            break
            
    print(f"\nBạn đã thêm thành công {uploadCount} tài liệu vào hệ thống.")

if __name__ == "__main__":
    interactiveUpload()