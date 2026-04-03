# =============================================================
# backend/database/db.py
# Edu-Platform — MongoDB Connection & Database Setup
# =============================================================

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

# Config se values lo
try:
    from config import settings
    MONGODB_URL   = settings.MONGODB_URL
    DATABASE_NAME = settings.DATABASE_NAME
    MONGO_TIMEOUT = settings.MONGO_TIMEOUT_MS
    MONGO_MAX     = settings.MONGO_MAX_POOL
    MONGO_MIN     = settings.MONGO_MIN_POOL
except Exception:
    # Fallback agar config load na ho
    MONGODB_URL   = os.getenv("MONGODB_URL",   "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "edu_platform")
    MONGO_TIMEOUT = 5000
    MONGO_MAX     = 10
    MONGO_MIN     = 1


# =============================================================
# Global Client
# =============================================================

class Database:
    client:   AsyncIOMotorClient   = None
    database: AsyncIOMotorDatabase = None


db_instance = Database()


# =============================================================
# Connect & Disconnect
# =============================================================

async def connect_db():
    """MongoDB se connect karo — startup pe call hota hai."""
    print(f"MongoDB se connect ho raha hai: {MONGODB_URL}")

    db_instance.client = AsyncIOMotorClient(
        MONGODB_URL,
        serverSelectionTimeoutMS = MONGO_TIMEOUT,
        maxPoolSize              = MONGO_MAX,
        minPoolSize              = MONGO_MIN,
    )
    db_instance.database = db_instance.client[DATABASE_NAME]

    await db_instance.client.admin.command("ping")
    print(f"MongoDB connected! Database: '{DATABASE_NAME}'")

    await create_indexes()


async def disconnect_db():
    """MongoDB connection band karo — shutdown pe call hota hai."""
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection band ho gaya.")


# =============================================================
# Indexes
# =============================================================

async def create_indexes():
    """Saare collections ke indexes create karo."""
    db = db_instance.database

    # Users
    await db["users"].create_index("email",          unique=True, name="idx_users_email")
    await db["users"].create_index("role",                         name="idx_users_role")
    await db["users"].create_index("learning_style",               name="idx_users_style")

    # Test Results
    await db["test_results"].create_index("user_id",                              name="idx_results_user")
    await db["test_results"].create_index([("user_id", 1), ("submitted_at", -1)], name="idx_results_user_date")

    # Progress
    await db["progress"].create_index(
        [("user_id", 1), ("content_id", 1)],
        unique=True, name="idx_progress_user_content"
    )
    await db["progress"].create_index([("user_id", 1), ("completed", 1)], name="idx_progress_completed")
    await db["progress"].create_index([("user_id", 1), ("subject",   1)], name="idx_progress_subject")

    # Refresh Tokens
    await db["refresh_tokens"].create_index("token",      unique=True,         name="idx_rt_token")
    await db["refresh_tokens"].create_index("user_id",                         name="idx_rt_user")
    await db["refresh_tokens"].create_index("expires_at", expireAfterSeconds=0, name="idx_rt_ttl")

    # OTPs
    await db["otps"].create_index("email",      unique=True,          name="idx_otps_email")
    await db["otps"].create_index("expires_at", expireAfterSeconds=0, name="idx_otps_ttl")

    print("Indexes create ho gaye!")


# =============================================================
# Dependency — Routes mein Depends(get_db) se use karo
# =============================================================

async def get_db() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency.

    Usage:
        async def my_route(db: AsyncIOMotorDatabase = Depends(get_db)):
            ...
    """
    return db_instance.database


# =============================================================
# Collection Helpers
# =============================================================

def get_users_collection():
    return db_instance.database["users"]

def get_test_results_collection():
    return db_instance.database["test_results"]

def get_progress_collection():
    return db_instance.database["progress"]

def get_refresh_tokens_collection():
    return db_instance.database["refresh_tokens"]

def get_otps_collection():
    return db_instance.database["otps"]