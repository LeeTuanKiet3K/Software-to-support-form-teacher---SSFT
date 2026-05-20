# Software-to-support-form-teacher---SSFT

## 1. Project Context (Bối cảnh Đồ án)
* **Project Name**: Phần mềm hỗ trợ Giáo viên chủ nhiệm (GVCN).
* **Core Objective**: Xây dựng hệ thống hỗ trợ GVCN quản lý, tư vấn và phân loại vấn đề của sinh viên bằng AI để giảm tải khối lượng công việc cho Giáo viên chủ nhiệm, nâng cao hiệu suất của hoạt động chủ nhiệm lớp.
* **Target Users**: Sinh viên (Student) và Giáo viên chủ nhiệm (Class Advisor).


## 2. Technical Stack (Công nghệ sử dụng)
* **Backend Language**: Python 3.10+.
* **UI Runtime**: Streamlit (`app/main.py`) là entrypoint đang chạy chính.
* **API Runtime**: FastAPI router theo phiên bản `app/api/v1/`.
* **Database**: Firebase (Firestore) dùng làm Knowledge Base (Cơ sở tri thức) để đảm bảo tính chính xác và tránh Hallucination (AI bịa đặt). Sử dụng Firestore Realtime Listeners để cập nhật danh sách vấn đề của sinh viên ngay khi có dữ liệu mới. Ưu tiên tối ưu hóa số lượng truy vấn (Read operations) để tránh vượt quá định mức của Firebase Free Tier.
* **Framework**: Ưu tiên các thư viện Python hiện đại để xử lý logic và kết nối Firebase (firebase-admin).

## 3. Architecture & Style Rules (Quy tắc Kiến trúc và Phong cách)
* **Feature-based Structure**: Mỗi tính năng lớn phải nằm trong một folder riêng biệt tại `/app/features/`. Tuyệt đối không gộp nhiều tính năng vào một file đơn lẻ.
* **Service First for IO**: Mọi thao tác Firebase/Auth/Storage phải đi qua lớp `/app/services/` trước, endpoint/UI không gọi DB trực tiếp.
* **API Layer Rule**: Các file trong `/app/api/v1/endpoints/` chỉ nhận request/validate response, sau đó gọi service tương ứng.
* **Coding Style**: Tuân thủ nghiêm ngặt chuẩn **PEP 8**. Sử dụng **Type Hinting** (Gợi ý kiểu dữ liệu) cho tất cả các function (hàm).
* **Language Policy**: 
    * Giữ nguyên các **Technical terms** (Thuật ngữ chuyên ngành) bằng tiếng Anh.
    * Phải có chú thích (Comments) bằng tiếng Việt ngay bên cạnh hoặc phía trên các thuật ngữ/logic phức tạp.
    * Ví dụ: `def authenticate_user():  # Xác thực người dùng`.
* **Global Error Handling (Xử lý lỗi toàn cục)**: Mọi thao tác kết nối ngoại vi (Firebase, Gemini API...) bắt buộc nằm trong khối `try...except`. Bắt cụ thể các loại exception (VD: `FirebaseError`) thay vì dùng `Exception` chung chung. Luôn ghi log lỗi chi tiết trước khi trả thông báo lỗi ra giao diện.

### 3.1 Current Canonical Interfaces (Chuẩn interface hiện tại)
Để tránh lệch chuẩn giữa code cũ/mới, khi viết mới phải ưu tiên các hàm sau:

1. **FirebaseAuthHandler**
   - Đăng nhập: `signInWithEmail(email, password)`
   - Đăng xuất: `signOutUser(uid)`
2. **FirestoreHandler**
   - Ghi document: `saveDocument(collectionName, data, documentId=None)`
   - Đọc document: `getDocument(collectionName, documentId)`
   - Cập nhật: `updateDocument(collectionName, documentId, data)`
   - Query nhiều bản ghi: `queryDocuments(collectionName, filters, limitCount=100)`
3. **Issue constants**
   - Priority: `URGENT`, `HIGH`, `MEDIUM`, `LOW`
   - Status: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `PENDING_ADVISOR`

*Lưu ý:* Một số alias tương thích ngược vẫn tồn tại để hỗ trợ module cũ; không tạo alias mới nếu không thật sự cần thiết.


## 4. Specific Feature Instructions (Chỉ dẫn tính năng cụ thể)

#### A. Authentication (Đăng nhập)
* Phân loại Role (Vai trò) ngay từ bước đăng nhập để dẫn vào đúng Dashboard (Bảng điều khiển) tương ứng của Sinh viên hoặc GVCN.
* Sử dụng `ErrorCodes` từ `/core` để hiển thị thông báo lỗi tiếng Việt thân thiện khi đăng nhập thất bại (Ví dụ: "Sai mật khẩu" thay vì "auth/wrong-password").

#### B. AI Processor & Fallback (Xử lý AI và Chuyển tiếp)
* AI phải thực hiện **Sentiment Analysis** (Phân tích cảm xúc) và phân loại độ phức tạp của vấn đề.
* **Auto-reply**: Trả lời các câu hỏi về quy định, thủ tục dựa trên Knowledge Base.
* **Fallback Logic**: Với vấn đề nhạy cảm (Tâm lý, Cảm xúc, Khiếu nại), AI phải chuyển trạng thái sang "Pending Advisor" (Chờ GVCN xử lý) và tạo Notification (Thông báo) cho giáo viên.
* Tối ưu hóa Token bằng cách sử dụng `extractKeywords` từ `StringHelpers` trước khi gửi dữ liệu cho LLM.
* **Prompt Engineering Constraints**: 
    * Toàn bộ system prompt phải được định nghĩa và quản lý tập trung ở `/app/features/chat/PromptTemplates.py`.
    * Đối với những module có chức năng tính toán hoặc phân loại ngầm, luôn ép kiểu LLM trả về cấu trúc dễ định dạng (ví dụ trả về nguyên gốc dạng JSON) để tránh làm lệch Data Pipeline.

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

## 5. Password & Security Policy (Chính sách Bảo mật & Mật khẩu)
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