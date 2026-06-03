import json
import re
import time
from typing import Any, Dict, List
from groq import Groq
from app.core.Middleware import Middleware
from app.features.chat.PromptTemplates import buildCombinedPrompt
from app.features.issue_manager.ChatIssueBridge import ChatIssueBridge
from app.features.issue_manager.PriorityLogic import PriorityLogic
from app.utils.StringHelpers import StringHelpers
from app.services.FirestoreHandler import FirestoreHandler


class ChatOrchestrator:
    """
    Luồng chính cho UI: phân loại bằng PriorityLogic, sau đó gọi Gemini một lần duy nhất
    để vừa trích xuất từ khóa (Keyword Extraction) vừa sinh câu trả lời (Response Generation)
    theo tier prompt tương ứng.
    """

    def __init__(self) -> None:
        self.m_priorityLogic = PriorityLogic()
        self.m_issueBridge = ChatIssueBridge()

    def _callCombined(
        self,
        middleware: Middleware,
        cleanedQuery: str,
        historyText: str,
        tierKey: str,
    ) -> Dict[str, Any]:
        # Kiểm tra sự tồn tại của Groq client 
        if not hasattr(middleware, "m_groqClient"):
            return {
                "keywords": [],
                "answer": "Hệ thống AI nền tảng chưa được cấu hình. (Cloud Service Absent)",
            }

        prompt = buildCombinedPrompt(tierKey, cleanedQuery, historyText)

        try:
            startTick = time.time()

            # Gọi Groq theo format OpenAI messages 
            response = middleware.m_groqClient.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, 
                max_tokens=1024,
            )
            elapsedSecs = time.time() - startTick

            # Trích xuất text từ response
            raw = response.choices[0].message.content.strip()

            # Bóc backtick nếu model thêm vào 
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()

            parsed = json.loads(raw)

            estimatedTokens = response.usage.total_tokens
            middleware.m_logAiUsage(
                "groq_llama3",
                elapsedSecs,
                prompt,
                parsed,
                estimatedTokens,
            )
            return parsed

        except json.JSONDecodeError:
            fallbackAnswer = response.choices[0].message.content if "response" in dir() else ""
            return {
                "keywords": StringHelpers.extractKeywords(cleanedQuery).split(),
                "answer": fallbackAnswer,
            }
        except Exception as systemErr:
            print(f"Groq error: {systemErr}")
            return {
                "keywords": [],
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
        Luồng: Phân loại (Classify) -> Gemini 1 lần (Single Inference) ->
        RAG tra cứu tri thức (Knowledge Retrieval) -> Định dạng (Format) -> UI.

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

        # Step 2:  Xác định mức độ ưu tiên và danh mục vấn đề 
        priorityLevel, category, isFallback = self.m_priorityLogic.determinePriority(cleanedQuery)

        # Lưu tin nhắn người dùng vào bộ nhớ ngữ cảnh
        middleware.m_contextManager.addMessage(chatId, "user", cleanedQuery)

        # Step 3: Nạp lịch sử hội thoại ngắn để AI không bị quên mạch
        chatHistory = middleware.m_contextManager.getChatContext(chatId, limit=4)
        historyText = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in chatHistory[:-1]
        )

        # Step 4: Gọi AI để đồng thời trích xuất keyword và sinh câu trả lời
        combined = self._callCombined(
            middleware=middleware,
            cleanedQuery=cleanedQuery,
            historyText=historyText,
            tierKey=priorityLevel,
        )

        # Tách dữ liệu từ JSON trả về
        keywords: List[str] = combined.get("keywords", [])
        rawAnswer: str = combined.get("answer", "")
        print(f"--- Keywords trích xuất: {keywords} ---")

        # Step 5: Tra cứu Firestore bằng keywords vừa nhận (DB Lookup)
        ragContext = ""
        if keywords:
            dbHandler = FirestoreHandler()
            # Giới hạn 10 từ khóa theo ràng buộc array_contains_any của Firestore
            searchWords = keywords[:10]
            try:
                commonDataList = dbHandler.queryDocuments(
                    collectionName="Common_data",
                    filters=[("keywords", "array_contains_any", searchWords)],
                    limitCount=3,
                )

                # Nối các đoạn tri thức thành ngữ cảnh dạng chuỗi
                ragContext = "\n".join(
                    f"Nội dung: {d.get('content', '')}\nNguồn: {d.get('source', '')}"
                    for d in commonDataList
                )
            except Exception as dbErr:
                print(f"Lỗi truy vấn Database: {dbErr}")

        # Step 6: format văn bản 
        finalResponse = StringHelpers.formatResponse(rawAnswer)

        # Cất thư trả lời vào bộ nhớ ngữ cảnh
        middleware.m_contextManager.addMessage(chatId, "assistant", finalResponse)

        # Step 7: Tạo bản ghi vấn đề cho bảng điều khiển GVCN 
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