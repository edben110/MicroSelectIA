"""
FastAPI application factory and configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routes import health, matching
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    application = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        debug=settings.API_DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    application.include_router(health.router, tags=["Health"])
    application.include_router(matching.router, prefix="/api/match", tags=["Matching"])
    
    # Startup event
    @application.on_event("startup")
    async def startup_event():
        logger.info("Starting MicroSelectIA...")
        logger.info(f"API Version: {settings.API_VERSION}")
        logger.info(f"AI Model: {settings.AI_MODEL}")
        logger.info(f"Device: {settings.AI_DEVICE}")
        logger.info("Application started successfully!")
    
    # Shutdown event
    @application.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down MicroSelectIA...")
    
    # Global exception handler
    @application.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(f"Global exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(exc) if settings.API_DEBUG else "An error occurred"
            }
        )
    
    return application


# Create app instance
app = create_application()
