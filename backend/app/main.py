"""
Main FastAPI Application Entry Point for KrishiDrishti Edge.
"""
from contextlib import asynccontextmanager
import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger, log_event
from app.core.errors import KrishiException, ErrorCode
from app.api.routes import api_router
from app.api.routes.health import get_health
from app.schemas.health import HealthResponse
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Lifespan: Initialize offline SQLite database safely
    log_event("SYSTEM", "INFO", f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    log_event("SYSTEM", "INFO", f"Tagline: {settings.TAGLINE}")
    log_event("DEVICE", "INFO", f"Mode: {'DEMO SIMULATION' if settings.DEMO_MODE else 'REAL HARDWARE MODE'}")
    log_event("AI", "INFO", f"AI Mode: {settings.AI_MODE} (Confidence Threshold: {settings.AI_CONFIDENCE_THRESHOLD:.2f})")
    
    # Initialize SQLite Database & Tables
    init_db()
    
    yield
    # Shutdown Lifespan
    log_event("SYSTEM", "INFO", "Shutting down KrishiDrishti Edge gracefully...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Portable Offline AI-Powered Farming Assistant for Smart India Hackathon (SIH)",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KrishiException Handler
@app.exception_handler(KrishiException)
async def krishi_exception_handler(request: Request, exc: KrishiException):
    log_event("API", "WARNING", f"KrishiException on {request.url.path}: [{exc.code}] {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# Global API Exception Handler (Zero Stack Trace Leaks)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_event("SYSTEM", "ERROR", f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCode.INTERNAL_ERROR.value,
            "message": "Internal server error occurred",
            "details": str(exc) if settings.DEBUG else "An unexpected error occurred. Consult system logs.",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )

# Root-level health endpoint aliases
@app.get("/health", response_model=HealthResponse, tags=["System Health & Diagnostics"])
async def root_health():
    """Root health check alias."""
    return await get_health()

@app.get("/api/v1/health", response_model=HealthResponse, tags=["System Health & Diagnostics"])
async def api_v1_health():
    """API v1 health check alias."""
    return await get_health()

# Include API Router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
