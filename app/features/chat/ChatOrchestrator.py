import json
import re
import time
from typing import Any, Dict, List

from app.core.Middleware import Middleware
from app.features.chat.PromptTemplates import AnsweringWithRAG, PROMPT_KEYWORD_EXTRACTION
from app.features.issue_manager.ChatIssueBridge import ChatIssueBridge
from app.features.issue_manager.PriorityLogic import PriorityLogic
from app.utils.StringHelpers import StringHelpers
from app.services.FirestoreHandler import FirestoreHandler


class ChatOrchestrator:
    """
    Luồng chính cho UI: phân loại bằng PriorityLogic, sau đó gọi Groq theo luồng 3 bước:
    Call #1 (chỉ lấy keywords) -> Firestore Search -> Call #2 (trả lời với RAG context).
    """

    def __init__(self) -> None:
        self.m_priorityLogic = PriorityLogic()
        self.m_issueBridge = ChatIssueBridge()

    def _extractKeywords(
        self,
        middleware: Middleware,
        cleanedQuery: str,
    ) -> List[str]:
        """Call #1: Trích xuất keywords dạng cụm từ để query Firestore."""
        if not hasattr(middleware, "m_groqClient"):
            return StringHelpers.extractKeywords(cleanedQuery).split()

        prompt = PROMPT_KEYWORD_EXTRACTION.format(user_message=cleanedQuery)
        try:
            response = middleware.m_groqClient.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=128,
            )
            raw = response.choices[0].message.content.strip()
            return [k.strip().lower() for k in raw.split(",") if k.strip()]
        except Exception as e:
            print(f"Keyword extraction error: {e}")
            return StringHelpers.extractKeywords(cleanedQuery).split()

    def _finalAnswerWithRAG(
        self,
        middleware: Middleware,
        cleanedQuery: str,
        historyText: str,
        tierKey: str,
        ragContext: str = "",
    ) -> Dict[str, Any]:
        """Call #2: Sinh câu trả lời cuối cùng dựa trên RAG context."""
        if not hasattr(middleware, "m_groqClient"):
            return {
                "answer": "Hệ thống AI nền tảng chưa được cấu hình. (Cloud Service Absent)",
            }

        prompt = AnsweringWithRAG(
            tierKey=tierKey,
            ragContext=ragContext,
            historyText=historyText,
            cleanedQuery=cleanedQuery,
        )

        try:
            startTick = time.time()
            response = middleware.m_groqClient.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            elapsedSecs = time.time() - startTick

            rawAnswer = response.choices[0].message.content.strip()

            middleware.m_logAiUsage(
                "groq_final_answer",
                elapsedSecs,
                prompt,
                rawAnswer,
                response.usage.total_tokens,
            )
            return {"answer": rawAnswer}

        except Exception as systemErr:
            print(f"Groq error: {systemErr}")
            return {
                "answer": "Rất tiếc hệ thống đang bảo trì. Vui lòng thử lại sau vài phút.",
            }

    def processTurn(
        self,
        middleware: Middleware,
        studentMessage: str,
        chatId: str,
        studentId: str,
    ) -> Dict[str, Any]:
        """
        Luồng: Phân loại (Classify) -> gọi Groq 1 lần (Extract keywords) ->
        RAG tra cứu tri thức -> gọi Groq lần 2 (trả lời) -> Định dạng (Format) -> UI.

        Args:
            middleware (Middleware): Bộ điều phối trung tâm.
            studentMessage (str): Tin nhắn gốc từ sinh viên.
            chatId (str): ID phiên hội thoại (Session Identifier).
            studentId (str): ID sinh viên (Student Identifier).

        Returns:
            Dict: Phản hồi hoàn chỉnh kèm metadata cho UI.
        """
        # Step 1: Chuẩn hóa đầu vào, loại bỏ ký tự dư thừa
        cleanedQuery = StringHelpers.cleanText(studentMessage)

        # Step 2: Xác định mức độ ưu tiên và danh mục vấn đề
        priorityLevel, category, isFallback = self.m_priorityLogic.determinePriority(cleanedQuery)

        # Lưu tin nhắn người dùng vào bộ nhớ ngữ cảnh
        middleware.m_contextManager.addMessage(chatId, "user", cleanedQuery)

        # Step 3: Nạp lịch sử hội thoại ngắn để AI không bị quên mạch
        chatHistory = middleware.m_contextManager.getChatContext(chatId, limit=4)
        historyText = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in chatHistory[:-1]
        )

        # Step 4: Call #1 — trích xuất keywords dạng cụm từ khớp với DB
        keywords = self._extractKeywords(middleware, cleanedQuery)
        print(f"--- Keywords AI trích xuất: {keywords} ---")

        # Step 5: Firestore Search
        ragContext = ""
        imageUrls: List[str] = []
        if keywords:
            dbHandler = FirestoreHandler()
            try:
                commonDataList = dbHandler.queryDocuments(
                    collectionName="Common_data",
                    filters=[("keywords", "array_contains_any", keywords[:10])],
                    limitCount=3,
                )
                print(f"--- Tìm thấy {len(commonDataList)} tài liệu ---")
                for doc in commonDataList:
                    print(f"{doc.get('Document ID', '')}")
                ragContext = "\n".join(
                    f"Nội dung: {d.get('content', '')}"
                    for d in commonDataList
                )
                imageUrls = [
                    d.get("source", "")
                    for d in commonDataList
                    if d.get("source", "").lower().endswith(".png")
                ]
            except Exception as dbErr:
                print(f"Lỗi truy vấn Database: {dbErr}")

        # Step 6: Call #2 — sinh câu trả lời cuối cùng với RAG context
        answerResult = self._finalAnswerWithRAG(
            middleware=middleware,
            cleanedQuery=cleanedQuery,
            historyText=historyText,
            tierKey=priorityLevel,
            ragContext=ragContext,
        )

        rawAnswer: str = answerResult.get("answer", "")

        # Step 7: Format văn bản
        finalResponse = StringHelpers.formatResponse(rawAnswer)

        middleware.m_contextManager.addMessage(chatId, "assistant", finalResponse)

        # Step 8: Tạo bản ghi vấn đề cho bảng điều khiển GVCN
        self.m_issueBridge.createIssueFromPriorityResult(
            chatId=chatId,
            studentId=studentId,
            rawMessage=studentMessage,
            priorityLevel=priorityLevel,
            category=category,
            isFallback=isFallback,
        )

        return {
            "answer": finalResponse,
            "quick_actions": self._quickActionsForTier(priorityLevel),
            "priority_level": priorityLevel,
            "category": category,
            "is_fallback": isFallback,
            "image_urls": imageUrls,
        }

    def _quickActionsForTier(self, priorityLevel: str) -> List[str]:
        """
        Đề xuất hành động nhanh cho sinh viên dựa theo mức ưu tiên (Contextual Quick Actions).
        Các thẻ bấm này được hiển thị ngay bên dưới câu trả lời trên UI (Actionable UI Chips).
        """
        if priorityLevel == "P0":
            return ["Liên hệ GVCN hoặc cố vấn tâm lý", "Xem quy trình hỗ trợ khẩn"]
        if priorityLevel == "P1":
            return ["Đặt lịch gặp GVCN", "Chuẩn bị giấy tờ/minh chứng nếu có"]
        if priorityLevel == "P2":
            return ["Xem FAQ & quy chế", "Đặt thêm câu hỏi cụ thể để mình hỗ trợ"]

        return ["Gửi nội dung cụ thể", "Tránh tin nhắn spam"]