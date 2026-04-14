# =============================================================
# backend/main.py
# Edu-Platform — FastAPI Application Entry Point
# =============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.db import connect_db, disconnect_db
from routes.auth    import router as auth_router
from routes.test    import router as test_router
from routes.content import router as content_router
from config import settings
from limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


# =============================================================
# Lifespan — Startup aur Shutdown
# =============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server start ho raha hai...")
    await connect_db()
    yield
    print("Server band ho raha hai...")
    await disconnect_db()


# =============================================================
# App Instance
# =============================================================

app = FastAPI(
    title       = "Edu-Platform API",
    description = "AI-powered personalized learning platform",
    version     = "1.0.0",
    lifespan    = lifespan,
)


# =============================================================
# CORS
# =============================================================

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

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "Edu-Platform API"}


# =============================================================
# Root
# =============================================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Edu-Platform API chal rahi hai!",
        "docs":    "http://localhost:8000/docs",
    }