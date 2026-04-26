import sys
import os
# Đưa thư mục gốc (chứa thư mục app) vào đường dẫn ưu tiên để Python hiểu 'app' là một module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from streamlit_chat import message
from app.services.FirestoreHandler import FirestoreHandler
from app.features.chat.ChatProcessor import processStudentMessage
from app.services.RealtimeHandler import RealtimeHandler

# Khởi tạo đối tượng Firebase Handler (Singleton context giả lập)
@st.cache_resource
def getFirebaseHandler():
    return FirebaseHandler()

@st.cache_resource
def initRealtime():
    handler = RealtimeHandler()
    handler.listenAcademicRecords()
    return handler

firebaseHandler = FirestoreHandler()

# Cấu hình cài đặt trang web mặc định (Page configuration)
st.set_page_config(page_title="Hệ thống Hỗ trợ GVCN", page_icon="🎓", layout="wide")

# Khởi tạo các biến trong Session State nếu chưa có
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
# Lưu trữ lịch sử chat tạm thời trong phiên (Temporary chat history)
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

def loginScreen():
    """
    Giao diện màn hình đăng nhập.
    """
    st.title("🎓 Cổng thông tin Hỗ trợ Giáo viên Chủ nhiệm")
    st.subheader("Đăng nhập hệ thống (Login)")
    
    with st.form(key="login_form"):
        email = st.text_input("Email", placeholder="Ví dụ: student@school.edu.vn")
        password = st.text_input("Mật khẩu", type="password")
        submitButton = st.form_submit_button(label="Đăng nhập")
        
    if submitButton:
        if email and password:
            role = firebaseHandler.verifyLogin(email, password)
            if role:
                st.session_state['user_role'] = role
                st.session_state['username'] = email.split("@")[0]
                st.success("Đăng nhập thành công! Đang chuyển hướng...")
                st.rerun()
            else:
                st.error("Email hoặc Mật khẩu không chính xác.")
        else:
            st.warning("Vui lòng nhập đầy đủ thông tin.")

def studentChatInterface():
    """
    Giao diện Chat dành cho Sinh viên (Student View).
    """
    st.title(f"Chào mừng {st.session_state['username']}! 👋")
    st.caption("AI Assistant sẵn sàng hỗ trợ các vấn đề thủ tục, quy chế và tư vấn tâm lý.")
    
    # Nút Đăng xuất
    if st.sidebar.button("Đăng xuất (Logout)"):
         st.session_state['user_role'] = None
         st.session_state['messages'] = []
         st.rerun()
         
    # Container lưu giữ và hiển thị lịch sử đoạn chat
    chatContainer = st.container()
    
    # Input field cho User
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 1])
        with col1:
            userInput = st.text_input("Bạn đang gặp vấn đề gì?", label_visibility="collapsed")
        with col2:
            submitBtn = st.form_submit_button("Gửi 🚀")
            
    if submitBtn and userInput:
        # 1. Thêm câu hỏi của user vào danh sách
        st.session_state['messages'].append({"content": userInput, "is_user": True})
        
        # 2. Xử lý qua Chat Processor
        with st.spinner("AI đang xử lý..."):
            aiResponse = processStudentMessage(
                studentIdOrName=st.session_state['username'],
                issueText=userInput,
                firebaseHandler=firebaseHandler
            )
            
        # 3. Thêm phản hồi của AI vào danh sách
        st.session_state['messages'].append({"content": aiResponse, "is_user": False})
        
        # Reload để hiển thị tin nhắn mới ngay lập tức
        st.rerun()
        
    # Render các tin nhắn trong container (Từ cũ đến mới)
    with chatContainer:
        if not st.session_state['messages']:
            st.info("Bắt đầu cuộc trò chuyện bằng cách nhập câu hỏi ở bên dưới.")
            
        for i, msg in enumerate(st.session_state['messages']):
            # Hàm message() của streamlit_chat sẽ tạo ra giao diện bong bóng thoại
            message(msg["content"], is_user=msg["is_user"], key=f"msg_{i}")

def advisorDashboardInterface():
    """
    Bảng điều khiển (Dashboard) dành cho GVCN.
    Hiển thị các issues cần xử lý, sắp xếp theo mức độ ưu tiên.
    """
    st.title(f"Bảng điều khiển GVCN (Advisor Dashboard) - {st.session_state['username']}")
    
    if st.sidebar.button("Đăng xuất (Logout)"):
         st.session_state['user_role'] = None
         st.rerun()
         
    st.header("📋 Danh sách các vấn đề sinh viên cần xử lý")
    
    with st.spinner("Đang tải dữ liệu từ cơ sở dữ liệu (Fetching data)..."):
        issues = firebaseHandler.getIssues()
        
    if not issues:
        st.success("Tuyệt vời! Hiện tại không có vấn đề nào cần giải quyết.")
    else:
        # Render từng issue thành các thẻ hiển thị (Expanders)
        for issue in issues:
            priority = issue.get("priority_level", "P2")
            student = issue.get("student", "Unknown")
            status = issue.get("status", "Pending")
            text = issue.get("issue_text", "")
            
            # Tùy chỉnh màu sắc tiêu đề dựa trên độ ưu tiên (Visual cues)
            if priority == "P0":
                header = f"🚨 [P0 - KHẨN CẤP] {student}"
            elif priority == "P1":
                header = f"⚠️ [P1 - KHIẾU NẠI] {student}"
            else:
                header = f"ℹ️ [P2 - THÔNG THƯỜNG] {student}"
                
            with st.expander(header, expanded=(priority == "P0")):
                st.markdown(f"**Trạng thái:** `{status}`")
                st.markdown(f"**Nội dung chi tiết:**")
                st.info(text)
                
                # Nút mô phỏng Mark as resolved (chức năng này có thể phát triển sau)
                if st.button("Đánh dấu đã xử lý", key=f"resolve_{issue.get('issue_id')}"):
                    st.toast(f"Tính năng chưa được liên kết DB: Trạng thái của ticket {issue.get('issue_id')} được đổi trên local.", icon="👌")
                    # (To-Do: Tích hợp hàm cập nhật firebase_handler.resolve_issue() tại đây)

def main():
    initRealtime()
    """
    Luồng điều hướng cốt lõi (Main routing flow)
    """
    role = st.session_state['user_role']
    
    if role is None:
        loginScreen()
    elif role == "student":
        studentChatInterface()
    elif role == "advisor":
        advisorDashboardInterface()
    else:
        st.error("Phân quyền không hợp lệ. Vui lòng thử lại.")
        st.session_state['user_role'] = None

if __name__ == '__main__':
    main()
