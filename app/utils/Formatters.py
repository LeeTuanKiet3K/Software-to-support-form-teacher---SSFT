def formatGpa(score: float) -> str:
    """
    Làm tròn điểm số GPA tới 2 chữ số thập phân.
    """
    return f"{score:.2f}"

def summarizeText(text: str, limit: int = 100) -> str:
    """
    Cắt ngắn văn bản để hiển thị trên Dashboard.
    """
    if len(text) <= limit:
        return text
    return text[:limit] + "..."
