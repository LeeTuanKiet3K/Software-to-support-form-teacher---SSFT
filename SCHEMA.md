# Database Schema (Firestore)

## 1. Collection: `Users` (Quản lý tài liệu người dùng)
- **Document ID**: `[UID]` (Lấy trực tiếp từ Firebase Authentication)
- **Fields**:
    - `full_name`: string (Họ và tên sinh viên hoặc giáo viên)
    - `email`: string (Email đăng ký)
    - `role`: string ("student" hoặc "advisor")  # Dùng để phân quyền giao diện
    - `class_id`: string (Mã lớp, ví dụ: "24CTT4") # Để GVCN quản lý đúng lớp của mình
    - `student_id`: string (Mã số sinh viên - chỉ dành cho role "student")
    - `created_at`: timestamp (Thời điểm tạo tài khoản)
    - `is_active`: boolean (Trạng thái tài khoản)

## 2. Collection: `issues` (Quản lý vấn đề sinh viên gửi)
- **Fields**:
    - `student_id`: reference (Liên kết đến user)
    - `content`: string (Nội dung vấn đề)
    - `timestamp`: timestamp (Thời gian gửi)
    - `category`: string (Phân loại: Học tập, Tâm lý, Quy định...)
    - `priority`: string ("P0", "P1", "P2")
    - `status`: string ("pending", "processing", "resolved")
    - `is_fallback`: boolean (Đánh dấu nếu AI không tự giải quyết được)

## 3. Collection: `commonData` (Dữ liệu uy tín cho AI tra cứu)
- **Fields**:
    - `topic`: string (Chủ đề: Quy chế thi, Học bổng...)
    - `content`: string (Nội dung chi tiết để AI dùng làm cơ sở trả lời)