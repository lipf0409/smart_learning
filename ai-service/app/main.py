# AI Service Main Entry
import sys
import io

# Fix Windows console encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

from app.config import settings
from app.database import init_db
from app.redis_client import redis_client
from app.routers import posture, question, learning, rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"[Startup] {settings.APP_NAME} v2.0.0")
    print(f"[Startup] Model: {settings.SPARK_MODEL_VERSION}")

    try:
        await init_db()
        print("[Startup] Database initialized")
    except Exception as e:
        print(f"[Startup] Database init failed: {e}")

    try:
        await redis_client.connect()
    except Exception as e:
        print(f"[Startup] Redis connect failed: {e}")

    yield

    # Shutdown
    await redis_client.disconnect()
    print("[Shutdown] Service stopped")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI services for posture detection, question solving, and learning analysis",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(posture.router)
app.include_router(question.router)
app.include_router(learning.router)
app.include_router(rag.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": "2.0.0",
        "endpoints": {
            "posture_detect": "/api/posture/detect",
            "question_solve": "/api/question/solve",
            "learning_analyze": "/api/learning/analyze",
            "study_plan": "/api/learning/plan",
            "ai_chat": "/api/learning/chat",
            "learning_stats": "/api/learning/stats",
            "chat_records": "/api/learning/records",
            "rag_search": "/api/rag/search"
        },
        "features": {
            "database": "MySQL",
            "cache": "Redis",
            "rag_ready": True,
            "model": settings.SPARK_MODEL_VERSION
        }
    }


@app.get("/health")
async def health():
    """Overall health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected" if redis_client.client else "disconnected",
        "spark_configured": bool(settings.SPARK_APP_ID and settings.SPARK_API_KEY and settings.SPARK_API_SECRET)
    }