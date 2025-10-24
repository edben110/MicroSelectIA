"""
Health check endpoint
"""

from fastapi import APIRouter
from datetime import datetime
from ...core.config import get_settings
from ...services.ai_matcher import get_ai_matcher

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns API status and model information
    """
    settings = get_settings()
    ai_matcher = get_ai_matcher(settings.AI_MODEL)
    
    try:
        model_info = ai_matcher.get_model_info()
        model_status = "loaded"
    except Exception as e:
        model_info = {"error": str(e)}
        model_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MicroSelectIA",
        "version": "1.0.0",
        "model": {
            "name": settings.AI_MODEL,
            "status": model_status,
            "info": model_info
        },
        "config": {
            "skills_weight": settings.SKILLS_WEIGHT,
            "experience_weight": settings.EXPERIENCE_WEIGHT,
            "education_weight": settings.EDUCATION_WEIGHT,
            "semantic_weight": settings.SEMANTIC_WEIGHT,
            "min_threshold": settings.MIN_MATCH_THRESHOLD,
            "good_threshold": settings.GOOD_MATCH_THRESHOLD,
            "excellent_threshold": settings.EXCELLENT_MATCH_THRESHOLD
        }
    }


@router.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "service": "MicroSelectIA - AI-Powered Candidate Matching",
        "version": "1.0.0",
        "description": "Microservicio de selección de candidatos usando IA para matching semántico",
        "endpoints": {
            "health": "/health",
            "single_match": "POST /api/match/single",
            "batch_match": "POST /api/match/batch",
            "explain_match": "POST /api/match/explain"
        },
        "documentation": "/docs"
    }
