import os
import threading
from typing import Callable, List, Dict, Any, Tuple, Optional
from firebase_admin import credentials, firestore
import firebase_admin
from app.core.Config import AppConfig

class RealtimeHandler:
    """
    Lớp quản lý lắng nghe dữ liệu theo thời gian thực (Real-time Listeners) trên Firestore.
    """

    def __init__(self) -> None:
        self.m_serviceAccountPath = AppConfig.FIREBASE_SERVICE_ACCOUNT_JSON
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.m_serviceAccountPath)
            firebase_admin.initialize_app(cred)
            
        self.m_dbClient = firestore.client()
        self.m_activeListeners = {}


    def listenCollection(self, listenerId: str, collectionName: str, filters: List[Tuple[str, str, Any]], callback: Callable[[List[Dict[str, Any]]], None]) -> bool:
        """
        Cắm một Listener để theo dõi sự thay đổi của Collection.
        """
        query = self.m_dbClient.collection(collectionName)

        for field, operator, value in filters:
            query = query.where(filter=firestore.FieldFilter(field, operator, value))

        def onSnapshot(colSnapshot, changes, readTime):
            dataList = []
            for doc in colSnapshot:
                docData = doc.to_dict()
                if docData is not None:
                    docData['id'] = doc.id
                    dataList.append(docData)
            
            callback(dataList)

        try:
            listener = query.on_snapshot(onSnapshot)
            self.m_activeListeners[listenerId] = listener
            return True
        except Exception as e:
            print(f"Failed to listen to collection: {e}")
            return False
        

    def stopListener(self, listenerId: str) -> bool:
        """
        Hủy bỏ việc theo dõi một nhiệm vụ cụ thể để tiết kiệm tiền.
        """

        if listenerId in self.m_activeListeners:
            listener = self.m_activeListeners[listenerId]
            
            listener.unsubscribe()
            
            del self.m_activeListeners[listenerId]
            return True
        return False
            
    def stopAllListeners(self) -> None:
        """
        Dừng toàn bộ các tiến trình lắng nghe đang chạy (Dùng khi Đăng xuất).
        """
        for listenerId in list(self.m_activeListeners.keys()):
            self.stopListener(listenerId)