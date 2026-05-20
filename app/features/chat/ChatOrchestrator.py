"""
Điều phối luồng chat: PriorityLogic (issue_manager) -> RAG ngắn -> Gemini với prompt theo mức.
"""

import time
from typing import Any, Dict, List

from app.core.Middleware import Middleware
from app.features.chat.PromptTemplates import buildTierGeminiInstruction
from app.features.issue_manager.ChatIssueBridge import ChatIssueBridge
from app.features.issue_manager.PriorityLogic import PriorityLogic
from app.utils.StringHelpers import StringHelpers


class ChatOrchestrator:
    """
    Luồng chính cho UI: phân loại bằng PriorityLogic, sinh câu trả lời Gemini theo tier prompt.
    """

    def __init__(self) -> None:
        self.m_priorityLogic = PriorityLogic()
        self.m_issueBridge = ChatIssueBridge()

    def _generateGeminiWithTier(
        self,
        middleware: Middleware,
        cleanedQuery: str,
        combinedMemory: str,
        tierKey: str,
    ) -> str:
        """
        Gọi Gemini với chỉ dẫn theo mức ưu tiên (tierKey: INVALID | P0 | P1 | P2).
        """
        if not hasattr(middleware, "m_geminiModel"):
            return "Hệ thống AI nền tảng chưa được cấu hình. (Cloud Service Absent)"

        tierInstruction = buildTierGeminiInstruction(tierKey)
        instructedPrompt = (
            f"{tierInstruction}\n\n"
            f"Thông tin hệ thống hỗ trợ và ngữ cảnh:\n{combinedMemory}\n\n"
            f"Câu hỏi/nội dung của sinh viên: {cleanedQuery}"
        )

        try:
            startTick = time.time()
            response = middleware.m_geminiModel.generate_content(instructedPrompt)
            elapsedSecs = time.time() - startTick

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                return (
                    "Phản hồi đã bị ngắt do phát hiện nội dung có nguy cơ vi phạm "
                    "(Content Safety Enforcement)."
                )

            finalAnswer = response.text
            estimatedTokens = len(instructedPrompt.split()) + len(finalAnswer.split())
            middleware.m_logAiUsage(
                "gemini_cloud_tiered",
                elapsedSecs,
                instructedPrompt,
                finalAnswer,
                estimatedTokens,
            )
            return finalAnswer
        except Exception as systemErr:
            print(f"Gemini tiered chat lỗi (Gemini tiered error): {systemErr}")
            return "Rất tiếc bộ khuếch đại AI đang bảo trì. Vui lòng thử gọi lại tôi sau vài phút."

    def processTurn(
        self,
        middleware: Middleware,
        studentMessage: str,
        chatId: str,
        studentId: str,
    ) -> Dict[str, Any]:
        """
        Xử lý một lượt chat đầy đủ: phân loại -> (tuỳ chọn) ticket -> Gemini -> trả metadata UI.

        Returns:
            Dict gồm answer, quick_actions, priority_level, category, is_fallback
        """
        cleanedQuery = StringHelpers.cleanText(studentMessage)

        priorityLevel, category, isFallback = self.m_priorityLogic.determinePriority(
            cleanedQuery
        )

        middleware.m_contextManager.addMessage(chatId, "user", cleanedQuery)

        searchKeywords = StringHelpers.extractKeywords(cleanedQuery)
        knowledgeList = middleware.m_searchEngine.findRelevantContext(
            searchKeywords, topN=2
        )
        knowledgeStrs = [item.get("content", "") for item in knowledgeList]
        ragContext = "\n".join(knowledgeStrs)

        chatHistory = middleware.m_contextManager.getChatContext(chatId, limit=4)
        historyText = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in chatHistory[:-1]]
        )
        combinedMemory = (
            f"Lịch sử tương tác ngắn:\n{historyText}\n\nKiến thức chuẩn lưu trữ:\n{ragContext}"
        )

        rawGeminiReply = self._generateGeminiWithTier(
            middleware=middleware,
            cleanedQuery=cleanedQuery,
            combinedMemory=combinedMemory,
            tierKey=priorityLevel,
        )
        finalResponse = StringHelpers.formatResponse(rawGeminiReply)

        middleware.m_contextManager.addMessage(chatId, "assistant", finalResponse)

        self.m_issueBridge.createIssueFromPriorityResult(
            chatId=chatId,
            studentId=studentId,
            rawMessage=studentMessage,
            priorityLevel=priorityLevel,
            category=category,
            isFallback=isFallback,
        )

        quickActions = self._quickActionsForTier(priorityLevel)

        return {
            "answer": finalResponse,
            "quick_actions": quickActions,
            "priority_level": priorityLevel,
            "category": category,
            "is_fallback": isFallback,
        }

    def _quickActionsForTier(self, priorityLevel: str) -> List[str]:
        """Gợi ý thao tác nhanh theo mức ưu tiên."""
        if priorityLevel == "P0":
            return [
                "Liên hệ GVCN hoặc cố vấn tâm lý",
                "Xem quy trình hỗ trợ khẩn trong sổ tay sinh viên",
            ]
        if priorityLevel == "P1":
            return [
                "Đặt lịch gặp GVCN",
                "Chuẩn bị giấy tờ/minh chứng nếu có",
            ]
        if priorityLevel == "P2":
            return [
                "Xem FAQ & quy chế",
                "Đặt thêm câu hỏi cụ thể để mình hỗ trợ đúng phần việc",
            ]
        return ["Gửi nội dung học tập/hành chính cụ thể", "Tránh tin nhắn spam hoặc thử đùa"]
