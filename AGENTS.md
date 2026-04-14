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
* **Core Objective**: Xây dựng hệ thống hỗ trợ GVCN quản lý, tư vấn và phân loại vấn đề của sinh viên bằng AI để giảm tải khối lượng công việc cho Giáo viên chủ nhiệm, nâng cao hiệu suất của hoạt động chủ nhiệm lớp.
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


### 4. Specific Feature Instructions (Chỉ dẫn tính năng cụ thể)

#### A. Authentication (Đăng nhập)
* Phân loại Role (Vai trò) ngay từ bước đăng nhập để dẫn vào đúng Dashboard (Bảng điều khiển) tương ứng của Sinh viên hoặc GVCN.
* Sử dụng `ErrorCodes` từ `/core` để hiển thị thông báo lỗi tiếng Việt thân thiện khi đăng nhập thất bại (Ví dụ: "Sai mật khẩu" thay vì "auth/wrong-password").

#### B. AI Processor & Fallback (Xử lý AI và Chuyển tiếp)
* AI phải thực hiện **Sentiment Analysis** (Phân tích cảm xúc) và phân loại độ phức tạp của vấn đề.
* **Auto-reply**: Trả lời các câu hỏi về quy định, thủ tục dựa trên Knowledge Base.
* **Fallback Logic**: Với vấn đề nhạy cảm (Tâm lý, Cảm xúc, Khiếu nại), AI phải chuyển trạng thái sang "Pending Advisor" (Chờ GVCN xử lý) và tạo Notification (Thông báo) cho giáo viên.
* Tối ưu hóa Token bằng cách sử dụng `extractKeywords` từ `StringHelpers` trước khi gửi dữ liệu cho LLM.

#### C. Priority Algorithm (Thuật toán Ưu tiên)
* Tự động sắp xếp mức độ ưu tiên (Priority level) dựa trên:
    1. Loại vấn đề (Khẩn cấp > Nhạy cảm > Thông thường).
    2. Chỉ số cảm xúc (Càng lo lắng/tiêu cực thì ưu tiên càng cao).
    3. Thời gian thực gửi (Sử dụng `formatTimestamp` để đồng bộ dữ liệu hiển thị).

#### D. Analytics & Reporting (Phân tích & Báo cáo)
* **Teacher Insights**: Dashboard phải tập trung vào các chỉ số tình hình lớp học.
* **Data Processing**: Sử dụng `AnalyticsHelpers` để tự động tính toán tỷ lệ chuyên cần và gom nhóm trạng thái vấn đề (Pending/Resolved).
* **Urgent Monitoring**: Luôn hiển thị "Top Urgent Issues" ở vị trí ưu tiên cao nhất trên giao diện của GVCN.

#### E. Data Validation & Security (Kiểm soát & Bảo mật)
* **Input Integrity**: Tất cả dữ liệu đầu vào (MSSV, Email, Name) phải đi qua bộ lọc của `Validators` và `StringHelpers` trước khi tương tác với Firestore.
* **File Management**: Mọi tệp minh chứng tải lên (giấy phép, ảnh) phải được kiểm soát định dạng và dung lượng qua `FileHelpers` để bảo vệ tài nguyên Cloud Storage.
* **Search Optimization**: Hỗ trợ GVCN tìm kiếm tên sinh viên không dấu thông qua `removeVietnameseAccents` để tăng hiệu suất quản lý.

#### F. Teacher Support Tools (Công cụ hỗ trợ GVCN)
* **Password Support**: Cung cấp tính năng tạo mật khẩu tạm thời ngẫu nhiên qua `SecurityHelpers` khi sinh viên yêu cầu cấp lại tài khoản.
* **Friendly Interface**: Sử dụng `Formatters` để làm tròn điểm số GPA và tóm tắt nội dung vấn đề, giúp GVCN nắm bắt thông tin nhanh chóng mà không bị quá tải dữ liệu.


## 5. Workflow for Agents (Quy trình làm việc của AI)
1. **Plan Before Action**: Luôn tạo một **Plan Artifact** (Kế hoạch thực hiện) chi tiết trước khi tạo file hoặc viết code.
2. **Modular Implementation**: Triển khai từng module một. Đảm bảo cấu trúc file rõ ràng như đã thỏa thuận.
3. **Legacy Code Awareness (Quét code cũ):**
   - Trước khi triển khai một hàm (Function) hoặc tiện ích (Utility) mới, bắt buộc phải kiểm tra thư mục `/app/utils/` và `/app/services/`.
   - Nếu hàm đã tồn tại (Ví dụ: `generateTempPassword` trong `SecurityHelpers.py`), phải **Tái sử dụng (Reuse)** thay vì viết lại.
