import os
import json
import google.generativeai as genai
from app.services.FirestoreHandler import FirestoreHandler
from app.features.issue_manager.PriorityLogic import classifyAndPrioritize
from app.features.chat.PromptTemplates import SYSTEM_PROMPT_ADVISOR
from app.core.Constants import IssueStatus
from app.utils.StringHelpers import StringHelpers

def processStudentMessage(studentIdOrName: str, issueText: str, firestoreHandler: FirestoreHandler) -> str:
    """
    Xử lý tin nhắn của sinh viên: Phân loại mức độ ưu tiên và chuyển tiếp 
    hoặc sử dụng Gemini API để trả lời tự động dựa trên Cơ sở tri thức.
    
    Args:
        studentIdOrName (str): Định danh của sinh viên.
        issueText (str): Nội dung câu hỏi/vấn đề.
        firestoreHandler (FirestoreHandler): Đối tượng thao tác với database.
        
    Returns:
        str: Câu trả lời tự động hoặc thông báo chuyển tiếp.
    """
    # 1. Phân loại vấn đề (Classify and Prioritize)
    priorityResult = classifyAndPrioritize(issueText)
    
    # 2. Xử lý Fallback (Chuyển tiếp cho GVCN)
    if priorityResult["isFallback"]:
        # Lưu vấn đề vào Firestore (Save complex issue to Firestore)
        # Vì đây là P0 hoặc P1, chúng ta sẽ lưu với status là "Pending Advisor"
        firestoreHandler.saveDocument("Issues", {
            "student_id": studentIdOrName,
            "issue_text": issueText,
            "priority": priorityResult["priorityLevel"],
            "status": IssueStatus.PENDING_ADVISOR
        })
        # Trả về câu thông báo mặc định (Return fallback message)
        return "Vấn đề của bạn đã được ghi nhận ở mức ưu tiên cao và chuyển đến trực tiếp GVCN. Thầy/cô sẽ liên hệ với bạn trong thời gian sớm nhất."
        
    # 3. Sử dụng AI để trả lời (Normal P2 issues)
    # Lấy API Key từ môi trường (Fetch API Key)
    apiKey = os.getenv("GEMINI_API_KEY")
    if not apiKey:
        return "Hệ thống AI hiện đang bảo trì (Thiếu API Key). Vui lòng liên hệ trực tiếp GVCN."
        
    # Lấy cơ sở tri thức để làm Grounding/Context (Fetch context)
    contextStr = "Dưới đây là một số thông tin quy định từ nhà trường:\n"
    
    # 1. Tải từ JSON
    try:
        with open("data/KnowledgeBase.json", "r", encoding="utf-8") as f:
            kbData = json.load(f)
            for category, items in kbData.items():
                if isinstance(items, dict):
                    for key, value in items.items():
                        contextStr += f"- {value}\n"
    except Exception as e:
        print(f"Lỗi đọc KnowledgeBase: {e}")
        
    # 2. Tải thêm từ Firestore nếu có từ khóa
    keywords = StringHelpers.extractKeywords(issueText)
    if keywords:
        try:
            commonDataList = firestoreHandler.queryDocuments("common_data", [])
            for data in commonDataList:
                title = data.get("title", "")
                content = data.get("content", "")
                if title and content:
                    contextStr += f"- {title}: {content}\n"
        except Exception as e:
            print(f"Lỗi query common_data: {e}")
            
    # Thiết lập System Prompt / Instruction với Context và Cleaned Text
    cleanedText = StringHelpers.cleanText(issueText)
    systemPrompt = SYSTEM_PROMPT_ADVISOR.format(context_str=contextStr, user_message=cleanedText)
    
    # Cấu hình AI Model (Setup AI Model)
    genai.configure(api_key=apiKey)
    
    # Sử dụng model gemini-1.5-flash cho tác vụ xử lý văn bản
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=systemPrompt)
        response = model.generate_content(issueText)
        return response.text
    except Exception as e:
        # Bắt lỗi khi gọi API (Error handling)
        return f"Hệ thống định tuyến AI đang gặp trục trặc: {str(e)}"
