import json
import time
import requests
import google.generativeai as genai
from typing import Dict, Any

from firebase_admin import firestore

from app.core.Config import AppConfig
from app.services.FirestoreHandler import FirestoreHandler
from app.utils.StringHelpers import StringHelpers
from app.utils.SearchEngine import SearchEngine
from app.features.chat.ContextManager import ContextManager

class Middleware:
    """
    Bộ điều phối quy trình hợp nhất AI (AI Orchestrator / Middleware Layer).
    Điều phối luồng dữ liệu theo kiến trúc Hybrid Logic: Client (SV) -> Llama 3 (Phân tích) -> 
    SearchEngine (Tra cứu tri thức) -> Gemini (Suy luận & Hội thoại vòng ngoài).
    """

    def __init__(self) -> None:
        """
        Khởi tạo và kết nối các client máy chủ suy luận (Models Instantiation).
        """
        # Cấu hình cho Local Inference LLM (Llama)
        self.m_ollamaUrl = AppConfig.OLLAMA_BASE_URL
        self.m_ollamaModel = AppConfig.OLLAMA_MODEL_NAME
        
        # Cấu hình cho Cloud Inference LLM (Gemini)
        self.m_geminiKey = AppConfig.GEMINI_API_KEY
        if self.m_geminiKey:
            genai.configure(api_key=self.m_geminiKey)
            # Khởi tạo instance kết nối (Service Binding)
            self.m_geminiModel = genai.GenerativeModel('gemini-1.5-flash')
            
        # Khởi chạy Dependency Injection với các Module đã lập trình trước (Data Linking)
        self.m_dbHandler = FirestoreHandler()
        self.m_searchEngine = SearchEngine()
        self.m_contextManager = ContextManager()

    def callLocalLlama(self, prompt: str) -> Dict[str, Any]:
        """
        Sử dụng Local Llama phục vụ phân tích cảm xúc (Sentiment Analysis) và ý định (Intent Classification).
        Chuyển mô hình LLM từ văn bản trực tiếp sang dữ liệu dạng JSON.
        
        Args:
            prompt (str): Câu lệnh gốc đưa vào.
            
        Returns:
            Dict: Đối tượng nhận biết ý định của đầu vào.
        """
        sysPrompt = (
            "Bạn là bộ lọc NLP (Natural Language Processing). Phân tích nội dung và trả về JSON chuẩn xác "
            "với 'intent' (Ý định: hoi_dap, khieu_nai, tam_ly) và "
            "'sentiment' (Cảm xúc: tich_cuc, tieu_cuc, trung_lap)."
            f"\n\nCâu nói: {prompt}"
        )
        
        payload = {
            "model": self.m_ollamaModel,
            "prompt": sysPrompt,
            "format": "json",
            "stream": False
        }
        
        try:
            startTick = time.time()
            res = requests.post(f"{self.m_ollamaUrl}/api/generate", json=payload)
            res.raise_for_status()
            elapsedSecs = time.time() - startTick
            
            rawOutput = res.json().get("response", "{}")
            parsedData = json.loads(rawOutput)
            
            # Vết theo dõi hoạt động và tối ưu ứng dụng (Telemetry Performance Logging)
            self.m_logAiUsage("llama3_local", elapsedSecs, prompt, parsedData)
            
            return parsedData
        except Exception as systemErr:
            print(f"Đứt gãy kết nối với Local LLM (Local Inference Broken): {systemErr}")
            return {"intent": "khong_ro", "sentiment": "trung_lap"}

    def callCloudGemini(self, prompt: str, context: str) -> str:
        """
        Truy vấn trực tuyến qua Cloud Gemini để tạo dạng ngôn từ (Response Generation) 
        dựa trên dữ liệu tài nguyên sẵn có (Context Grounding).
        
        Args:
            prompt (str): Thông điệp gốc của SV.
            context (str): Văn bản tri thức cần RAG đính kèm.
            
        Returns:
            str: Đáp án đã lập luận đầy đủ.
        """
        if not hasattr(self, 'm_geminiModel'):
            return "Hệ thống AI nền tảng chưa được cấu hình. (Cloud Service Absent)"
            
        # Kiến trúc Prompt theo kiểu Zero-Shot có tri thức (Prompt Engineering)
        instructedPrompt = (
            f"Sử dụng thông tin hệ thống cung cấp dưới đây để trả lời câu hỏi sinh viên.\n"
            f"Thông tin hệ thống hỗ trợ:\n{context}\n\n"
            f"Câu hỏi của sinh viên: {prompt}"
        )
        
        try:
            startTick = time.time()
            response = self.m_geminiModel.generate_content(instructedPrompt)
            elapsedSecs = time.time() - startTick
            
            # Module đánh giá an ninh nội dung (Safety Metrics Check)
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                return "Phản hồi đã bị ngắt do phát hiện nội dung có nguy cơ vi phạm (Content Safety Enforcement)."
                
            finalAnswer = response.text
            
            # Điểm tính toán token sơ lược (Token Approximation)
            estimatedTokens = len(instructedPrompt.split()) + len(finalAnswer.split())
            
            self.m_logAiUsage("gemini_cloud", elapsedSecs, instructedPrompt, finalAnswer, estimatedTokens)
            
            return finalAnswer
        except Exception as systemErr:
            print(f"Cloud Server từ chối phản hồi (Gemini Instance Offline): {systemErr}")
            return "Rất tiếc bộ khuếch đại AI đang bảo trì. Vui lòng thử gọi lại tôi sau vài phút."

    def coordinateFlow(self, studentMessage: str, chatId: str = "default_session") -> str:
        """
        Hệ điều phối vòng đời tin nhắn (Pipeline Orchestrator Layer).
        Kích hoạt Hybrid Logic: Tin nhắn -> Llama 3 -> SearchEngine -> Gemini -> Formatted Response.
        
        Args:
            studentMessage (str): Thông điệp từ bảng UI mà sinh viên gửi.
            chatId (str): ID kết nối định danh sinh viên (để duy trì Context Manager).
            
        Returns:
            str: Văn bản phản hồi cuối cùng sau quá trình đánh bóng.
        """
        # [Step 1: Sanitize Signal] Chuẩn hóa và làm rỗng mã độc nội dung
        cleanedQuery = StringHelpers.cleanText(studentMessage)
        self.m_contextManager.addMessage(chatId, "user", cleanedQuery)
        
        # [Step 2: Semantic Intent Analytics] Chạy Llama 3 để phân vùng loại nội dung cần trả lời
        llamaAnalytics = self.callLocalLlama(cleanedQuery)
        # Ghi chú: Có thể mở rộng dùng `llamaAnalytics['sentiment']` để báo động Issue lên màu đỏ (URGENT) cho bảng điều khiển của GVCN sau này.
        
        # [Step 3: Keyword Extraction & Target Traversal] Bóc tách khóa để thu hồi thông tin RAG
        searchKeywords = StringHelpers.extractKeywords(cleanedQuery)
        knowledgeList = self.m_searchEngine.findRelevantContext(searchKeywords, topN=2)
        
        # Nối và định hình các văn bản rời rạc lại (Synthesizing string chunks)
        knowledgeStrs = [item.get("content", "") for item in knowledgeList]
        ragContext = "\n".join(knowledgeStrs)
        
        # Nạp lịch sử vào để AI không bị mắc lỗi quên quá khứ (Historical Context Injection)
        chatHistory = self.m_contextManager.getChatContext(chatId, limit=4)
        historyText = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chatHistory[:-1]])
        
        combinedMemory = f"Lịch sử tương tác ngắn:\n{historyText}\n\nKiến thức chuẩn lưu trữ:\n{ragContext}"
        
        # [Step 4: Central Cloud Computing] Kêu gọi Gemini phác thảo kiến tạo ngôn ngữ cuối cùng
        rawGeminiReply = self.callCloudGemini(cleanedQuery, combinedMemory)
        
        # [Step 5: Output Polish] Đánh bóng văn bản tương tác UI
        finalResponse = StringHelpers.formatResponse(rawGeminiReply)
        
        # Cất thư trả lời của thiết bị vào bộ chứa (Memory State Saving)
        self.m_contextManager.addMessage(chatId, "assistant", finalResponse)
        
        return finalResponse

    def m_logAiUsage(self, modelId: str, timeSecs: float, traceIn: str, traceOut: Any, tokens: int = 0) -> None:
        """
        Hàm giám sát và quản lý tác vụ AI (Telemetry & Telecommand Monitor).
        Đảm bảo tuân thủ cấu trúc lưu vết trong Workflow cho mọi yêu cầu gọi LLM.
        
        Args:
            modelId (str): Phiên bản LLM được gọi.
            timeSecs (float): Độ trễ (Latency).
            traceIn (str): Tải lượng đi vào (Inbound Data).
            traceOut (Any): Kết quả AI (Outbound Target).
            tokens (int): Mật độ tiêu thụ (Consumption scale).
        """
        try:
            logStructure = {
                "model_identifier": modelId,
                "latency_seconds": timeSecs,
                "tokens_estimated": tokens,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            # Gọi API hạ tầng ghi dữ liệu lên Cloud Firebase (Database Integration)
            self.m_dbHandler.saveDocument("AI_logs", logStructure)
        except Exception as e:
            print(f"Đứt liên lạc Logger (Audit Disconnected): {e}")
