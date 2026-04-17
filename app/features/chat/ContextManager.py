import google.generativeai as genai
from typing import List, Dict, Any
from app.core.Config import AppConfig
from app.services.FirestoreHandler import FirestoreHandler

class ContextManager:
    """
    Trình quản lý ngữ cảnh hội thoại (Context Manager).
    Quản lý bộ nhớ các đoạn hội thoại (Conversation Memory) để AI hiểu mạch trò chuyện.
    """
    
    # Sử dụng Singleton Pattern để giữ bộ nhớ đồng nhất toàn hệ thống
    m_instance = None

    def __new__(cls):
        """Khởi tạo ContextManager (Singleton Instantiation)."""
        if cls.m_instance is None:
            cls.m_instance = super(ContextManager, cls).__new__(cls)
            # Khởi tạo liên kết cơ sở dữ liệu (Database Link)
            cls.m_instance.m_dbHandler = FirestoreHandler()
            
            # Bộ nhớ tạm lưu trữ RAM (Temporary memory mapping)
            cls.m_instance.m_conversationHistory = {}
            
            # Cấu hình độc lập API nội bộ để chạy luồng tóm tắt (Independent AI Configuration)
            geminiKey = AppConfig.GEMINI_API_KEY
            if geminiKey:
                genai.configure(api_key=geminiKey)
                cls.m_instance.m_geminiModel = genai.GenerativeModel('gemini-1.5-flash')
                
        return cls.m_instance

    def addMessage(self, chatId: str, role: str, content: str) -> None:
        """
        Lưu tin nhắn mới vào bộ nhớ tạm (Add message caching).
        
        Args:
            chatId (str): Mã định danh phiên chat hiện tại.
            role (str): Vai trò của tác giả (VD: user, assistant).
            content (str): Nội dung chi tiết của bản ghi.
        """
        if chatId not in self.m_conversationHistory:
            self.m_conversationHistory[chatId] = []
            
        messageRecord = {"role": role, "content": content}
        self.m_conversationHistory[chatId].append(messageRecord)
        
        # Đồng bộ dư liệu song song (Persistent Storage Replication) xuống Firestore
        try:
            self.m_dbHandler.saveDocument("chats", {
                "chat_id": chatId,
                "role": role,
                "content": content
            })
        except Exception as systemErr:
            # Ghi nhận lỗi nhưng không ngắt chương trình (Non-blocking exception)
            print(f"Lỗi sao lưu lịch sử tin nhắn (Chat Persistence Error): {systemErr}")

    def getChatContext(self, chatId: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Lấy N tin nhắn gần nhất để làm ngữ cảnh cho AI (Rolling Context Retrieval).
        
        Args:
            chatId (str): ID phiên hội thoại.
            limit (int): Kích thước cửa sổ trượt (Sliding window size).
            
        Returns:
            List[Dict]: Một danh sách lịch sử tin nhắn mới nhất.
        """
        historyList = self.m_conversationHistory.get(chatId, [])
        return historyList[-max(limit, 1):]

    def summarizeOldContext(self, chatId: str) -> str:
        """
        Sử dụng Gemini chạy nền tóm tắt các cuộc hội thoại quá lớn (Context Summarization),
        nhằm tối ưu mật độ token truyền vào (Token Compression).
        
        Args:
            chatId (str): Mã session trò chuyện.
            
        Returns:
            str: Bản tóm tắt súc tích, nếu hội thoại ngắn sẽ trả về dạng rỗng.
        """
        historyList = self.m_conversationHistory.get(chatId, [])
        
        # Token Optimization Check: Chỉ kích hoạt tóm tắt khi nội dung quá dài
        if len(historyList) <= 6:
            return ""
            
        try:
            oldMessages = historyList[:-4]
            contextBody = "\n".join([f"{msg['role']}: {msg['content']}" for msg in oldMessages])
            
            promptInjection = f"Hãy tóm tắt ngắn gọn hội thoại này thành 1-2 câu để làm ngữ cảnh nền tảng cho trợ lý AI:\n{contextBody}"
            
            # Phát sinh kết quả song song (Background Generation)
            response = self.m_geminiModel.generate_content(promptInjection)
            summaryBody = response.text
            
            # Ghi log lịch trình (Audit Trail Logging)
            self.m_dbHandler.saveDocument("AI_logs", {
                "action": "summarize_context",
                "chat_id": chatId,
                "summary": summaryBody
            })
            
            return summaryBody
            
        except Exception as error:
            print(f"Tiến trình tóm tắt ngữ cảnh gián đoạn (Context Summarization Failed): {error}")
            return ""
