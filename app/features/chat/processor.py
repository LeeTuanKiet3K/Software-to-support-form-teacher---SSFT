import os
import google.generativeai as genai
from app.services.firebase_handler import FirebaseHandler
from app.features.issue_manager.priority import classify_and_prioritize

def process_student_message(student_id_or_name: str, issue_text: str, firebase_handler: FirebaseHandler) -> str:
    """
    Xử lý tin nhắn của sinh viên: Phân loại mức độ ưu tiên và chuyển tiếp 
    hoặc sử dụng Gemini API để trả lời tự động dựa trên Cơ sở tri thức.
    
    Args:
        student_id_or_name (str): Định danh của sinh viên.
        issue_text (str): Nội dung câu hỏi/vấn đề.
        firebase_handler (FirebaseHandler): Đối tượng thao tác với database.
        
    Returns:
        str: Câu trả lời tự động hoặc thông báo chuyển tiếp.
    """
    # 1. Phân loại vấn đề (Classify and Prioritize)
    priority_result = classify_and_prioritize(issue_text)
    
    # 2. Xử lý Fallback (Chuyển tiếp cho GVCN)
    if priority_result["is_fallback"]:
        # Lưu vấn đề vào Firestore (Save complex issue to Firestore)
        # Vì đây là P0 hoặc P1, chúng ta sẽ lưu với status là "Pending Advisor"
        firebase_handler.save_issue(
            student_id_or_name=student_id_or_name,
            issue_text=issue_text,
            priority_level=priority_result["priority_level"],
            status="Pending Advisor"
        )
        # Trả về câu thông báo mặc định (Return fallback message)
        return "Vấn đề của bạn đã được ghi nhận ở mức ưu tiên cao và chuyển đến trực tiếp GVCN. Thầy/cô sẽ liên hệ với bạn trong thời gian sớm nhất."
        
    # 3. Sử dụng AI để trả lời (Normal P2 issues)
    # Lấy API Key từ môi trường (Fetch API Key)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Hệ thống AI hiện đang bảo trì (Thiếu API Key). Vui lòng liên hệ trực tiếp GVCN."
        
    # Lấy cơ sở tri thức để làm Grounding/Context (Fetch context)
    kb_data_list = firebase_handler.get_knowledge_base()
    
    # Nối tất cả các kiến thức thành chuỗi context (Build context string)
    context_str = "Dưới đây là một số thông tin quy định từ nhà trường:\n"
    for kb in kb_data_list:
        title = kb.get("title", "")
        content = kb.get("content", "")
        if title and content:
            context_str += f"- {title}: {content}\n"
            
    # Thiết lập System Prompt / Instruction
    system_prompt = (
        "Bạn là một trợ lý AI hỗ trợ Giáo viên chủ nhiệm (GVCN) trả lời các câu hỏi thủ tục, quy chế cho sinh viên. "
        "Hãy luôn trả lời một cách thân thiện, chính xác và chuyên nghiệp. "
        "Chỉ sử dụng những thông tin được cung cấp trong Cơ sở tri thức dưới đây để trả lời.\n\n"
        f"Cơ sở tri thức (Knowledge Base):\n{context_str}\n\n"
        "Nếu sinh viên hỏi thông tin nằm ngoài cơ sở tri thức này, hãy đáp lại: "
        "'Xin lỗi, trợ lý hiện chưa có thông tin về vấn đề này. Bạn vui lòng liên hệ GVCN trực tiếp nhé.'\n"
    )
    
    # Cấu hình AI Model (Setup AI Model)
    genai.configure(api_key=api_key)
    
    # Sử dụng model gemini-1.5-flash cho tác vụ xử lý văn bản
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        response = model.generate_content(issue_text)
        return response.text
    except Exception as e:
        # Bắt lỗi khi gọi API (Error handling)
        return f"Hệ thống định tuyến AI đang gặp trục trặc: {str(e)}"
