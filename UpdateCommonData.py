import os
import sys
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from groq import Groq
from app.services.FirestoreHandler import FirestoreHandler
from app.features.chat.PromptTemplates import PROMPT_KEYWORD_EXTRACTION
from app.core.Config import AppConfig


PROMPT_GENERATE_KEYWORDS = """
Bạn là bộ trích xuất từ khóa cho hệ thống tìm kiếm tri thức, từ nội dung tri thức sau, hãy sinh ra danh sách từ khóa để lưu vào Firestore.

YÊU CẦU:
- Trích xuất từ khóa và cụm từ khóa quan trọng nhất (là từ có nghĩa).
- Sửa lỗi chính tả nếu có.
- Giữ nguyên tên riêng, tên môn học, tên khoa, tên trường, tên phòng ban.
- Loại bỏ từ dư thừa như: tôi, em, mình, là, có, được, không, thế nào,...
- Trả về tối đa 10 từ khóa.
- Viết thường.
- Loại bỏ dấu câu thừa.
- Thêm với dạng viết tắt nếu có (ví dụ: "đại học khoa học tự nhiên" -> thêm "khtn", "đhkhtn").
- Không giải thích.
- Không đánh số.
- Không markdown.
- Chỉ trả về một dòng duy nhất.
- Các từ khóa phân cách bằng dấu phẩy.
Ví dụ: input: 'Trường đại học khoa học tự nhiên' => keywords: 'trường đại học, đại học khoa học tự nhiên, khoa học tự nhiên, khtn, dhkhtn'
"""


class UpdateCommonData:
    """
    Công cụ quản lý và cập nhật kho tri thức (Common_data) cho hệ thống AI.
    Phiên bản sử dụng Keyword Search truyền thống.
    """
    def __init__(self):
        self.m_dbHandler = FirestoreHandler()
        self.m_collectionName = "Common_data"
        groqKey = AppConfig.GROQ_DATAHELPER_API_KEY
        self.m_groqClient = Groq(api_key=groqKey) if groqKey else None

    def generateKeywordsFromContent(self, textContent: str) -> List[str]:
        """
        Dùng Groq để tự động sinh từ khóa từ nội dung theo đúng logic của PromptTemplates.
        """
        if not self.m_groqClient:
            print("   [!] Groq chưa được cấu hình — bỏ qua sinh keyword tự động.")
            return []

        prompt = PROMPT_GENERATE_KEYWORDS.format(content=textContent)
        try:
            response = self.m_groqClient.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=256,
            )
            raw = response.choices[0].message.content.strip()
            keywords = [k.strip().lower() for k in raw.split(",") if k.strip()]
            return keywords
        except Exception as e:
            print(f"   [!] Lỗi sinh keyword tự động: {e}")
            return []

    def addSingleDocument(self, sourceUrl: str, keywordsList: List[str], textContent: str) -> bool:
        """
        Thêm một tài liệu vào kho tri thức. doc_id luôn do Firestore tự tạo.
        """
        cleanKeywords = [k.lower() for k in keywordsList]

        dataPayload = {
            "source": sourceUrl,
            "keywords": cleanKeywords,
            "content": textContent
        }

        try:
            savedId = self.m_dbHandler.saveDocument(
                collectionName=self.m_collectionName,
                data=dataPayload,
            )
            print(f"Đã lưu thành công lên Firestore với ID: {savedId}\n")
            return True
        except Exception as e:
            print(f"Error saving document: {e}\n")
            return False


def interactiveUpload():
    """Hàm tương tác qua Terminal giúp nhập liệu liên tục."""
    updater = UpdateCommonData()
    print("="*60)
    print("CÔNG CỤ NHẬP LIỆU TRI THỨC (COMMON DATA) CHO AI")
    print("Mẹo: Nhập 'quit' ở bất kỳ bước nào để thoát chương trình.")
    print("="*60)

    uploadCount = 0
    while True:
        print(f"\n--- Đang nhập tài liệu thứ {uploadCount + 1} ---")

        sourceLink = input("1. Nhập URL nguồn tham khảo (Nhấn Enter để bỏ qua): ").strip()
        if sourceLink.lower() == 'quit': break
        if not sourceLink: sourceLink = "N/A"

        print("2. Nhập nội dung tri thức (nhấn Enter 2 lần liên tiếp để kết thúc):")
        lines = []
        while True:
            line = input()
            if line.lower() == 'quit':
                lines = ['quit']
                break
            if line == '' and lines and lines[-1] == '':
                break
            lines.append(line)
        mainContent = '\n'.join(lines).strip()
        if mainContent.lower() == 'quit': break
        if not mainContent:
            print("Nội dung không được để trống. Vui lòng nhập lại tài liệu này!")
            continue

        print("\n   Bạn muốn nhập keyword theo cách nào?")
        print("   [1] Tự động sinh bằng AI (khuyến nghị)")
        print("   [2] Nhập thủ công")
        keywordChoice = input("   Lựa chọn (1/2): ").strip()

        if keywordChoice == "1":
            print("   Đang sinh keyword tự động...")
            keywordArray = updater.generateKeywordsFromContent(mainContent)
            if keywordArray:
                print(f"   => Keyword sinh được: {keywordArray}")
                confirm = input("   Dùng danh sách này? (y/n): ").strip().lower()
                if confirm != 'y':
                    rawKeywords = input("   Nhập lại từ khóa, cách nhau bằng dấu phẩy: ").strip()
                    keywordArray = [k.strip() for k in rawKeywords.split(",") if k.strip()]
            else:
                print("   Sinh tự động thất bại, chuyển sang nhập thủ công.")
                rawKeywords = input("   Nhập từ khóa, cách nhau bằng dấu phẩy: ").strip()
                keywordArray = [k.strip() for k in rawKeywords.split(",") if k.strip()]
        else:
            rawKeywords = input("   Nhập từ khóa, cách nhau bằng dấu phẩy: ").strip()
            if rawKeywords.lower() == 'quit': break
            keywordArray = [k.strip() for k in rawKeywords.split(",") if k.strip()]

        print("Đang đẩy dữ liệu lên Firestore...")
        isSuccess = updater.addSingleDocument(sourceLink, keywordArray, mainContent)
        if isSuccess:
            uploadCount += 1

        shouldContinue = input("Bạn có muốn thêm tài liệu khác không? (y/n): ").strip().lower()
        if shouldContinue != 'y':
            break

    print(f"\nBạn đã thêm thành công {uploadCount} tài liệu vào hệ thống.")


if __name__ == "__main__":
    interactiveUpload()