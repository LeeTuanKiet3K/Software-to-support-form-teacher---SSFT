from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="SSFT Backend API",
    description="Software to support form teacher - API backend",
    version="1.0.0",
)

# Cấu hình CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000",  # Frontend Next.js
    "http://localhost:8501",  # Frontend Streamlit (nếu còn dùng)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router chính của version 1
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
async def root():
    return {"message": "SSFT Backend is running!", "status": "OK"}
