"""
ATF Sentinel - GitHub Webhook Server
Main FastAPI application that receives and processes GitHub PR events
Author: ANIRUDH S J
"""
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from app.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ATF Sentinel",
    description="Automated security scanning for GitHub Pull Requests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 ATF Sentinel starting up...")
   
    # Validate configuration
    if config.validate():
        logger.info("✅ All configuration validated")
    else:
        logger.warning("⚠️ Some configuration issues detected")
   
    logger.info("✅ Application ready to receive webhooks")

@app.get("/")
async def root():
    """Root endpoint - basic service info"""
    return {
        "service": "ATF Sentinel",
        "version": "1.0.0",
        "status": "operational",
        "description": "Automated security scanning for GitHub Pull Requests",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook/github",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
   
    health_status = {
        "status": "healthy",
        "secrets_loaded": bool(config.github_token),
        "version": "1.0.0"
    }
   
    # Check if all critical components are working
    if not health_status["secrets_loaded"]:
        health_status["status"] = "degraded"
        return JSONResponse(status_code=503, content=health_status)
   
    return health_status

# For local testing
if __name__ == "__main__":
    import uvicorn
   
    print("\n" + "="*70)
    print("🚀 Starting ATF Sentinel locally...")
    print("="*70)
    print(f"\n📍 Server will run at: http://localhost:8000")
    print(f"📖 API docs at: http://localhost:8000/docs")
    print(f"💚 Health check: http://localhost:8000/health")
    print("\n" + "="*70 + "\n")
   
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )