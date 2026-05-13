# SSFT — Software to Support Form Teacher

Phần mềm hỗ trợ **Giáo viên chủ nhiệm (GVCN)** quản lý, tư vấn và phân loại vấn đề sinh viên bằng AI.

## Cấu trúc dự án

```
Software-to-support-form-teacher---SSFT/
├── /app        ← Python backend (FastAPI + logic AI)
├── /client     ← Next.js 14 frontend (UI chính)
├── /data       ← KnowledgeBase.json, Firebase keys
├── AGENTS.md   ← Coding conventions & quy trình
├── SCHEMA.md   ← Firestore database schema
└── requirements.txt
```

## Khởi chạy

### Backend (Python FastAPI)
```bash
pip install -r requirements.txt
uvicorn app.api.v1.api:api_router --reload --port 8000
```

### Frontend (Next.js)
```bash
cd client
npm install
npm run dev
# Mở http://localhost:3000
```

## Tài khoản test

| Loại | Email | Mật khẩu |
|------|-------|----------|
| GVCN → Dashboard | `gvcn@test.com` | bất kỳ |
| Sinh viên → Chat | `student@test.com` | bất kỳ |

## Tech Stack

| Tầng | Công nghệ |
|------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| Backend | Python 3.10+, FastAPI, Firebase Admin |
| AI | Google Gemini 1.5 Flash + Llama 3 (Ollama local) |
| Database | Firebase Firestore |
| Storage | Cloudinary |