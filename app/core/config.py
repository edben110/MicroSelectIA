"""
Configuration settings for the microservice
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    API_DEBUG: bool = False
    API_TITLE: str = "MicroSelectIA - AI Candidate Matching Service"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Microservicio de IA para calcular compatibilidad entre candidatos y ofertas laborales"
    
    # AI Model Configuration
    AI_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    AI_DEVICE: str = "cpu"  # 'cpu' or 'cuda'
    AI_MAX_LENGTH: int = 512
    
    # Matching Weights (must sum to 1.0)
    SKILLS_WEIGHT: float = 0.40
    EXPERIENCE_WEIGHT: float = 0.25
    SEMANTIC_WEIGHT: float = 0.25
    EDUCATION_WEIGHT: float = 0.10
    
    # Matching Thresholds
    MIN_MATCH_SCORE: float = 0.30
    GOOD_MATCH_SCORE: float = 0.60
    EXCELLENT_MATCH_SCORE: float = 0.80
    
    # CORS Origins
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:5173"
    
    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow .env file to be optional (will use only environment variables if .env doesn't exist)
        extra = "ignore"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def validate_weights(self) -> bool:
        """Validate that weights sum to 1.0"""
        total = (
            self.SKILLS_WEIGHT +
            self.EXPERIENCE_WEIGHT +
            self.SEMANTIC_WEIGHT +
            self.EDUCATION_WEIGHT
        )
        return abs(total - 1.0) < 0.01  # Allow small floating point errors


# Global settings instance
settings = Settings()

# Validate weights on startup
if not settings.validate_weights():
    raise ValueError(
        f"Weights must sum to 1.0, current sum: "
        f"{settings.SKILLS_WEIGHT + settings.EXPERIENCE_WEIGHT + settings.SEMANTIC_WEIGHT + settings.EDUCATION_WEIGHT}"
    )
