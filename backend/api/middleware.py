import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        logger.info(f"→ {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[{response.status_code}] {duration:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": str(e) if request.app.state.debug else "An error occurred"
                }
            )