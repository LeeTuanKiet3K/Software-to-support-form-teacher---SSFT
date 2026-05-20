# SSFT Frontend

Giao diện Next.js 14 cho hệ thống **Phần mềm hỗ trợ Giáo viên chủ nhiệm (SSFT)**.

## Cài đặt & Chạy

### 1. Cài Node.js (nếu chưa có)
Tải tại: https://nodejs.org → chọn phiên bản LTS

### 2. Cài dependencies
```bash
cd frontend
npm install
```

### 3. Chạy dev server
```bash
npm run dev
```

Mở trình duyệt: http://localhost:3000

## Tài khoản test (Mock)

| Loại | Email | Mật khẩu |
|------|-------|----------|
| GVCN (Dashboard) | `gvcn@test.com` | bất kỳ |
| Sinh viên (Chat) | `student@test.com` | bất kỳ |

> **Lưu ý**: Email chứa "gv", "gvcn", "advisor" → vào Dashboard GVCN. Còn lại → Chat sinh viên.

## Cấu trúc
```
frontend/
├── app/
│   ├── login/     ← Trang đăng nhập
│   ├── dashboard/ ← Dashboard GVCN
│   └── student/   ← Chat AI sinh viên
├── components/    ← UI components
├── lib/mockData.ts
└── types/index.ts
```
