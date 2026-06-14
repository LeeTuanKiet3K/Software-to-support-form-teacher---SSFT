from datetime import datetime

def formatTimestamp(ts: any) -> str:
    """
    Chuyển đổi Firebase Timestamp hoặc UNIX timestamp sang "HH:MM - DD/MM/YYYY".
    """
    # Nếu ts là object của Firebase Firestore có phương thức to_datetime()
    if hasattr(ts, "to_datetime"):
        dt = ts.to_datetime()
    # Nếu là unix timestamp nguyên thủy
    elif isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(ts)
    elif isinstance(ts, datetime):
        dt = ts
    else:
        return ""
    
    return dt.strftime("%H:%M - %d/%m/%Y")

def getCurrentSemester() -> str:
    """
    Xác định học kỳ hiện tại dựa trên thời gian thực.
    HK1: Tháng 9 - 1
    HK2: Tháng 2 - 6
    HK Hè: Tháng 7 - 8
    """
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    
    if 8 <= currentMonth <= 12:
        return f"HK1 - {currentYear}-{currentYear+1}"
    elif 1 <= currentMonth <= 5:
        return f"HK2 - {currentYear-1}-{currentYear}"
    else:
        return f"HK Hè - {currentYear-1}-{currentYear}"

def calculateAge(birthdateStr: str) -> int:
    """
    Tính tuổi từ chuỗi ngày sinh (định dạng YYYY-MM-DD hoặc DD/MM/YYYY).
    """
    for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            birthdate = datetime.strptime(birthdateStr, date_format)
            today = datetime.now()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        except ValueError:
            continue
    return 0
