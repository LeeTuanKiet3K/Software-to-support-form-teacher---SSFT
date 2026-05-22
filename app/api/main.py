from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="SSFT API",
    description="Backend API cho Hệ thống Hỗ trợ Giáo viên Chủ nhiệm",
    version="1.0.0",
)

# Cấu hình CORS để cho phép frontend (VD: Next.js chạy trên cổng 3000) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Có thể thay đổi thành ["http://localhost:3000"] ở production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn (Mount) toàn bộ các router v1 vào app chính
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Welcome to SSFT API. Go to /docs for Swagger UI"}
