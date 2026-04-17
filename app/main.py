import sys
import os

# Tự động cấu hình đường dẫn root của dự án để tránh lỗi "No module named 'app'"
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import traceback

from app.core.Constants import UserRole, IssueStatus
from app.services.FirebaseAuthHandler import FirebaseAuthHandler
from app.core.Middleware import Middleware
from app.features.chat.ResponseAggregator import ResponseAggregator
from app.services.IssueService import IssueService

# --- TRẠNG THÁI HỆ THỐNG (STATE MANAGEMENT) ---
def initializeState():
    """Khởi tạo trạng thái phiên làm việc (Session Variables Init)."""
    if 'm_isLoggedIn' not in st.session_state:
        st.session_state.m_isLoggedIn = False
    if 'm_currentUserData' not in st.session_state:
        st.session_state.m_currentUserData = None
    if 'm_chatId' not in st.session_state:
        st.session_state.m_chatId = None
    if 'm_interfaceHistory' not in st.session_state:
        st.session_state.m_interfaceHistory = []
    
    # Khởi tạo các Instances dịch vụ (Service singletons)
    if 'm_authHandler' not in st.session_state:
        st.session_state.m_authHandler = FirebaseAuthHandler()
    if 'm_middleware' not in st.session_state:
        st.session_state.m_middleware = Middleware()
    if 'm_aggregator' not in st.session_state:
        st.session_state.m_aggregator = ResponseAggregator()
    if 'm_issueService' not in st.session_state:
        st.session_state.m_issueService = IssueService()

# --- MODULE: XÁC THỰC (AUTHENTICATION UI) ---
def renderLoginWindow():
    """Hiển thị Giao diện Xác thực (Authentication View)."""
    st.title("🎓 SSFT: AI Trợ lý Cố Vấn Học Tập")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("Vui lòng đăng nhập hệ thống (System Sign In)")
        with st.form("loginForm"):
            email = st.text_input("Địa chỉ Email (Email)")
            password = st.text_input("Mật khẩu (Password)", type="password")
            submitBtn = st.form_submit_button("Tiếp tục (Continue)", use_container_width=True)
            
            if submitBtn:
                if not email or not password:
                    st.warning("Thông tin chưa đầy đủ (Missing credentials).")
                    return
                    
                with st.spinner("Đang mã hóa & xác thực (Authenticating...)"):
                    authResult = st.session_state.m_authHandler.signIn(email, password)
                    if authResult.get("success"):
                        # Trích xuất payload xác thực (Extract Auth Payload)
                        tokenData = authResult.get("data")
                        idToken = tokenData.get("idToken")
                        
                        # Giải mã JWT để móc nối thông tin (Decode JWT Info)
                        userObj = st.session_state.m_authHandler.getCurrentUser(idToken)
                        
                        if userObj:
                            st.session_state.m_isLoggedIn = True
                            st.session_state.m_currentUserData = userObj
                            
                            # Cấu hình Role giả lập qua email do Auth Firebase chưa set custom claim
                            # Tính năng này hoạt động tốt với Workflow (Role mapping step)
                            emailLower = email.lower()
                            if "advisor" in emailLower or "gv" in emailLower:
                                st.session_state.m_currentUserData['role'] = UserRole.ADVISOR
                            else:
                                st.session_state.m_currentUserData['role'] = UserRole.STUDENT
                                
                            # Thiết lập mã trò chuyện theo UID hoặc email (Session Tracking)
                            st.session_state.m_chatId = userObj.get('uid', email)
                            st.rerun()
                        else:
                            st.error("Khóa ký bảo mật không chính xác (Token Expired).")
                    else:
                        st.error(authResult.get("error"))

# --- MODULE: CHAT AI (CONVERSATIONAL INTERFACE) ---
def renderChatWindow():
    """Giao diện Cửa sổ Trò chuyện Học sinh & Cố vấn (Chat Interface)."""
    st.header("💬 Khu vực Trợ lý Thông minh (AI Companion)")
    st.info("Trợ lý có thể dẫn đường bạn qua các thủ tục, giải đáp thắc mắc, hoặc gửi cảnh báo lên GVCN.")
    
    # Lịch sử hiển thị UI (UI State Loop)
    for msg in st.session_state.m_interfaceHistory:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "actions" in msg and msg["actions"]:
                st.caption(f"🚀 **Thao tác nhanh:** {', '.join(msg['actions'])}")

    # Nhận hiệu lệnh mới (Input listener)
    userInput = st.chat_input("Gõ vấn đề bạn quan tâm (Ví dụ: Form điểm danh)...")
    if userInput:
        # Cập nhật hiển thị lập tức (Echo signal)
        st.session_state.m_interfaceHistory.append({"role": "user", "content": userInput})
        with st.chat_message("user"):
            st.markdown(userInput)
            
        # Kích hoạt xương sống Hybrid AI (Activate AI Backbone)
        with st.chat_message("assistant"):
            with st.spinner("AI đang tính toán dữ liệu (Processing RAG)..."):
                try:
                    middleware = st.session_state.m_middleware
                    aggregator = st.session_state.m_aggregator
                    issueSvc = st.session_state.m_issueService
                    chatId = st.session_state.m_chatId
                    userId = st.session_state.m_currentUserData.get("email")
                    
                    # 1. Quét cảm xúc để đề phòng nguy ngập (Risk Analysis via Llama)
                    analysisParams = middleware.callLocalLlama(userInput)
                    
                    # 2. Sinh Ticket quản lý cho Giáo viên nếu có URGENT/HIGH (Automatic Escalation)
                    issueSvc.createIssueFromChat(chatId, userId, analysisParams)
                    
                    # 3. Chạy quá trình truy vấn đám mây (Cloud Orchestration)
                    rawAnswer = middleware.coordinateFlow(studentMessage=userInput, chatId=chatId)
                    
                    # 4. Gắn thêm Action Button ảo và Markdown References (Response Aggregation)
                    finalAnswer = aggregator.formatFinalResponse(rawAnswer)
                    quickActTags = aggregator.generateQuickActions(analysisParams.get("intent"))
                    
                    # In thực tế vào Bong bóng (Render Blob)
                    st.markdown(finalAnswer)
                    if quickActTags:
                        st.caption(f"🚀 **Đề xuất truy cập:** {', '.join(quickActTags)}")
                    
                    # Giữ bản sao màn hình (Save Render State)
                    st.session_state.m_interfaceHistory.append({
                        "role": "assistant", 
                        "content": finalAnswer,
                        "actions": quickActTags
                    })
                    
                except Exception as sysErr:
                    st.error("Cổng nối suy luận đang ngập tải. Bạn chờ một lát rồi kết nối lại nhé!")
                    st.write(f"Vết chẩn đoán kỹ thuật (Traceback): {sysErr}")