4. **Modular Extension (Mở rộng mô-đun):**
   - Nếu một file đã có sẵn (Ví dụ: `FirebaseAuthHandler.py`), hãy thêm hàm vào file đó thay vì tạo file mới có chức năng tương tự.
5. **Double Check**: Sau khi viết code, kiểm tra lại xem các chú thích tiếng Việt đã đầy đủ và dễ hiểu chưa.


## 6. Password & Security Policy (Chính sách Bảo mật & Mật khẩu)
Để đảm bảo an toàn dữ liệu sinh viên, mọi tính năng liên quan đến xác thực phải tuân thủ:
1. **Flexible Password Change (Đổi mật khẩu linh hoạt):**
   - Cờ `requires_password_change` vẫn được khởi tạo là `true` cho tài khoản mới.
   - **KHÔNG** chặn quyền truy cập (No Route Guard). Sinh viên vẫn sử dụng được hệ thống bình thường.
   - Hệ thống chỉ hiển thị thông báo nhắc nhở (Reminder/Toast) trên giao diện cho đến khi mật khẩu được đổi.
2. **Simplified Rules (Đơn giản hóa quy tắc):**
   - Quyền truy cập dữ liệu chỉ phụ thuộc vào việc đăng nhập và Vai trò (Role), không phụ thuộc vào trạng thái mật khẩu.
3. **Password Validation (Kiểm tra mật khẩu):**
   - Sử dụng `Validators.py` để kiểm tra mật khẩu mới: Tối thiểu 8 ký tự, bao gồm ít nhất 1 chữ hoa, 1 chữ thường và 1 ký số (Digit).
4. **Recovery Protocol (Giao thức khôi phục):**
   - Ưu tiên sử dụng **Firebase Password Reset Link** (Gửi link qua Email) để khôi phục mật khẩu. 
   - Hạn chế tự quản lý mã OTP thủ công để giảm thiểu rủi ro bảo mật và lưu trữ dư thừa.
5. **Audit Logging (Nhật ký bảo mật):**
   - Mọi hành động đổi mật khẩu hoặc yêu cầu reset phải được ghi nhận vào collection `AI_logs` hoặc một collection `Audit_logs` riêng biệt để truy vết.


## 7. Folder Structure (Cấu trúc thư mục tổng hợp)
/Software-to-support-form-teacher---SSFT  
├── /app  
│   ├── __init__.py  
│   ├── /core                (Cấu hình & Logic hệ thống)  
│   │   ├── Config.py        (Nạp .env & Remote Config để Bật/Tắt AI)  
│   │   ├── Constants.py     (Lưu Role, Trạng thái vấn đề, Mức độ ưu tiên)  
│   │   ├── ErrorCodes.py    (Xử lý mã lỗi từ Firebase sang Tiếng Việt)  
│   │   └── __init__.py  
│   ├── /features            (Tính năng nghiệp vụ)  
│   │   ├── /auth            (Tài khoản, Mật khẩu & Phân quyền)  
│   │   │   ├── AuthService.py  
│   │   │   └── PasswordService.py  (Xử lý đổi/quên mật khẩu)  
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
│   │   ├── DateHelpers.py      (Định dạng thời gian)  
│   │   ├── Validators.py       (Kiểm tra dữ liệu đầu vào)  
│   │   ├── Formatters.py       (Làm tròn điểm GPA, tóm tắt văn bản)  
│   │   ├── AnalyticsHelpers.py  (Tính tỷ lệ chuyên cần, lọc top vấn đề cho Dashboard)  
│   │   ├── FileHelpers.py       (Kiểm tra định dạng, dung lượng file minh chứng)  
│   │   ├── StringHelpers.py     (Chuyển tiếng Việt không dấu, tách từ khóa cho AI)  
│   │   └── SecurityHelpers.py   (Tạo mật khẩu tạm thời cho sinh viên)  
│   └── main.py              (Giao diện Streamlit chính)  
├── /data                    (Dữ liệu lưu trữ)  
│   ├── serviceAccountKey.json (Firebase Key)  
│   └── KnowledgeBase.json   (Dữ liệu keyword xác định)  
├── .env                     (Biến môi trường)  
├── .gitignore  
├── AGENTS.md  
├── SCHEMA.md                (Thiết kế cấu trúc dữ liệu)  
└── requirements.txt  