from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.ErrorCodes import getErrorMessage

try:
    from firebase_admin.exceptions import FirebaseError
except ImportError:
    class FirebaseError(Exception):
        pass

async def firebase_exception_handler(request: Request, exc: FirebaseError):
    """
    Global Exception Handler cho FirebaseError.
    Chuyển đổi lỗi từ Firebase Admin SDK thành JSON Response thân thiện bằng tiếng Việt.
    """
    error_code = getattr(exc, 'code', 'unknown')
    if error_code == 'unknown':
        cause = getattr(exc, 'cause', None)
        if cause and hasattr(cause, 'code'):
            error_code = cause.code
            
    # Lấy message tiếng Việt
    message = getErrorMessage(error_code)
    
    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": message,
            "details": str(exc)
        }
    )
