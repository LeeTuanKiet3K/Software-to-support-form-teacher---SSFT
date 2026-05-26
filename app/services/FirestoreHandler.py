import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.Config import AppConfig

class FirestoreHandler:
    """
    Lớp xử lý kết nối và thao tác với Firestore (Firestore Handler Layer).
    Được thiết kế để SearchEngine và ContextManager có thể kế thừa và gọi trơn tru.
    """

    def __init__(self) -> None:
        """
        Khởi tạo dịch vụ (Initialize services) Firestore.
        """
        self.m_serviceAccountPath = AppConfig.FIREBASE_SERVICE_ACCOUNT_JSON
        
        if not self.m_serviceAccountPath:
            raise ValueError("Lỗi: FIREBASE_SERVICE_ACCOUNT_JSON không được tìm thấy trong cấu hình.")
        
        # Chỉ khởi tạo app nếu chưa tồn tại (Prevent multiple app initializations)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.m_serviceAccountPath)
            firebase_admin.initialize_app(cred)
        
        self.m_dbClient = firestore.client()
        # Alias tương thích cho code cũ dùng `m_db`.
        self.m_db = self.m_dbClient

    def saveDocument(self, collectionName: str, data: Dict[str, Any], documentId: Optional[str] = None) -> str:
        """
        Lưu dữ liệu vào Firestore (Save document to Firestore).
        Tích hợp log vào AI_logs nếu có thao tác liên quan đến AI.
        
        Args:
            collectionName (str): Tên collection.
            data (Dict): Dữ liệu cần lưu.
            documentId (Optional[str]): ID tài liệu (nếu không truyền sẽ tự tạo ID).
            
        Returns:
            str: ID của document đã được lưu.
        """
        current_time = datetime.now(timezone.utc)
        if "created_at" not in data:
            data["created_at"] = current_time
        data["updated_at"] = current_time
        collectionRef = self.m_dbClient.collection(collectionName)
        
        if documentId:
            collectionRef.document(documentId).set(data)
            savedId = documentId
        else:
            _, docRef = collectionRef.add(data)
            savedId = docRef.id

        # Kiểm tra nếu là các thao tác liên quan đến AI để ghi log
        m_aiEventTriggers = ["AI_logs", "common_data", "responses", "issues", "knowledge_base", "ai_responses", "chats"]
        if collectionName in m_aiEventTriggers:
            self.m_logAiAction("save_document", collectionName, savedId)

        return savedId

    def getDocument(
        self,
        collectionName: Optional[str] = None,
        documentId: Optional[str] = None,
        **kwargs: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Lấy dữ liệu từ Firestore (Retrieve document from Firestore).
        
        Args:
            collectionName (str): Tên collection.
            documentId (str): ID của tài liệu.  
            
        Returns:
            Optional[Dict]: Nội dung tài liệu hoặc None nếu không tồn tại.
        """
        # Hỗ trợ cả chữ ký cũ: getDocument(collection=..., docId=...)
        if collectionName is None:
            collectionName = kwargs.get("collection")
        if documentId is None:
            documentId = kwargs.get("docId")

        if not collectionName or not documentId:
            return None

        docRef = self.m_dbClient.collection(collectionName).document(documentId)
        doc = docRef.get()
        
        if doc.exists:
            docData = doc.to_dict()
            if docData:
                docData['id'] = doc.id
            # Ghi log nếu truy xuất thông tin từ AI (Log AI data retrieval)
            if collectionName in ["knowledge_base", "ai_responses", "common_data", "AI_logs"]:
                self.m_logAiAction("get_document", collectionName, documentId)
            return docData
        return None

    def updateDocument(self, collectionName: str, documentId: str, data: Dict[str, Any]) -> bool:
        """
        Cập nhật dữ liệu vào Firestore (Update existing document).
        
        Args:
            collectionName (str): Tên collection.
            documentId (str): ID của tài liệu.
            data (Dict): Dữ liệu cần cập nhật.
            
        Returns:
            bool: True nếu cập nhật thành công, False nếu thất bại.
        """
        docRef = self.m_dbClient.collection(collectionName).document(documentId)
        try:
            docRef.update(data)
            # Log AI manipulation
            if collectionName in ["ai_responses", "chats", "common_data", "AI_logs"]:
                self.m_logAiAction("update_document", collectionName, documentId)
            return True
        except Exception as e:
            print(f"Failed to update document: {e}")
            return False

    def deleteDocument(self, collectionName: str, documentId: str) -> bool:
        """
        Xóa một document khỏi Firestore (Delete document).
        
        Args:
            collectionName (str): Tên collection.
            documentId (str): ID của tài liệu cần xóa.
            
        Returns:
            bool: True nếu xóa thành công, False nếu thất bại.
        """
        docRef = self.m_dbClient.collection(collectionName).document(documentId)
        try:
            docRef.delete()
            # Ghi log nếu thao tác liên quan đến AI
            if collectionName in ["ai_responses", "chats", "common_data", "AI_logs"]:
                self.m_logAiAction("delete_document", collectionName, documentId)
            return True
        except Exception as e:
            print(f"Failed to delete document: {e}")
            return False

    def m_logAiAction(self, action: str, targetCollection: str, targetId: str) -> None:
        """
        Hàm nội bộ (Private function) để ghi nhận nhật ký thao tác liên quan đến AI.
        
        Args:
            action (str): Hành động (vd: save, get, update).
            targetCollection (str): Tên collection bị tác động.
            targetId (str): Document ID bị tác động.
        """
        logData = {
            "action": action,
            "target_collection": targetCollection,
            "target_id": targetId,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        try:
            self.m_dbClient.collection("AI_logs").add(logData)
        except Exception as e:
            print(f"Failed to write AI log: {e}")

    def queryDocuments(self, collectionName: str, filters: List[Tuple[str, str, Any]], limitCount: int = 100) -> List[Dict[str, Any]]:
        query = self.m_dbClient.collection(collectionName)

        for field, operator, value in filters:
            query = query.where(filter=firestore.FieldFilter(field, operator, value))

        query = query.limit(limitCount)

        resultList = []
        try:
            docs = query.stream()
            for doc in docs:
                docData = doc.to_dict()
                if docData is not None:
                    docData['id'] = doc.id
                    resultList.append(docData)
        except Exception as e:
            print(f"Fail to query documents: {e}")
            
        return resultList

    def addDocument(self, collection: str, data: Dict[str, Any]) -> str:
        """
        Alias tương thích ngược cho saveDocument.
        """
        return self.saveDocument(collectionName=collection, data=data)

    def queryOne(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        Truy vấn một document đầu tiên theo điều kiện bằng nhau.
        """
        result = self.queryDocuments(
            collectionName=collection,
            filters=[(field, "==", value)],
            limitCount=1,
        )
        return result[0] if result else None

    def getUserProfile(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Lấy hồ sơ người dùng theo UID từ collection Users.
        """
        return self.getDocument(collectionName="Users", documentId=uid)

    def createUserProfile(self, uid: str, profileData: Dict[str, Any]) -> bool:
        """
        Tạo hồ sơ người dùng theo UID vào collection Users.
        """
        try:
            self.saveDocument(collectionName="Users", data=profileData, documentId=uid)
            return True
        except Exception as error:
            print(f"Failed to create user profile: {error}")
            return False
