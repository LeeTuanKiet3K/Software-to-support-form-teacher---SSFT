def groupIssuesByStatus(issuesList: list) -> dict:
    """
    Thống kê số lượng vấn đề theo trạng thái để vẽ biểu đồ.
    Giả sử mỗi item trong issuesList là dict có key 'status'.
    """
    m_stats = {}
    for issue in issuesList:
        status = issue.get("status", "unknown")
        m_stats[status] = m_stats.get(status, 0) + 1
    return m_stats

def calculateAttendanceRate(total: int, absent: int) -> float:
    """
    Tính tỷ lệ chuyên cần.
    """
    if total <= 0:
        return 0.0
    attended = total - absent
    rate = (attended / total) * 100
    return round(rate, 2)

def getTopUrgentIssues(issuesList: list, limit: int = 5) -> list:
    """
    Lọc ra các vấn đề khẩn cấp nhất cho GVCN. 
    Giả sử thuộc tính priority = 'urgent'.
    """
    urgentIssues = [issue for issue in issuesList if issue.get("priority") == "urgent"]
    # Tuỳ chọn: sắp xếp theo mức độ mới nhất nếu có trường createdAt
    # urgentIssues.sort(key=lambda x: x.get("createdAt", 0), reverse=True)
    return urgentIssues[:limit]
