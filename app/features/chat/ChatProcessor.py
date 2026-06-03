from groq import Groq
from app.services.FirestoreHandler import FirestoreHandler
from app.features.issue_manager.PriorityLogic import classifyAndPrioritize
from app.features.chat.PromptTemplates import SYSTEM_PROMPT_ADVISOR
from app.core.Constants import IssueStatus
from app.utils.StringHelpers import StringHelpers
from app.core.Config import AppConfig


def processStudentMessage(
    studentIdOrName: str,
    issueText: str,
    firestoreHandler: FirestoreHandler,
) -> tuple:
    """
    Xử lý tin nhắn của sinh viên theo luồng độc lập.
    Phân loại mức độ ưu tiên rồi chuyển tiếp cho GVCN hoặc tự động trả lời bằng Groq kết hợp tra cứu Cơ sở tri thức.

    Args:
        studentIdOrName (str): ID hoặc tên sinh viên.
        issueText (str): Nội dung tin nhắn gốc từ sinh viên.
        firestoreHandler (FirestoreHandler): Instance kết nối Firestore.

    Returns:
        tuple: (answer: str, metadata: dict) — câu trả lời và dữ liệu bổ trợ (references, ...).
    """
    # Step 1: Phân loại vấn đề và xác định mức độ ưu tiên 
    priorityResult = classifyAndPrioritize(issueText)

    # Step 2: Chuyển thẳng lên GVCN nếu vấn đề thuộc diện P0/P1 
    if priorityResult["isFallback"]:
        # Lưu vấn đề khẩn cấp vào collection Issues để GVCN theo dõi
        firestoreHandler.saveDocument("Issues", {
            "student_id": studentIdOrName,
            "issue_text": issueText,
            "priority": priorityResult["priorityLevel"],
            "status": IssueStatus.PENDING_ADVISOR
        })
        return (
            "Vấn đề của bạn đã được ghi nhận ở mức ưu tiên cao và chuyển đến trực tiếp GVCN. "
            "Thầy/cô sẽ liên hệ với bạn trong thời gian sớm nhất.",
            {},
        )

    # Step 3: Kiểm tra API Key trước khi khởi tạo Groq client 
    apiKey = AppConfig.GROQ_API_KEY
    if not apiKey:
        return "Hệ thống AI hiện đang bảo trì (Thiếu API Key). Vui lòng liên hệ trực tiếp GVCN.", {}

    # Khung ngữ cảnh tri thức sẽ được bổ sung từ Firestore
    contextStr = "Dưới đây là một số thông tin từ nhà trường:\n"
    # Metadata trả về cho frontend chứa danh sách tài liệu tham khảo (nếu có)
    responseMetadata = {"references": []}

    # Step 4: Extract keywords để tra cứu Firestore
    rawKeywords = StringHelpers.extractKeywords(issueText)
    if rawKeywords:
        # Chuẩn hóa về chữ thường và loại bỏ khoảng trắng thừa
        cleanKeywords = [k.strip().lower() for k in rawKeywords if k.strip()]
        print(f"\nKey words: {cleanKeywords} ---")

        if cleanKeywords:
            # Giới hạn 10 từ theo ràng buộc array_contains_any của Firestore 
            searchWords = cleanKeywords[:10]
            try:
                # Tìm kiếm tài liệu có chứa ít nhất 1 từ khóa trong collection 
                commonDataList = firestoreHandler.queryDocuments(
                    collectionName="Common_data",
                    filters=[("keywords", "array_contains_any", searchWords)],
                    limitCount=3,
                )

                # Nối nội dung tài liệu vào ngữ cảnh và thu thập URL tham khảo 
                for dataItem in commonDataList:
                    contentBody = dataItem.get("content", "")
                    sourceUrl = dataItem.get("source", "N/A")

                    if contentBody:
                        contextStr += f"- {contentBody}\n"
                        if sourceUrl and sourceUrl.strip() != "N/A":
                            responseMetadata["references"].append(sourceUrl.strip())

            except Exception as systemErr:
                print(f"Error querying Common_data: {systemErr}")

    # Lọc bỏ các URL trùng lặp trong danh sách tài liệu tham khảo
    responseMetadata["references"] = list(set(responseMetadata["references"]))

    # Step 5: Ghép ngữ cảnh tri thức vào System Prompt
    cleanedText = StringHelpers.cleanText(issueText)
    systemPrompt = SYSTEM_PROMPT_ADVISOR.format(context_str=contextStr, user_message=cleanedText)

    # Step 6: Khởi tạo Groq client per-request vì hàm này là stateless
    groqClient = Groq(api_key=apiKey)

    try:
        completionResponse = groqClient.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user",   "content": cleanedText},
            ],
            temperature=0.3,
            max_tokens=1024,
        )
        return completionResponse.choices[0].message.content, responseMetadata

    except Exception as generationErr:
        print(f"Content Generation Error: {generationErr}")
        return "Hệ thống định tuyến AI đang gặp trục trặc. Vui lòng thử lại sau.", {}