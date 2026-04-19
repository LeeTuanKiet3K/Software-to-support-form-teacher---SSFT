import os
import google.generativeai as genai
from app.services.FirestoreHandler import FirebaseHandler
from app.features.issue_manager.PriorityLogic import classifyAndPrioritize
from app.features.chat.PromptTemplates import SYSTEM_PROMPT_ADVISOR

def processStudentMessage(studentIdOrName: str, issueText: str, firebaseHandler: FirebaseHandler) -> str:
    """
    Xử lý tin nhắn của sinh viên: Phân loại mức độ ưu tiên và chuyển tiếp 
    hoặc sử dụng Gemini API để trả lời tự động dựa trên Cơ sở tri thức.
    
    Args:
        studentIdOrName (str): Định danh của sinh viên.
        issueText (str): Nội dung câu hỏi/vấn đề.
        firebaseHandler (FirebaseHandler): Đối tượng thao tác với database.
        
    Returns:
        str: Câu trả lời tự động hoặc thông báo chuyển tiếp.
    """
    # 1. Phân loại vấn đề (Classify and Prioritize)
    priorityResult = classifyAndPrioritize(issueText)
    
    # 2. Xử lý Fallback (Chuyển tiếp cho GVCN)
    if priorityResult["isFallback"]:
        # Lưu vấn đề vào Firestore (Save complex issue to Firestore)
        # Vì đây là P0 hoặc P1, chúng ta sẽ lưu với status là "Pending Advisor"
        firebaseHandler.saveIssue(
            studentIdOrName=studentIdOrName,
            issueText=issueText,
            priorityLevel=priorityResult["priorityLevel"],
            status="Pending Advisor"
        )
        # Trả về câu thông báo mặc định (Return fallback message)
        return "Vấn đề của bạn đã được ghi nhận ở mức ưu tiên cao và chuyển đến trực tiếp GVCN. Thầy/cô sẽ liên hệ với bạn trong thời gian sớm nhất."
        
    # 3. Sử dụng AI để trả lời (Normal P2 issues)
    # Lấy API Key từ môi trường (Fetch API Key)
    apiKey = os.getenv("GEMINI_API_KEY")
    if not apiKey:
        return "Hệ thống AI hiện đang bảo trì (Thiếu API Key). Vui lòng liên hệ trực tiếp GVCN."
        
    # Lấy cơ sở tri thức để làm Grounding/Context (Fetch context)
    kbDataList = firebaseHandler.getKnowledgeBase()
    
    # Nối tất cả các kiến thức thành chuỗi context (Build context string)
    contextStr = "Dưới đây là một số thông tin quy định từ nhà trường:\n"
    for kb in kbDataList:
        title = kb.get("title", "")
        content = kb.get("content", "")
        if title and content:
            contextStr += f"- {title}: {content}\n"
            
    # Thiết lập System Prompt / Instruction
    systemPrompt = SYSTEM_PROMPT_ADVISOR.format(context_str=contextStr)
    
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