# --- MODULE: BẢNG THEO DÕI NÂNG CAO (ADVISOR DASHBOARD) ---
def renderAdvisorDashboard():
    """Giao diện Quản trị của Giáo Viên (Advisor Issue Tracker)."""
    st.header("📊 Bộ theo dõi Vấn đề Khẩn (Issue Tracker)")
    
    # Truy xuất dữ liệu thời gian chìm (Fetch Backend Tasks)
    pendingTasks = st.session_state.m_issueService.getPendingIssues()
    
    if not pendingTasks:
        st.success("Tuyệt vời! Không phát hiện lỗ hổng hay vấn đề khẩn cấp nào (No pending issues).")
        return
        
    st.write(f"Máy dò thấy **{len(pendingTasks)}** báo động cần duyệt.")
    
    # Hiển thị lặp Ticket dưới dạng Cards (Card Iteration)
    for idx, ticket in enumerate(pendingTasks):
        tId = ticket.get("issue_id", f"UNKNOWN-{idx}")
        lvl = ticket.get("priority", "N/A")
        emotion = ticket.get("sentiment", "N/A")
        statusFlag = ticket.get("status", IssueStatus.OPEN)
        studentStr = ticket.get("student_id", "Ẩn danh")
        sessionKey = ticket.get("chat_id")
        
        # Nhãn hiệu HTML/màu sắc (Color Metrics)
        colorMap = {"URGENT": "red", "HIGH": "orange", "MEDIUM": "blue", "LOW": "green"}
        badgeColor = colorMap.get(lvl, "gray")
        
        with st.expander(f"🛑 [Mức: {lvl}] Tín hiệu từ: {studentStr} | Trạng thái: {statusFlag}"):
            st.markdown(f"**Gắn cờ sự cố (Priority):** :{badgeColor}[{lvl}]")
            st.markdown(f"**Trạng thái tâm sinh lý (Emotion Profile):** {emotion}")
            
            # Khởi động dịch vụ giải mã tóm tắt bí mật (Call Context Summarizer)
            aggregatorObj = st.session_state.m_aggregator
            secretIntel = aggregatorObj.createSummaryForAdvisor(sessionKey)
            
            st.info(f"**AI Tóm lược cốt lõi (Core Intel):** {secretIntel.get('secret_summary')}")
            
            # Hệ nút quản trị (Resolution Workflow Button)
            if statusFlag != IssueStatus.RESOLVED:
                if st.button("Ngắt báo động / Bấm Đã Xử Lý (Resolve Ticket)", key=f"btn_res_{tId}"):
                    updateCheck = st.session_state.m_issueService.updateIssueStatus(tId, IssueStatus.RESOLVED)
                    if updateCheck:
                        st.success("Tín hiệu đã được xử lý (Trigger Cleared). File sẽ nạp lại.")
                        st.rerun()
                    else:
                        st.error("Báo lỗi kết nối CSDL (DB Push Fail).")

# --- HÀM MAIN: TẬP TRUNG KHUNG LEO (FRONTEND MOUNTS) ---
def main():
    """Gốc kết xuất màn hình hệ thống (Core Mount Context)."""
    st.set_page_config(page_title="AI: Cố vấn thông minh SSFT", page_icon="🎓", layout="wide")
    initializeState()
    
    if not st.session_state.m_isLoggedIn:
        renderLoginWindow()
    else:
        userRole = st.session_state.m_currentUserData.get('role', UserRole.STUDENT)
        uid = st.session_state.m_currentUserData.get('uid', 'System')
        
        # Thanh bên phân bổ chức năng (Navigation Sidebar)
        with st.sidebar:
            st.subheader(f"Xin chào, {st.session_state.m_currentUserData.get('email')}")
            st.caption(f"Chức vụ truy cập (Role Profile): {userRole}")
            st.markdown("---")
            
            # Nút tắt phiên (Sign out killswitch)
            if st.button("Thoát (Sign Out)", use_container_width=True):
                st.session_state.m_authHandler.signOut(uid)
                st.session_state.clear()
                st.rerun()
        
        # Định hình View dựa theo Phân quyền Role (Role Layout Dispatcher)
        if userRole == UserRole.ADVISOR:
            tabStats, tabConvo = st.tabs(["🚦 Dashboard (Trạm QL)", "💬 Trợ lý Bot (Convo)"])
            with tabStats:
                renderAdvisorDashboard()
            with tabConvo:
                renderChatWindow()
        else:
            renderChatWindow()

if __name__ == "__main__":
    main()
