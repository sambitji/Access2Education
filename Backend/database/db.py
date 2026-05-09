# =============================================================
# backend/database/db.py
# Edu-Platform — MySQL Connection & SQLAlchemy ORM Setup
# =============================================================

import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, JSON, ForeignKey, Index, Text
from dotenv import load_dotenv

load_dotenv()

# Config
MYSQL_URL = os.getenv("MYSQL_URL", "mysql+aiomysql://root:@Sambit01@localhost:3306/edu_platform")

# SQLAlchemy Setup
engine = create_async_engine(MYSQL_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# =============================================================
# Models
# =============================================================

class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(60), nullable=False)
    email          = Column(String(100), unique=True, index=True, nullable=False)
    password_hash  = Column(String(255), nullable=False)
    role           = Column(String(20), default="student")
    avatar_url     = Column(String(255), default="")
    learning_style = Column(String(50), nullable=True)
    cluster_id     = Column(Integer, nullable=True)
    is_verified    = Column(Boolean, default=False)
    total_completed = Column(Integer, default=0)
    joined_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login     = Column(DateTime, nullable=True)

    # Relationships
    test_results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")
    sr_cards     = relationship("SRCard", back_populates="user", cascade="all, delete-orphan")

class TestResult(Base):
    __tablename__ = "test_results"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    scores       = Column(JSON, nullable=False) # {'logical': 80, ...}
    cluster      = Column(Integer, nullable=False)
    learning_style = Column(String(50), nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="test_results")

class Progress(Base):
    __tablename__ = "progress"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content_id   = Column(String(50), nullable=False)
    subject      = Column(String(50), nullable=False)
    completed    = Column(Boolean, default=False)
    score        = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_progress_user_content", "user_id", "content_id", unique=True),
    )

class SRCard(Base):
    __tablename__ = "sr_cards"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    concept_id     = Column(String(100), nullable=False)
    concept_title  = Column(String(255), nullable=False)
    subject        = Column(String(50), nullable=False)
    
    # SM-2 Fields
    interval       = Column(Integer, default=0)
    easiness       = Column(Float, default=2.5)
    repetition     = Column(Integer, default=0)
    next_review    = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    learning_style = Column(Integer, default=0)
    
    user = relationship("User", back_populates="sr_cards")

    __table_args__ = (
        Index("idx_sr_user_concept", "user_id", "concept_id", unique=True),
    )

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token      = Column(String(512), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)

class OTP(Base):
    __tablename__ = "otps"

    id         = Column(Integer, primary_key=True, index=True)
    email      = Column(String(100), index=True, nullable=False)
    otp        = Column(String(6), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    used       = Column(Boolean, default=False, index=True)

class SRReviewHistory(Base):
    __tablename__ = "sr_review_history"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    concept_id     = Column(String(100), nullable=False)
    quality        = Column(Integer, nullable=False)
    interval_after = Column(Integer, nullable=False)
    easiness_after = Column(Float, nullable=False)
    reviewed_at    = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# =============================================================
# DB Lifecycle & Dependency
# =============================================================

async def connect_db():
    """MySQL tables create karo."""
    print("MySQL se connect ho raha hai...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("MySQL connected aur Tables create ho gaye!")
    except Exception as e:
        print(f"CRITICAL ERROR (MySQL): {e}")

async def disconnect_db():
    """Connection band karo."""
    await engine.dispose()
    print("MySQL connection band ho gaya.")

async def get_db():
    """FastAPI Dependency for Session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()