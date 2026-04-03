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
    allow_origins     = ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# =============================================================
# Routes
# =============================================================

app.include_router(auth_router)
app.include_router(test_router)
app.include_router(content_router)


# =============================================================
# Root
# =============================================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Edu-Platform API chal rahi hai!",
        "docs":    "http://localhost:8000/docs",
    }