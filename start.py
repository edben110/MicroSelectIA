"""
MicroSelectIA - Script de inicio para desarrollo local
Solo para testing local, NO se usa en producción
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print("  MicroSelectIA - Development Server")
    print("=" * 60)
    print(f"  API: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"  Docs: http://localhost:{settings.API_PORT}/docs")
    print(f"  Model: {settings.AI_MODEL}")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
