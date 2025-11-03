from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
import logging

from ..agent.config import settings
from ..agent.provenance_guardian import ProvenanceGuardian
from ..utils.logger import get_logger
from .routes import router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic"""
    # Startup
    logger.info("🚀 Starting Provenance Guardian API...")
    
    # Initialize agent
    app.state.agent = ProvenanceGuardian()
    
    logger.info("✅ API ready")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="Provenance Guardian API",
    description="AI Model Authenticity Auditor",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Provenance Guardian API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "chat": "/api/v1/assist",
            "audit": "/api/v1/audit",
            "health": "/api/v1/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}