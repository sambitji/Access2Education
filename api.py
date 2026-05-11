# =============================================================
# api.py - Vercel Entry Point
# Edu-Platform — FastAPI Application Entry Point
# =============================================================

import sys
import os

# Add current directory and Backend to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

print(f"Python path: {sys.path}")
print(f"Current dir: {os.getcwd()}")
print(f"Files in root: {os.listdir(ROOT_DIR) if os.path.exists(ROOT_DIR) else 'N/A'}")
print(f"Files in Backend: {os.listdir(BACKEND_DIR) if os.path.exists(BACKEND_DIR) else 'N/A'}")

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    print("FastAPI imports successful")
except Exception as e:
    print(f"FastAPI import error: {e}")

try:
    from routes.auth import router as auth_router
    print("Auth router import successful")
except Exception as e:
    print(f"Auth router import error: {e}")

try:
    from config import settings
    print("Config import successful")
except Exception as e:
    print(f"Config import error: {e}")

try:
    from limiter import limiter
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    print("Limiter imports successful")
except Exception as e:
    print(f"Limiter import error: {e}")


# =============================================================
# Lifespan — Startup and Shutdown
# =============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    try:
        from database.db import connect_db
        await connect_db()
    except Exception as e:
        print(f"Database connection failed during startup (normal for build): {e}")
    yield
    print("Server shutting down...")
    try:
        from database.db import disconnect_db
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


app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],  # Allow all for Vercel
    allow_credentials = True,
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