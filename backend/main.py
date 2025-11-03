"""
Main entry point for running the backend
"""
import uvicorn
from api.server import app
from agent.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run the application"""
    logger.info("🚀 Starting Provenance Guardian")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"GPU Enabled: {settings.enable_gpu}")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=settings.environment == "development"
    )


if __name__ == "__main__":
    main()
