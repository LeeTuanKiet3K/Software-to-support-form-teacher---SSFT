# Firestore Database Schema (Sơ đồ cơ sở dữ liệu)

## 1. Core Collections (Bộ sưu tập cốt lõi)

### **Collection: `Users` (Quản lý người dùng)**
* **Document ID**: `[UID]` (Lấy từ Firebase Authentication).
* **Fields**:
    * `full_name`: string (Họ và tên).
    * `email`: string (Email đăng ký).
    * `role`: string (`"student"` / `"advisor"` / `"admin"`).
    * `class_id`: string (Mã lớp - VD: 24CTT4).
    * `student_id`: string (Mã số sinh viên - nếu là student).
    * `avatar_url`: string (Ảnh đại diện - URL).
    * `is_active`: boolean (Trạng thái tài khoản).
    * `created_at`: timestamp (Thời điểm tạo).
    * `updated_at`: timestamp (Thời điểm cập nhật).

### **Collection: `Classes` (Danh sách lớp học)**
* **Document ID**: Auto-generated (Hệ thống tự tạo).
* **Fields**:
    * `class_name`: string (Tên lớp).
    * `advisor_id`: string (UID của GVCN - Liên kết với Users).
    * `student_count`: int (Số lượng sinh viên).
    * `created_at`: timestamp (Thời điểm tạo).

---

## 2. Issue Tracking & Management (Quản lý vấn đề)

### **Collection: `Issues` (Các vấn đề sinh viên báo cáo)**
* **Document ID**: Auto-generated.
* **Fields**:
    * `student_id`: string (UID sinh viên).
    * `class_id`: string (Mã lớp).
    * `content`: string (Nội dung vấn đề).
    * `category`: string (Loại vấn đề).
    * `priority`: string (`P0` / `P1` / `P2`).
    * `status`: string (`pending` / `processing` / `resolved`).
    * `is_ai_handled`: boolean (AI xử lý được hay không).
    * `is_fallback`: boolean (AI không xử lý được, cần chuyển cho người).
    * `assigned_to`: string (UID GVCN xử lý).
    * `created_at`: timestamp (Thời gian tạo).
    * `updated_at`: timestamp (Thời gian cập nhật).

### **Collection: `Responses` (Phản hồi vấn đề)**
* **Document ID**: Auto-generated.
* **Fields**:
    * `issue_id`: string (Liên kết với Document ID của Issues).
    * `sender_id`: string (UID người gửi).
    * `sender_role`: string (`student` / `advisor` / `ai`).
    * `message`: string (Nội dung phản hồi).
    * `created_at`: timestamp (Thời gian gửi).

---

## 3. Communication (Hệ thống trao đổi)

### **Collection: `Chats` (Hội thoại trực tiếp)**
* **Fields**:
    * `participants`: array (Danh sách UID tham gia).
    * `type`: string (`direct` / `ai`).
    * `last_message`: string (Nội dung tin nhắn cuối).
    * `last_updated`: timestamp (Thời gian cập nhật).

### **Collection: `Message` (Chi tiết tin nhắn)**
* **Document ID**: Auto-generated.
* **Fields**:
    * `chat_id`: string (Liên kết với Chats).
    * `sender_id`: string (UID người gửi).
    * `message`: string (Nội dung văn bản).
    * `is_ai`: boolean (Có phải phản hồi từ AI không).
    * `created_at`: timestamp (Thời gian gửi).

---

## 4. Notifications & Academic (Thông báo & Học vụ)

### **Collection: `Notifications` (Thông báo cá nhân)**
* **Fields**:
    * `user_id`: string (UID người nhận).
    * `title`: string (Tiêu đề thông báo).
    * `content`: string (Nội dung).
    * `type`: string (`issue` / `system` / `announcement`).
    * `is_read`: boolean (Trạng thái đã đọc).
    * `created_at`: timestamp (Thời gian tạo).

### **Collection: `Academic_records` (Kết quả học tập)**
* **Document ID**: `[UID_sinh_viên]`.
* **Fields**:
    * `student_id`: string (UID sinh viên).
    * `class_id`: string (Mã lớp).
    * `subjects`: array (Danh sách môn học và điểm số).
    * `gpa`: double (Điểm trung bình học kỳ/năm).
    * `updated_at`: timestamp (Thời gian cập nhật).

---

## 5. Intelligence & Logs (Hỗ trợ AI & Nhật ký)

### **Collection: `Common_data` (Kho tri thức cho AI tra cứu)**
* **Fields**:
    * `topic`: string (Chủ đề tra cứu).
    * `doc_id`: string (id dữ liệu gốc).
    * `source`: string (nguồn dữ liệu).
    * `keywords`: array (Các từ khóa liên quan).
    * `content`: string (Nội dung tri thức chính xác).
    * `updated_at`: timestamp.

### **Collection: `AI_logs` (Nhật ký xử lý AI)**
* **Fields**:
    * `user_id`: string (UID người dùng tương tác).
    * `input`: string (Câu hỏi/Yêu cầu đầu vào).
    * `response`: string (Câu trả lời từ AI).
    * `confidence`: number (Độ tin cậy).
    * `is_fallback`: boolean (Có xảy ra lỗi hoặc chuyển tiếp không).
    * `created_at`: timestamp (Thời gian ghi nhật ký).

### **Collection: `Audit_logs` (Nhật ký hệ thống)**
* **Fields**:
    * `user_id`: string (UID người thực hiện).
    * `action`: string (Hành động thực hiện).
    * `target_id`: string (Đối tượng bị tác động).
    * `metadata`: map (Dữ liệu bổ sung).
    * `created_at`: timestamp (Thời gian ghi nhận).
