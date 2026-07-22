from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from fastapi import Request
import logging

logger = logging.getLogger("indusmind-ai")

def setup_middleware(app: FastAPI):
    """Configures CORS and request logging middleware."""
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific React UI origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Time Logging and CORS PNA Middleware
    @app.middleware("http")
    async def add_process_time_and_cors_pna_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        logger.info(f"{request.method} {request.url.path} Status {response.status_code} Time {int(process_time * 1000)}ms")
        return response

