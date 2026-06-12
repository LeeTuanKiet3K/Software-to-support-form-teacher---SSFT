from groq import Groq
from typing import List, Dict, Any
from app.core.Config import AppConfig
from app.services.FirestoreHandler import FirestoreHandler
from app.features.chat.PromptTemplates import PROMPT_CONTEXT_SUMMARIZATION


class ContextManager:
    """
    Trình quản lý ngữ cảnh hội thoại (Context Manager).
    Quản lý bộ nhớ các đoạn hội thoại để AI hiểu mạch trò chuyện.
    """
    m_instance = None

    def __new__(cls):
        """
        Khởi tạo ContextManager.
        Chỉ tạo thể hiện mới nếu chưa tồn tại — các lần gọi sau trả về cùng một object.
        """
        if cls.m_instance is None:
            cls.m_instance = super(ContextManager, cls).__new__(cls)

            cls.m_instance.m_dbHandler = FirestoreHandler()

            cls.m_instance.m_conversationHistory = {}

            groqKey = AppConfig.GROQ_API_KEY
            if groqKey:
                cls.m_instance.m_groqClient = Groq(api_key=groqKey)


        return cls.m_instance

    def addMessage(self, chatId: str, role: str, content: str) -> None:
        """
        Lưu tin nhắn mới vào bộ nhớ tạm và đồng bộ xuống Firestore.

        Args:
            chatId (str): ID phiên hội thoại.
            role (str): Vai trò người gửi — 'user' hoặc 'assistant'.
            content (str): Nội dung tin nhắn.
        """
        if chatId not in self.m_conversationHistory:
            self.m_conversationHistory[chatId] = []

        messageRecord = {"role": role, "content": content}
        self.m_conversationHistory[chatId].append(messageRecord)

        try:
            self.m_dbHandler.saveDocument("chats", {
                "chat_id": chatId,
                "role": role,
                "content": content
            })
        except Exception as systemErr:
            print(f"Error persisting chat history: {systemErr}")

    def getChatContext(self, chatId: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Lấy N tin nhắn gần nhất để làm ngữ cảnh cho AI.
        Giới hạn số lượng tin nhắn giúp tối ưu token truyền vào model.

        Args:
            chatId (str): ID phiên hội thoại.
            limit (int): Số tin nhắn tối đa cần lấy, mặc định 5.

        Returns:
            List[Dict]: Danh sách tin nhắn theo thứ tự thời gian.
        """
        historyList = self.m_conversationHistory.get(chatId, [])
        return historyList[-max(limit, 1):]

    def summarizeOldContext(self, chatId: str) -> str:
        """
        Dùng Groq tóm tắt các tin nhắn cũ khi lịch sử hội thoại quá dài
        Mục tiêu: nén lịch sử thành 1-2 câu để tiết kiệm token ở các lượt gọi tiếp theo.

        Chiến lược:
            - Giữ nguyên 4 tin nhắn gần nhất
            - Tóm tắt tất cả tin nhắn cũ hơn bằng Groq

        Args:
            chatId (str): ID phiên hội thoại cần tóm tắt .

        Returns:
            str: Chuỗi tóm tắt ngữ cảnh, hoặc chuỗi rỗng nếu chưa đủ dài để tóm tắt.
        """
        historyList = self.m_conversationHistory.get(chatId, [])
        if len(historyList) <= 6:
            return ""

        try:
            oldMessages = historyList[:-4]
            contextBody = "\n".join([f"{msg['role']}: {msg['content']}" for msg in oldMessages])

            promptInjection = PROMPT_CONTEXT_SUMMARIZATION.format(context_body=contextBody)

            response = self.m_instance.m_groqClient.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": promptInjection}],
            max_tokens=256,
            )
            summaryBody = response.choices[0].message.content

            self.m_instance.m_dbHandler.saveDocument("AI_logs", {
                "action": "summarize_context",
                "chat_id": chatId,
                "summary": summaryBody
            })

            return summaryBody

        except Exception as error:
            print(f"Context Summarization Failed: {error}")
            return ""