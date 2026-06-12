import json
import os
import traceback
from typing import List, Dict, Any
from rapidfuzz import fuzz
from app.services.FirestoreHandler import FirestoreHandler

class SearchEngine:
    """
    Công cụ tìm kiếm thông minh (Semantic Search Engine).
    Sử dụng Rapidfuzz cho phép tìm kiếm mờ (Fuzzy matching) hiệu quả khi sinh viên gõ sai chính tả.
    """
    
    # Biến nội bộ phục vụ mô hình thiết kế (Private Singleton Instance)
    m_instance = None
    
    def __new__(cls):
        """
        Khởi tạo đối tượng theo pattern Singleton (Singleton Pattern).
        Đảm bảo dữ liệu KnowledgeBase được nạp (Caching) một lần duy nhất vào RAM.
        """
        if cls.m_instance is None:
            cls.m_instance = super(SearchEngine, cls).__new__(cls)
            # Khởi tạo instance kết nối Firestore (Database injection)
            cls.m_instance.m_dbHandler = FirestoreHandler()
            # Tải tri thức nội bộ (Load knowledge data)
            cls.m_instance.m_knowledgeData = cls.m_instance.m_loadKnowledgeBase()
        return cls.m_instance

    def m_loadKnowledgeBase(self) -> List[Dict[str, Any]]:
        """
        Hàm nội bộ lấy thông tin từ KnowledgeBase.json (Internal File Loader).
        
        Returns:
            List[Dict]: Danh sách các cấu trúc tri thức.
        """
        # Xác định đường dẫn file JSON một cách linh hoạt (Dynamic path resolution)
        currentDir = os.path.dirname(os.path.abspath(__file__))
        projectRoot = os.path.dirname(os.path.dirname(currentDir))
        kbPath = os.path.join(projectRoot, "data", "KnowledgeBase.json")
        
        try:
            if os.path.exists(kbPath):
                with open(kbPath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Hỗ trợ cả trường hợp cấu trúc lấy là mảng hoặc nằm trong object "data"
                    return data if isinstance(data, list) else data.get("data", [])
            else:
                self.m_logError("m_loadKnowledgeBase", f"Không tìm thấy file (File not found): {kbPath}")
                return []
        except Exception as e:
            self.m_logError("m_loadKnowledgeBase", f"Lỗi tải file JSON (JSON parse error): {str(e)}")
            return []

    def findRelevantContext(self, query: str, topN: int = 3) -> List[Dict[str, Any]]:
        """
        Tìm kiếm ngữ cảnh tương đồng nhất từ KnowledgeBase (Context Retrieval).
        Sẽ cung cấp kiến thức nền (Grounding input) cho Groq.
        
        Args:
            query (str): Xâu truy vấn hoặc câu hỏi của sinh viên.
            topN (int): Số lượng ngữ cảnh (Context instances) tối đa cần trả về.
            
        Returns:
            List[Dict]: Các kết quả khớp nhất được sắp xếp theo độ tương đồng.
        """
        if not self.m_knowledgeData or not query:
            return []
            
        try:
            results = []
            normalizedQuery = query.lower()
            
            for item in self.m_knowledgeData:
                # Trích xuất content và định dạng (Extract and normalize)
                keywordsRaw = item.get("keywords", [])
                keywordsStr = " ".join(keywordsRaw) if isinstance(keywordsRaw, list) else str(keywordsRaw)
                contentStr = str(item.get("content", ""))
                
                # Nối khối văn bản so sánh (Target block)
                searchTarget = f"{keywordsStr} {contentStr}".lower()
                
                # Tính điểm độ giống nhau từng phần (Fuzzy Score)
                score = fuzz.token_set_ratio(normalizedQuery, searchTarget)
                results.append((score, item))
                
            # Sắp xếp số điểm từ cao xuống thấp (Sort descending)
            results.sort(key=lambda x: x[0], reverse=True)
            
            # Lọc các kết quả có điểm đủ cao (với token_set_ratio, trung bình >50 là khả thi)
            threshold = 40
            topResults = [item for score, item in results[:topN] if score >= threshold]
            
            return topResults
            
        except Exception as e:
            self.m_logError("findRelevantContext", str(e))
            return []

    def searchCommonData(self, query: str) -> List[Dict[str, Any]]:
        """
        Nạp dữ liệu từ xa (Remote fetching) qua bảng Common_data trên Firestore.
        
        Args:
            query (str): Truy vấn mở rộng.
            
        Returns:
            List[Dict]: Danh sách dữ liệu chung liên quan.
        """
        try:
            # Liên kết với dịch vụ Firebase để kéo dữ liệu (Firestore read)
            docs = self.m_dbHandler.m_dbClient.collection("Common_data").stream()
            
            commonList = []
            normalizedQuery = query.lower()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Chuyển đổi dữ liệu thành text để chấm điểm (Stringify for scoring)
                searchTarget = str(data).lower()
                score = fuzz.token_set_ratio(normalizedQuery, searchTarget)
                
                if score >= 40:
                    commonList.append((score, data))
            
            # Sắp xếp giảm dần và lấy giá trị (Sort descending)
            commonList.sort(key=lambda x: x[0], reverse=True)
            return [data for score, data in commonList[:3]]
            
        except Exception as e:
            self.m_logError("searchCommonData", str(e))
            return []

    def m_logError(self, functionName: str, errorMsg: str) -> None:
        """
        Chuyên trách ghi log mọi ngoại lệ của trình duyệt tìm kiếm (Exception Logger) 
        vào bộ sưu tập `AI_logs` của Firebase.
        
        Args:
            functionName (str): Tên hàm khởi tạo lỗi.
            errorMsg (str): Nội dung lỗi (Error description).
        """
        try:
            logData = {
                "module": "SearchEngine",
                "function": functionName,
                "error": errorMsg,
                "traceback": traceback.format_exc()
            }
            # Gọi lại chính quy trình ghi log chung từ FirestoreHandler (Dependency reuse)
            self.m_dbHandler.saveDocument("AI_logs", logData)
        except Exception as systemErr:
            print(f"Hệ thống log thất bại (CRITICAL Logger Failure): {systemErr}")
