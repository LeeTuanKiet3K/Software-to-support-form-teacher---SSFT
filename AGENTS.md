# AGENTS.md - Project Instructions for GVCN Support System

## 1. Naming Conventions (Quy ước đặt tên)

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


## 2. Workflow for Agents (Quy trình làm việc của AI)
1. **Plan Before Action**: Luôn tạo một **Plan Artifact** (Kế hoạch thực hiện) chi tiết trước khi tạo file hoặc viết code.
2. **Modular Implementation**: Triển khai từng module một. Đảm bảo cấu trúc file rõ ràng như đã thỏa thuận.
3. **Legacy Code Awareness (Quét code cũ):**
   - Trước khi triển khai một hàm (Function) hoặc tiện ích (Utility) mới, bắt buộc phải kiểm tra thư mục `/app/utils/` và `/app/services/`.
   - Nếu hàm đã tồn tại (Ví dụ: `generateTempPassword` trong `SecurityHelpers.py`), phải **Tái sử dụng (Reuse)** thay vì viết lại.
4. **Modular Extension (Mở rộng mô-đun):**
   - Nếu một file đã có sẵn (Ví dụ: `FirebaseAuthHandler.py`), hãy thêm hàm vào file đó thay vì tạo file mới có chức năng tương tự.
5. **Double Check**: Sau khi viết code, kiểm tra lại xem các chú thích tiếng Việt đã đầy đủ và dễ hiểu chưa.


## 3. Environment Variables (.env)
Để hệ thống khởi chạy an toàn không rò rỉ bảo mật và không gặp lỗi kết nối, phải kiểm soát cấu hình gốc thông qua file `.env`. Cần liệt kê hoặc tạo `.env.example` với các key thiết yếu:
* `FIREBASE_SERVICE_ACCOUNT_JSON`: Nơi lưu file `serviceAccountKey.json`.
* `FIREBASE_WEB_API_KEY`: API key cho Firebase Identity Toolkit REST login.
* `GEMINI_API_KEY`: API Key để kết nối mô hình Google Gemini.
* `OLLAMA_BASE_URL`: Endpoint của Ollama local server (mặc định: `http://localhost:11434`).
* `OLLAMA_MODEL_NAME`: Tên model local (mặc định: `llama3`).
* `ENVIRONMENT`: Phân biệt môi trường (Ví dụ: `development` hoặc `production`). 


## 4. Testing Rules (Quy tắc kiểm thử)
* Luôn đảm bảo các logic xử lý khối lượng dữ liệu phức tạp (như `PriorityLogic`) và hành vi của AI có cơ chế theo vết (track input/output). 
* AI phải thêm các lệnh log (print / logging) ghi nhận trạng thái ở các block tính toán quan trọng để hỗ trợ người dùng chẩn đoán và khắc phục sự cố.


## 5. Folder Structure (Cấu trúc thư mục tổng hợp)
/Software-to-support-form-teacher---SSFT  
├── /app  
│   ├── __init__.py  
│   ├── /core                (Cấu hình & Logic hệ thống)  
│   │   ├── Config.py        (Nạp .env & Remote Config để Bật/Tắt AI)  
│   │   ├── Constants.py     (Lưu Role, Trạng thái vấn đề, Mức độ ưu tiên)  
│   │   ├── ErrorCodes.py    (Xử lý mã lỗi từ Firebase sang Tiếng Việt)  
│   │   ├── Middleware.py    (Kiểm soát điều hướng và vòng luân chuyển request)  
│   │   └── __init__.py  
│   ├── /features            (Tính năng nghiệp vụ)  
│   │   ├── /auth            (Tài khoản, Mật khẩu & Phân quyền)  
│   │   │   ├── AuthService.py  
│   │   │   └── PasswordService.py  (Xử lý đổi/quên mật khẩu)  
│   │   ├── /chat            (AI Tư vấn & Tin nhắn trực tiếp)  
│   │   │   ├── ChatProcessor.py  
│   │   │   ├── ContextManager.py  (Quản lý ngữ cảnh và lịch sử chat)  
│   │   │   ├── ResponseAggregator.py (Tổng hợp kết quả phản hồi của AI)  
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
│   ├── /api                 (FastAPI interface layer)  
│   │   ├── deps.py  
│   │   ├── exceptions.py  
│   │   └── /v1  
│   │       ├── api.py  
│   │       └── /endpoints  
│   │           ├── academic.py  
│   │           ├── auth.py  
│   │           ├── notifications.py  
│   │           └── chat.py  
│   ├── /services            (Kết nối Database/Cloud)  
│   │   ├── __init__.py  
│   │   ├── FirestoreHandler.py  (Lưu SV, Điểm, Tin nhắn)  
│   │   ├── StorageHandler.py    (Lưu Ảnh minh chứng, Avatar)  
│   │   ├── RealtimeHandler.py   (Trạng thái Chat trực tiếp)  
│   │   ├── FirebaseAuthHandler.py (Xử lý Auth)  
│   │   └── IssueService.py        (Xử lý nghiệp vụ vấn đề vào DB - có nguy cơ trùng lặp)  
│   ├── /utils               (Tiện ích dùng chung)  
│   │   ├── __init__.py  
│   │   ├── DateHelpers.py      (Định dạng thời gian)  
│   │   ├── Validators.py       (Kiểm tra dữ liệu đầu vào)  
│   │   ├── Formatters.py       (Làm tròn điểm GPA, tóm tắt văn bản)  
│   │   ├── AnalyticsHelpers.py  (Tính tỷ lệ chuyên cần, lọc top vấn đề cho Dashboard)  
│   │   ├── FileHelpers.py       (Kiểm tra định dạng, dung lượng file minh chứng)  
│   │   ├── StringHelpers.py     (Chuyển tiếng Việt không dấu, tách từ khóa cho AI)  
│   │   ├── SecurityHelpers.py   (Tạo mật khẩu tạm thời cho sinh viên)  
│   │   └── SearchEngine.py      (Hỗ trợ tìm kiếm sinh viên/vấn đề toàn diện)  
│   └── main.py              (Giao diện Streamlit chính)  
├── /data                    (Dữ liệu lưu trữ)  
│   ├── serviceAccountKey.json (Firebase Key)  
│   └── KnowledgeBase.json   (Dữ liệu keyword xác định)  
├── .env                     (Biến môi trường)  
├── .gitignore  
├── AGENTS.md  
├── SCHEMA.md                (Thiết kế cấu trúc dữ liệu)  
└── requirements.txt  