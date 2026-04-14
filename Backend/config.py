# =============================================================
# backend/config.py
# Edu-Platform — Centralized Configuration
#
# Kya karta hai:
#   - Saari settings ek jagah manage karta hai
#   - .env file se values load karta hai
#   - Pydantic BaseSettings se automatic validation
#   - Har setting ka clear description aur default value
# =============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache
from typing import Optional, Union
import os


# =============================================================
# Settings Class
# =============================================================

class Settings(BaseSettings):
    """
    Poori application ki settings ek jagah.

    Values load hone ka order:
    1. .env file se (sabse pehle)
    2. Environment variables se
    3. Default values se (agar kuch nahi mila)

    Usage:
        from config import get_settings
        settings = get_settings()
        print(settings.DATABASE_NAME)
    """

    model_config = SettingsConfigDict(
        env_file         = ".env",        # .env file ka naam
        env_file_encoding= "utf-8",
        case_sensitive   = False,         # MONGODB_URL = mongodb_url — dono same
        extra            = "ignore",      # Extra variables ignore karo
    )

    # ──────────────────────────────────────────────────────────
    # App Settings
    # ──────────────────────────────────────────────────────────

    APP_NAME:        str  = Field(
        default="Edu-Platform",
        description="Application ka naam — API docs mein dikhega"
    )
    APP_VERSION:     str  = Field(
        default="1.0.0",
        description="API version"
    )
    APP_DESCRIPTION: str  = Field(
        default="AI-powered personalized learning platform",
        description="API ka short description"
    )
    DEBUG:           bool = Field(
        default=False,
        description="True karo toh detailed error messages milenge — sirf development mein"
    )
    PORT:            int  = Field(
        default=8000,
        ge=1000, le=65535,
        description="Server kis port pe chalega — default 8000"
    )

    # ──────────────────────────────────────────────────────────
    # MongoDB Settings
    # ──────────────────────────────────────────────────────────

    MONGODB_URL:       str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection string — local ya Atlas URL"
    )
    DATABASE_NAME:     str = Field(
        default="edu_platform",
        description="Database ka naam"
    )
    MONGO_MAX_POOL:    int = Field(
        default=10,
        ge=1, le=100,
        description="Maximum concurrent MongoDB connections"
    )
    MONGO_MIN_POOL:    int = Field(
        default=1,
        ge=1,
        description="Minimum open connections"
    )
    MONGO_TIMEOUT_MS:  int = Field(
        default=5000,
        ge=1000,
        description="Connection timeout milliseconds — 5 second default"
    )

    # Collection Names
    USERS_COLLECTION:          str = Field(default="users")
    TEST_RESULTS_COLLECTION:   str = Field(default="test_results")
    PROGRESS_COLLECTION:       str = Field(default="progress")
    REFRESH_TOKENS_COLLECTION: str = Field(default="refresh_tokens")
    OTPS_COLLECTION:           str = Field(default="otps")

    # ──────────────────────────────────────────────────────────
    # JWT Authentication Settings
    # ──────────────────────────────────────────────────────────

    SECRET_KEY:          str = Field(
        default="change-this-super-secret-key-in-production-min-32-chars",
        min_length=32,
        description="Access token sign karne ke liye secret key — production mein change karo"
    )
    REFRESH_SECRET_KEY:  str = Field(
        default="change-this-refresh-secret-key-in-production-min-32-chars",
        min_length=32,
        description="Refresh token ke liye alag secret key"
    )
    JWT_ALGORITHM:       str = Field(
        default="HS256",
        description="JWT signing algorithm — HS256 standard hai"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES:  int = Field(
        default=30,
        ge=5, le=1440,
        description="Access token kitne minutes mein expire hoga — default 30 min"
    )
    REFRESH_TOKEN_EXPIRE_DAYS:    int = Field(
        default=7,
        ge=1, le=30,
        description="Refresh token kitne din mein expire hoga — default 7 din"
    )

    # ──────────────────────────────────────────────────────────
    # CORS Settings
    # ──────────────────────────────────────────────────────────

    CORS_ORIGINS: Union[list[str], str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Frontend ke URLs jo backend se request kar sakte hain"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Cookies aur auth headers allow karo"
    )

    # ──────────────────────────────────────────────────────────
    # DeepSeek AI / Chatbot Settings
    # ──────────────────────────────────────────────────────────

    DEEPSEEK_API_KEY:    str = Field(
        default="",
        description="DeepSeek API key — deepseek.com se lo"
    )
    DEEPSEEK_API_URL:    str = Field(
        default="https://api.deepseek.com/v1/chat/completions",
        description="DeepSeek API endpoint"
    )
    DEEPSEEK_MODEL:      str = Field(
        default="deepseek-chat",
        description="Use karne wala model — deepseek-chat ya deepseek-coder"
    )
    DEEPSEEK_MAX_TOKENS: int = Field(
        default=1000,
        ge=100, le=4000,
        description="Chatbot response mein maximum tokens"
    )
    DEEPSEEK_TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0, le=2.0,
        description="Response creativity — 0 = deterministic, 2 = very creative"
    )

    # ──────────────────────────────────────────────────────────
    # ML Model Settings
    # ──────────────────────────────────────────────────────────

    # Vercel setup ke liye paths optimize karo
    ML_MODELS_PATH: str = Field(
        default="ML/models", # Root se default path
        description="ML model files ka path"
    )
    KMEANS_MODEL_FILE:  str = Field(default="kmeans_model.pkl")
    SCALER_FILE:        str = Field(default="scaler.pkl")
    CLUSTER_MAP_FILE:   str = Field(default="cluster_map.pkl")
    RETEST_COOLDOWN_DAYS: int = Field(
        default=30,
        ge=1, le=365,
        description="Student kitne din baad dobara aptitude test de sakta hai"
    )

    # ──────────────────────────────────────────────────────────
    # Email / OTP Settings
    # ──────────────────────────────────────────────────────────

    OTP_EXPIRE_MINUTES: int = Field(
        default=10,
        ge=1, le=60,
        description="OTP kitne minutes mein expire hoga — default 10 min"
    )
    OTP_LENGTH:         int = Field(
        default=6,
        ge=4, le=8,
        description="OTP kitne digits ka hoga — default 6"
    )

    # Email settings (production mein SMTP ya SendGrid use karo)
    EMAIL_HOST:     Optional[str] = Field(default=None, description="SMTP server — jaise smtp.gmail.com")
    EMAIL_PORT:     int           = Field(default=587,  description="SMTP port — 587 TLS ke liye")
    EMAIL_USERNAME: Optional[str] = Field(default=None, description="SMTP login email")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, description="SMTP password ya App Password")
    EMAIL_FROM:     str           = Field(
        default="noreply@edu-platform.com",
        description="Sent emails mein 'From' address"
    )
    EMAIL_ENABLED:  bool = Field(
        default=False,
        description="True karo toh real email bhejega — False pe sirf console mein print hoga"
    )

    # ──────────────────────────────────────────────────────────
    # Password Policy
    # ──────────────────────────────────────────────────────────

    PASSWORD_MIN_LENGTH:    int  = Field(default=8,  ge=6,  le=32)
    PASSWORD_MAX_LENGTH:    int  = Field(default=64, ge=16, le=256)
    PASSWORD_REQUIRE_UPPER: bool = Field(default=True,  description="Uppercase letter zaroori hai?")
    PASSWORD_REQUIRE_DIGIT: bool = Field(default=True,  description="Digit zaroori hai?")
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True, description="Special character zaroori hai?")

    # ──────────────────────────────────────────────────────────
    # Pagination Defaults
    # ──────────────────────────────────────────────────────────

    DEFAULT_PAGE_SIZE: int = Field(
        default=10,
        ge=1, le=100,
        description="Content list mein default items per page"
    )
    MAX_PAGE_SIZE:     int = Field(
        default=50,
        ge=10, le=200,
        description="Maximum items per page — zyada nahi"
    )

    # ──────────────────────────────────────────────────────────
    # Validators
    # ──────────────────────────────────────────────────────────

    @field_validator("SECRET_KEY", "REFRESH_SECRET_KEY")
    @classmethod
    def secret_keys_not_default(cls, v):
        """
        Production mein default secret keys nahi chalenge.
        DEBUG=False hone pe enforce hota hai.
        """
        weak_keys = {
            "change-this-super-secret-key-in-production-min-32-chars",
            "change-this-refresh-secret-key-in-production-min-32-chars",
        }
        # Sirf warn karo — production mein ye alag se handle karo
        if v in weak_keys:
            print("WARNING: Default secret key use ho rahi hai — production mein change karo!")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """
        .env mein CORS_ORIGINS comma-separated string bhi ho sakti hai:
        CORS_ORIGINS=http://localhost:5173,https://myapp.com
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ──────────────────────────────────────────────────────────
    # Computed Properties
    # ──────────────────────────────────────────────────────────

    @property
    def kmeans_model_path(self) -> str:
        """KMeans model file ka full path."""
        # Agar relative path kaam na kare, toh absolute dhundo
        path = os.path.join(self.ML_MODELS_PATH, self.KMEANS_MODEL_FILE)
        if not os.path.exists(path):
            # Try searching from Backend folder
            alt_path = os.path.join("..", self.ML_MODELS_PATH, self.KMEANS_MODEL_FILE)
            if os.path.exists(alt_path): return alt_path
        return path

    @property
    def scaler_path(self) -> str:
        """Scaler file ka full path."""
        return os.path.join(self.ML_MODELS_PATH, self.SCALER_FILE)

    @property
    def cluster_map_path(self) -> str:
        """Cluster map file ka full path."""
        return os.path.join(self.ML_MODELS_PATH, self.CLUSTER_MAP_FILE)

    @property
    def is_production(self) -> bool:
        """Production environment hai kya?"""
        return not self.DEBUG

    @property
    def mongodb_settings(self) -> dict:
        """Motor client ke liye MongoDB settings dict."""
        return {
            "serverSelectionTimeoutMS": self.MONGO_TIMEOUT_MS,
            "maxPoolSize":              self.MONGO_MAX_POOL,
            "minPoolSize":              self.MONGO_MIN_POOL,
        }


# =============================================================
# Singleton — Ek hi instance poori app mein
# lru_cache ensure karta hai settings ek baar load hon
# =============================================================

@lru_cache()
def get_settings() -> Settings:
    """
    Settings ka cached instance return karta hai.

    @lru_cache ki wajah se .env file sirf ek baar read hoti hai
    — har request pe nahi.

    Usage:
        from config import get_settings
        settings = get_settings()

        # Ya FastAPI dependency ke roop mein:
        from fastapi import Depends
        async def my_route(settings: Settings = Depends(get_settings)):
            ...
    """
    return Settings()


# =============================================================
# Quick Access — Import karke directly use karo
# =============================================================

# Ye line import karte hi settings load ho jaati hai
settings = get_settings()