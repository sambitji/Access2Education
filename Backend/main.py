# =============================================================
# backend/main.py
# Edu-Platform — FastAPI Application Entry Point
# =============================================================

import sys
import os

# Add Backend to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.db import connect_db, disconnect_db
from routes.auth    import router as auth_router
from routes.test    import router as test_router
from routes.content import router as content_router
from routes.sr_routes import router as sr_router
from routes.chatbot import router as chatbot_router
from routes.cluster import router as cluster_router
from config import settings
from limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


# =============================================================
# Lifespan — Startup and Shutdown
# =============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    try:
        await connect_db()
    except Exception as e:
        print(f"Database connection failed during startup (normal for build): {e}")
    yield
    print("Server shutting down...")
    try:
        await disconnect_db()
    except Exception as e:
        print(f"Database disconnect failed: {e}")


# =============================================================
# App Instance
# =============================================================

app = FastAPI(
    title       = "Edu-Platform API",
    description = "AI-powered personalized learning platform",
    version     = "1.0.0",
    lifespan    = lifespan,
)


@app.on_event("startup")
async def startup_event():
    print("Startup event triggered...")
    await connect_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.CORS_ORIGINS,
    allow_credentials = settings.CORS_ALLOW_CREDENTIALS,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Rate Limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# =============================================================
# Routes
# =============================================================

app.include_router(auth_router)
app.include_router(test_router)
app.include_router(content_router)
app.include_router(sr_router, prefix="/spaced-repetition", tags=["Spaced Repetition"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(cluster_router, prefix="/cluster", tags=["Learning DNA"])

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "Edu-Platform API"}


# =============================================================
# Root
# =============================================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Edu-Platform API chal rahi hai!",
        "docs":    "/docs",
    }