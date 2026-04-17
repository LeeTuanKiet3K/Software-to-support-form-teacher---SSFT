import re

class StringHelpers:
    """
    Lớp xử lý văn bản (String Utility Class).
    Hỗ trợ chuẩn hóa dữ liệu đầu vào và đầu ra để giảm thiểu Hallucination của AI.
    """

    @staticmethod
    def cleanText(text: str) -> str:
        """
        Loại bỏ ký tự đặc biệt, chuẩn hóa văn bản (Text Normalization).
        Bảo vệ JSON payload không bị phá vỡ.
        
        Args:
            text (str): Văn bản gốc (Raw text).
            
        Returns:
            str: Văn bản đã được làm sạch (Cleaned text).
        """
        if not text:
            return ""
        # Giữ lại các chữ cái, số, khoảng trắng và các dấu câu cơ bản
        cleanedText = re.sub(r'[^\w\s\.,\?!\-]', '', text)
        # Loại bỏ khoảng trắng thừa (Remove extra spaces)
        cleanedText = re.sub(r'\s+', ' ', cleanedText).strip()
        return cleanedText

    @staticmethod
    def extractKeywords(text: str) -> str:
        """
        Trích xuất các từ khóa chính từ câu hỏi của sinh viên (Keyword Extraction).
        (Sẽ được gọi bởi Llama 3 trong module sau để Token Optimization).
        
        Args:
            text (str): Văn bản truy vấn (Query text).
            
        Returns:
            str: Chuỗi các từ khóa cốt lõi, cách nhau bởi khoảng trắng.
        """
        if not text:
            return ""
            
        # Cơ bản: Lọc stop words đơn giản có trong tiếng Việt (Stopword Filtering)
        stopWords = {"là", "của", "và", "những", "các", "có", "không", "ở", "vào", "ra", "thì", "mà", "bị", "bởi"}
        
        # Tiền xử lý: Viết thường, loại bỏ dấu câu (Preprocessing)
        textNoPunctuation = re.sub(r'[^\w\s]', '', text.lower())
        words = textNoPunctuation.split()
        
        keywords = [word for word in words if word not in stopWords and len(word) > 1]
        
        # Ghép lại thành một chuỗi (Serialized string)
        return " ".join(keywords)

    @staticmethod
    def formatResponse(text: str) -> str:
        """
        Định dạng lại văn bản (Text Formatting) để hiển thị chuyên nghiệp trên UI.
        
        Args:
            text (str): Văn bản phản hồi thô từ AI (Raw response).
            
        Returns:
            str: Văn bản đã được format cấu trúc chuẩn.
        """
        if not text:
            return ""
            
        # Chuẩn hóa khoảng trống (Normalize spacing)
        formattedText = text.replace('\n\n\n', '\n\n').strip()
        
        # Đảm bảo chữ cái đầu tiên luôn được viết hoa (Capitalize first letter)
        if len(formattedText) > 0:
            formattedText = formattedText[0].upper() + formattedText[1:]
            
        return formattedText
