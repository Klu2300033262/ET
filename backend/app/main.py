from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from backend.app.config.settings import settings
from backend.app.config.logging import setup_logging
from backend.app.core.middleware import setup_middleware
from backend.app.core.exceptions import (
    APIException,
    global_exception_handler,
    api_exception_handler,
    validation_exception_handler,
)
from backend.app.core.init_folders import initialize_folders
from backend.app.api.router import api_router

# 1. Initialize System Logger
logger = setup_logging()

# 2. Define FastAPI application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing IndusMindAI Backend System...")
    initialize_folders()
    yield
    # Shutdown actions
    logger.info("Shutting down IndusMindAI Backend System.")

# 3. Initialize FastAPI application instance
app = FastAPI(
    title="IndusMindAI API",
    description="Backend API for the Industrial Knowledge Intelligence Platform.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI route
    redoc_url="/redoc"     # ReDoc UI route
)

# 4. Attach Middlewares (CORS, Logging)
setup_middleware(app)

# 5. Attach Custom Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 6. Include API Routers (Versioning prefix: /api/v1)
app.include_router(api_router, prefix="/api/v1")
