"""
Development web server for serving the frontend
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="News Automation API",
    description="Backend service for news automation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global error handler
@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Error handling request {request.url}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(e),
                "path": str(request.url)
            }
        )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    try:
        # Check if news data is accessible
        with open("public/data/news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
            last_update = news_data[0]["fetchedAt"] if news_data else None
    except Exception as e:
        last_update = None
        logger.error(f"Health check failed: {str(e)}")

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "lastNewsUpdate": last_update
    }

# Mount static files
app.mount("/", StaticFiles(directory="public", html=True), name="static")

# Serve index.html for the root path
@app.get("/")
async def read_root():
    return FileResponse("public/index.html")

# Get news data
@app.get("/api/news")
async def get_news(category: Optional[str] = None, limit: Optional[int] = None):
    """Get news articles with optional category filter and limit.
    
    Args:
        category: Optional category to filter by
        limit: Optional limit on number of articles to return
    """
    try:
        # Read news data
        with open("public/data/news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)

        # Apply category filter if provided
        if category:
            news_data = [
                article for article in news_data 
                if article.get("category", "").lower() == category.lower()
            ]

        # Apply limit if provided
        if limit and limit > 0:
            news_data = news_data[:limit]

        return {
            "success": True,
            "count": len(news_data),
            "data": news_data,
            "timestamp": datetime.now().isoformat()
        }

    except FileNotFoundError:
        logger.error("News data file not found")
        raise HTTPException(
            status_code=404,
            detail="News data not available"
        )
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in news data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Invalid news data format"
        )
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# Error handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "path": str(request.url),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Configure logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Run server
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_config=log_config,
        reload=True  # Enable auto-reload for development
    )
