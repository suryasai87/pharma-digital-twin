"""
FastAPI Backend for Pharmaceutical Manufacturing Digital Twin Platform
Implements 21 CFR Part 11 compliant REST API with audit trails
"""
import os
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from backend.api import bioreactor, batch, equipment, contamination, ebr, audit, simulator
from backend.utils.logging_config import setup_logging
from backend.utils.auth import verify_token, AuditContext

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Pharmaceutical Digital Twin API")
    logger.info("Loading ML models from MLflow...")
    # Initialize ML models, database connections, etc.
    yield
    logger.info("Shutting down Pharmaceutical Digital Twin API")
    # Cleanup resources

# Create FastAPI app
app = FastAPI(
    title="Pharmaceutical Manufacturing Digital Twin API",
    description="""
    **21 CFR Part 11 Compliant REST API for Pharmaceutical Manufacturing**

    Features:
    - Real-time bioreactor monitoring
    - Batch quality control and analytics
    - Predictive maintenance
    - Contamination detection
    - Electronic Batch Records (EBR)
    - Complete audit trail (ALCOA+ compliant)
    - Multi-site support

    Regulatory Compliance:
    - 21 CFR Part 11 (Electronic Records/Signatures)
    - EU Annex 11 (Computerized Systems)
    - cGMP (Current Good Manufacturing Practices)
    - Data Integrity (ALCOA+)
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "pharma-digital-twin-api"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root with basic information"""
    return {
        "service": "Pharmaceutical Manufacturing Digital Twin API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/health",
        "compliance": "21 CFR Part 11, cGMP, ALCOA+"
    }

# Include routers
app.include_router(bioreactor.router, prefix="/api/v1/bioreactor", tags=["Bioreactor"])
app.include_router(batch.router, prefix="/api/v1/batch", tags=["Batch Quality"])
app.include_router(equipment.router, prefix="/api/v1/equipment", tags=["Equipment"])
app.include_router(contamination.router, prefix="/api/v1/contamination", tags=["Contamination"])
app.include_router(ebr.router, prefix="/api/v1/ebr", tags=["Electronic Batch Records"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit Trail"])
app.include_router(simulator.router, prefix="/api/v1/simulator", tags=["Training Simulator"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "production") == "development",
        log_level="info"
    )
