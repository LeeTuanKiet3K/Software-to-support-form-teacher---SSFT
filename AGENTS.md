# AGENTS.md - Project Instructions for GVCN Support System

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