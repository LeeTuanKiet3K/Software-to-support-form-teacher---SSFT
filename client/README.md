# SSFT Frontend (Client)

Đây là giao diện người dùng được xây dựng bằng **Next.js 14** (App Router) cho hệ thống **Phần mềm hỗ trợ Giáo viên chủ nhiệm (SSFT)**.

## Yêu cầu Hệ thống
- **Node.js**: Phiên bản 18.17.0 trở lên (Khuyến nghị dùng bản LTS mới nhất).
- **Trình duyệt**: Chrome, Firefox, Edge, Safari phiên bản mới.
- **Backend**: Đảm bảo Backend (FastAPI) đang chạy ở cổng `8000` (mặc định) để có thể đăng nhập và lấy dữ liệu thật từ hệ thống.

## Cài đặt & Chạy ứng dụng

### 1. Cài đặt các thư viện (Dependencies)
Mở terminal và di chuyển vào thư mục `client`, sau đó chạy:
```bash
cd client
npm install
```

### 2. Khởi chạy môi trường phát triển (Dev server)
```bash
npm run dev
```

Sau khi Terminal báo thành công, hãy mở trình duyệt và truy cập: [http://localhost:3000](http://localhost:3000)

## Hướng dẫn Đăng nhập
Hệ thống hiện tại đã kết nối trực tiếp với **Firebase Authentication** thông qua Backend thật, không còn dùng dữ liệu giả (Mock data) nữa.

- **Sinh viên / GVCN**: Sử dụng tài khoản đã được cấp hoặc tạo mới từ trang Quản trị để đăng nhập.
- **Trang Quản trị (Admin)**: Bạn có thể truy cập `http://localhost:3000/admin` để khởi tạo hàng loạt tài khoản cho Giáo viên và Sinh viên vào cơ sở dữ liệu. 
- **Phân quyền tự động**: Khi đăng nhập thành công, hệ thống sẽ tự động nhận diện Role (Vai trò) và điều hướng về trang tương ứng:
  - Tài khoản sinh viên → Chuyển tới giao diện Tư vấn AI (`/student`).
  - Tài khoản GVCN → Chuyển tới Dashboard theo dõi lớp (`/dashboard`).

## Cấu trúc thư mục cốt lõi
```text
client/
├── app/
│   ├── admin/       ← Trang khởi tạo tài khoản (Admin)
│   ├── login/       ← Trang đăng nhập chung
│   ├── dashboard/   ← Dashboard toàn diện cho GVCN (Quản lý, Thống kê, Lịch hẹn)
│   ├── student/     ← Giao diện cho sinh viên (Chat AI, Xem điểm)
│   ├── globals.css  ← Cấu hình Tailwind CSS & hiệu ứng
│   └── layout.tsx   ← Bố cục (Root Layout) của Next.js
├── components/      ← Chứa các Component dùng chung (UI components, Biểu đồ, Chat...)
├── lib/             ← Tiện ích và cấu hình kết nối (Gọi API, Các hằng số hiển thị)
└── types/           ← Khai báo các Interface/Kiểu dữ liệu (TypeScript)
```

## Đóng gói (Build) cho Production
Để kiểm tra lỗi hoặc chạy trên môi trường thực tế, hãy dùng lệnh:
```bash
npm run build
npm start
```
