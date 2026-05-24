import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.api.exceptions import firebase_exception_handler, FirebaseError

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="SSFT API Backend",
    description="API hỗ trợ nghiệp vụ Giáo viên chủ nhiệm & Trợ lý học vụ AI",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Cấu hình CORS cho phép Frontend kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các nguồn gốc để dễ debug phát triển
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các exception handlers để chuyển ngữ lỗi sang tiếng Việt
app.add_exception_handler(FirebaseError, firebase_exception_handler)

# Đăng ký Router chính thức
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "active",
        "message": "SSFT Backend FastAPI is running successfully.",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
