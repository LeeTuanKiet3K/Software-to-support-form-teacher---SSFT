def getErrorMessage(errorCode: str) -> str:
    """
    Chuyển đổi mã lỗi Firebase/Firestore sang thông báo tiếng Việt thân thiện.
    """
    m_errorMap = {
        "auth/user-not-found": "Không tìm thấy người dùng.",
        "auth/wrong-password": "Sai mật khẩu.",
        "auth/email-already-in-use": "Email đã được sử dụng.",
        "auth/email-already-exists": "Email đã tồn tại trong hệ thống.",
        "auth/invalid-email": "Email không hợp lệ.",
        "INVALID_LOGIN_CREDENTIALS": "Sai email hoặc mật khẩu!",
        "permission-denied": "Bạn không có quyền truy cập.",
        "not-found": "Không tìm thấy dữ liệu.",
        "unavailable": "Dịch vụ tạm thời không khả dụng."
    }
    return m_errorMap.get(errorCode, "Đã xảy ra lỗi không xác định.")
