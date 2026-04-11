# AGENTS.md - Project Instructions for GVCN Support System

## 0. Naming Conventions (Quy ước đặt tên)

Để đảm bảo tính đồng bộ cho toàn bộ source code, Agent phải tuân thủ các quy tắc sau:

1. **Classes (Lớp):** Sử dụng **PascalCase**.
   - *Ví dụ:* `FirebaseHandler`, `IssueManager`, `UserSession`.
2. **Variables & Functions (Biến & Hàm):** Sử dụng **camelCase**.
   - *Ví dụ:* `studentName`, `getStudentData()`, `calculatePriority()`.
3. **Private Members (Thành phần nội bộ):** Thêm tiền tố **m_** trước tên biến.
   - *Ví dụ:* `m_dbClient`, `m_apiKey`.
4. **Getters & Setters:** Sử dụng tiền tố **get** và **set**.
   - *Ví dụ:* `getRole()`, `setStatus()`.
5. **Constants (Hằng số):** Sử dụng **UPPER_CASE** với dấu gạch nối.
   - *Ví dụ:* `MAX_RETRY_ATTEMPTS`, `FIREBASE_TIMEOUT`.

*Lưu ý: Luôn ưu tiên dùng tiếng Anh cho tên biến/hàm và kèm chú thích tiếng Việt bên cạnh các thuật ngữ IT.*

## 1. Project Context (Bối cảnh Đồ án)
* **Project Name**: Phần mềm hỗ trợ Giáo viên chủ nhiệm (GVCN).
* **Core Objective**: Xây dựng hệ thống hỗ trợ GVCN quản lý, tư vấn và phân loại vấn đề của sinh viên bằng AI để giảm tải khối lượng công việc (Workload reduction).
* **Target Users**: Sinh viên (Student) và Giáo viên chủ nhiệm (Class Advisor).

## 2. Technical Stack (Công nghệ sử dụng)
* **Backend Language**: Python 3.10+.
* **Database**: Firebase (Firestore) dùng làm Knowledge Base (Cơ sở tri thức) để đảm bảo tính chính xác và tránh Hallucination (AI bịa đặt). Sử dụng Firestore Realtime Listeners để cập nhật danh sách vấn đề của sinh viên ngay khi có dữ liệu mới. Ưu tiên tối ưu hóa số lượng truy vấn (Read operations) để tránh vượt quá định mức của Firebase Free Tier.
* **Framework**: Ưu tiên các thư viện Python hiện đại để xử lý logic và kết nối Firebase (firebase-admin).

## 3. Architecture & Style Rules (Quy tắc Kiến trúc và Phong cách)
* **Feature-based Structure**: Mỗi tính năng lớn phải nằm trong một folder riêng biệt tại `/app/features/`. Tuyệt đối không gộp nhiều tính năng vào một file đơn lẻ.
* **Coding Style**: Tuân thủ nghiêm ngặt chuẩn **PEP 8**. Sử dụng **Type Hinting** (Gợi ý kiểu dữ liệu) cho tất cả các function (hàm).
* **Language Policy**: 
    * Giữ nguyên các **Technical terms** (Thuật ngữ chuyên ngành) bằng tiếng Anh.
    * Phải có chú thích (Comments) bằng tiếng Việt ngay bên cạnh hoặc phía trên các thuật ngữ/logic phức tạp.
    * Ví dụ: `def authenticate_user():  # Xác thực người dùng`.

## 4. Specific Feature Instructions (Chỉ dẫn tính năng cụ thể)

### A. Authentication (Đăng nhập)
* Phân loại Role (Vai trò) ngay từ bước đăng nhập để dẫn vào đúng Dashboard (Bảng điều khiển) tương ứng của Sinh viên hoặc GVCN.

### B. AI Processor & Fallback (Xử lý AI và Chuyển tiếp)
* AI phải thực hiện **Sentiment Analysis** (Phân tích cảm xúc) và phân loại độ phức tạp của vấn đề.
* **Auto-reply**: Trả lời các câu hỏi về quy định, thủ tục dựa trên Knowledge Base.
* **Fallback Logic**: Với vấn đề nhạy cảm (Tâm lý, Cảm xúc, Khiếu nại), AI phải chuyển trạng thái sang "Pending Advisor" (Chờ GVCN xử lý) và tạo Notification (Thông báo) cho giáo viên.

