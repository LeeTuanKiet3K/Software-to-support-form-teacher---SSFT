# Phần mềm hỗ trợ Giáo viên chủ nhiệm (Smart Advisor)

> AI-powered Student Advisory Support System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?logo=firebase&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green.svg)

[Demo](#) • [Documentation](./docs) • [Architecture](#system-architecture)

---

## 📌 Overview

Smart Advisor là hệ thống hỗ trợ Giáo viên Chủ nhiệm (GVCN) quản lý và tư vấn sinh viên bằng Trí tuệ nhân tạo (AI).

Hệ thống giúp:

- Tiếp nhận phản ánh từ sinh viên
- Tự động đánh giá mức độ ưu tiên
- Hỗ trợ phát hiện các trường hợp cần can thiệp sớm
- Theo dõi kết quả học tập
- Tăng cường trao đổi giữa sinh viên và GVCN

---

## ✨ Key Features

### 🤖 AI Student Assistant

- Hỏi đáp nội quy, quy chế
- Hỗ trợ sinh viên 24/7
- Phân tích nội dung phản hồi

### 🚨 Intelligent Issue Classification

- Phân loại mức độ ưu tiên
- Đánh giá cảm xúc (Sentiment Analysis)
- Phát hiện trường hợp quan trọng cần hỗ trợ sớm

### 📊 Advisor Dashboard

- Theo dõi tình hình lớp
- Danh sách vấn đề cần xử lý
- Tổng quan học tập

### 📈 Academic Monitoring

- Theo dõi điểm số
- Phân tích kết quả học tập
- Hỗ trợ phát hiện nguy cơ học tập

### 👥 User Management

- Quản lý tài khoản
- Phân quyền người dùng
- Authentication bằng Firebase

---

## 🖼️ Screenshots

### Login

![Login](docs/images/login.png)

### Advisor Dashboard

![Advisor Dashboard](docs/images/advisor-dashboard.png)

### Student Workspace

![Student Workspace](docs/images/student-dashboard.png)

### AI Chat Assistant

![AI Chat](docs/images/chat.png)

---

## 🏗️ System Architecture

```text
┌─────────────────────┐
│     Frontend        │
│     Next.js         │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│      Backend        │
│      FastAPI        │
└──────┬────────┬─────┘
       │        │
       ▼        ▼

 Firebase   Gemini API
```

### Technology Stack

| Layer          | Technology         |
| -------------- | ------------------ |
| Frontend       | Next.js, React     |
| Backend        | FastAPI            |
| Database       | Firestore          |
| Authentication | Firebase Auth      |
| AI Engine      | Google Gemini      |
| Language       | Python, JavaScript |

---

## 🤖 AI Processing Workflow

```text
Student Message
       │
       ▼
AI Processor
       │
       ├── Sentiment Analysis
       ├── Priority Classification
       └── Risk Detection
       │
       ▼
Issue Assessment
       │
       ▼
Advisor Notification
```

### AI Capabilities

| Capability              | Description                |
| ----------------------- | -------------------------- |
| Sentiment Analysis      | Đánh giá cảm xúc sinh viên |
| Priority Classification | Xếp mức độ ưu tiên         |
| Risk Detection          | Phát hiện rủi ro           |
| Escalation Support      | Hỗ trợ chuyển GVCN xử lý   |

---

## 🚨 Issue Lifecycle

```text
Student
   │
   ▼
Submit Issue
   │
   ▼
AI Analysis
   │
   ▼
Priority Assignment
   │
   ▼
Advisor Review
   │
   ├── Resolved
   │
   └── Escalated
          │
          ▼
     Follow-up
```

---

## 👥 User Roles

### Student

- Chat với AI
- Gửi phản ánh
- Theo dõi điểm số

### Advisor

- Theo dõi Dashboard
- Xử lý phản ánh
- Nhận cảnh báo

### Admin

- Quản lý tài khoản
- Phân quyền người dùng

---

## ⚙️ Installation

### Backend

```bash
pip install -r requirements.txt
python -m app.main
```

Backend:

```text
http://localhost:8000
```

### Frontend

```bash
cd client
npm install
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

## 🚀 Quick Start

### 1. Start Backend

```bash
python -m app.main
```

### 2. Start Frontend

```bash
cd client
npm run dev
```

### 3. Open Browser

```text
http://localhost:3000
```

---

## 📂 Project Structure

```text
project-root/
│
├── app/
│   ├── api/
│   ├── features/
│   ├── services/
│   ├── models/
│   └── utils/
│
├── client/
│
├── docs/
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Troubleshooting

### Firebase Connection Error

Kiểm tra:

- File `.env`
- Firebase Credentials
- Firestore Configuration

### Gemini API Error

Kiểm tra:

- API Key
- Quota
- Internet Connection

### Port Conflict

```bash
npm run dev -- -p 3001
```

---

## 🤝 Contributing

```bash
git checkout -b feature/my-feature
git commit -m "Add new feature"
git push origin feature/my-feature
```

Sau đó tạo Pull Request.

---

## 📚 Documentation

| File                   | Description          |
| ---------------------- | -------------------- |
| README.md              | Tổng quan dự án      |
| SCHEMA.md              | Thiết kế CSDL        |
| AGENTS.md              | AI Rules             |
| docs/DeveloperGuide.md | Hướng dẫn phát triển |

---

## 🐛 Known Issues

- Gemini API có thể phản hồi chậm khi quá tải
- Một số giao diện chưa tối ưu cho màn hình rất nhỏ

---

## 📄 Changelog

### v2.0.0

- Migrate từ Streamlit sang Next.js
- Tái cấu trúc Backend
- Nâng cấp AI Pipeline

### v1.0.0

- Initial Release

---

## ⚖️ License

MIT License.