### C. Priority Algorithm (Thuật toán Ưu tiên)
* Tự động sắp xếp mức độ ưu tiên (Priority level) dựa trên:
    1. Loại vấn đề (Khẩn cấp > Nhạy cảm > Thông thường).
    2. Chỉ số cảm xúc (Càng lo lắng/tiêu cực thì ưu tiên càng cao).
    3. Thời gian thực gửi.

## 5. Workflow for Agents (Quy trình làm việc của AI)
1. **Plan Before Action**: Luôn tạo một **Plan Artifact** (Kế hoạch thực hiện) chi tiết trước khi tạo file hoặc viết code.
2. **Modular Implementation**: Triển khai từng module một. Đảm bảo cấu trúc file rõ ràng như đã thỏa thuận.
3. **Double Check**: Sau khi viết code, kiểm tra lại xem các chú thích tiếng Việt đã đầy đủ và dễ hiểu chưa.

## 6. Folder Structure (Cấu trúc thư mục tổng hợp)
/Software-to-support-form-teacher---SSFT  
├── /app  
│   ├── __init__.py  
│   ├── /core                (Cấu hình & Logic hệ thống)  
│   │   ├── Config.py        (Nạp .env & Remote Config để Bật/Tắt AI)  
│   │   ├── Constants.py     (Lưu Role, Trạng thái vấn đề, Mức độ ưu tiên)  
│   │   └── __init__.py  
│   ├── /features            (Tính năng nghiệp vụ)  
│   │   ├── /auth            (Tài khoản, Mật khẩu & Phân quyền)  
│   │   │   ├── AuthService.py  
│   │   │   └── UserModels.py  
│   │   ├── /chat            (AI Tư vấn & Tin nhắn trực tiếp)  
│   │   │   ├── ChatProcessor.py  
│   │   │   └── PromptTemplates.py  
│   │   ├── /issue_manager   (Quản lý vấn đề từ SV/AI gửi tới)  
│   │   │   ├── IssueService.py  
│   │   │   └── PriorityLogic.py (Thuật toán sắp xếp vấn đề)  
│   │   ├── /academic        (Quản lý Điểm số & Thông tin SV)  
│   │   │   ├── AcademicService.py  (Xử lý các logic chính)  
│   │   │   └── GradeModels.py  (Định nghĩa cấu trúc dữ liệu hoặc các Class)  
│   │   ├── /notifications   (Thông báo & Phản hồi từ GVCN)  
│   │   │   ├── NotificationService.py  
│   │   │   └── AnnouncementUI.py  
│   │   └── /analytics       (Dashboard GVCN & Đánh giá lớp)  
│   │       └── AdvisorDashboard.py  
│   ├── /services            (Kết nối Database/Cloud)  
│   │   ├── __init__.py  
│   │   ├── FirestoreHandler.py  (Lưu SV, Điểm, Tin nhắn)  
│   │   ├── StorageHandler.py    (Lưu Ảnh minh chứng, Avatar)  
│   │   ├── RealtimeHandler.py   (Trạng thái Chat trực tiếp)  
│   │   └── FirebaseAuthHandler.py (Xử lý Auth)  
│   ├── /utils               (Tiện ích dùng chung)  
│   │   ├── __init__.py  
│   │   ├── DateHelpers.py   (Định dạng thời gian)  
│   │   └── Validators.py    (Kiểm tra dữ liệu đầu vào)  
│   └── main.py              (Giao diện Streamlit chính)  
├── /data                    (Dữ liệu lưu trữ)  
│   ├── serviceAccountKey.json (Firebase Key)  
│   └── KnowledgeBase.json   (Dữ liệu keyword xác định)  
├── .env                     (Biến môi trường)  
├── .gitignore  
├── AGENTS.md  
├── SCHEMA.md                (Thiết kế cấu trúc dữ liệu)  
└── requirements.txt  