# =============================================================
# backend/routes/auth.py
# Edu-Platform — Authentication Routes
#
# Endpoints:
#   POST /auth/register         -> New student / teacher signup
#   POST /auth/login            -> Login, returns JWT tokens
#   POST /auth/token            -> OAuth2 form login (Swagger UI)
#   POST /auth/refresh          -> Get new access token
#   POST /auth/logout           -> Invalidate refresh token
#   GET  /auth/me               -> Current user profile
#   PUT  /auth/me               -> Update profile / password
#   POST /auth/forgot-password  -> Send OTP to email
#   POST /auth/reset-password   -> Reset password with OTP
# =============================================================

from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase
import random
import string
from limiter import limiter

from database.db import get_db

# Config se keys lo
try:
    from config import settings
    SECRET_KEY           = settings.SECRET_KEY
    REFRESH_SECRET_KEY   = settings.REFRESH_SECRET_KEY
    ALGORITHM            = settings.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE  = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE = settings.REFRESH_TOKEN_EXPIRE_DAYS
    OTP_EXPIRE_MINUTES   = settings.OTP_EXPIRE_MINUTES
except Exception:
    SECRET_KEY           = "change-this-super-secret-key-in-production-min-32-chars"
    REFRESH_SECRET_KEY   = "change-this-refresh-secret-key-in-production-min-32-chars"
    ALGORITHM            = "HS256"
    ACCESS_TOKEN_EXPIRE  = 30
    REFRESH_TOKEN_EXPIRE = 7
    OTP_EXPIRE_MINUTES   = 10

# ── Router ─────────────────────────────────────────────────────
router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# =============================================================
# Pydantic Schemas
# =============================================================

class RegisterRequest(BaseModel):
    name:     str      = Field(..., min_length=2,  max_length=60,  example="Rahul Sharma")
    email:    EmailStr = Field(...,                                 example="rahul@gmail.com")
    password: str      = Field(..., min_length=8,  max_length=64,  example="StrongPass@123")
    role:     str      = Field("student",                          example="student")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password mein kam se kam ek uppercase letter hona chahiye")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password mein kam se kam ek digit honi chahiye")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v):
        if v not in ("student", "teacher"):
            raise ValueError("Role sirf 'student' ya 'teacher' ho sakta hai")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    user:          dict


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    name:         Optional[str] = Field(None, min_length=2, max_length=60)
    avatar_url:   Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email:        EmailStr
    otp:          str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)


# =============================================================
# Utility Functions
# =============================================================

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"]  = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    payload["type"] = "access"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"]  = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE)
    payload["type"] = "refresh"
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise JWTError("Wrong token type")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid ya expire ho gaya hai. Dobara login karo.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def format_user_response(user: dict) -> dict:
    return {
        "id":             str(user["_id"]),
        "name":           user["name"],
        "email":          user["email"],
        "role":           user["role"],
        "avatar_url":     user.get("avatar_url", ""),
        "learning_style": user.get("learning_style", None),
        "cluster_id":     user.get("cluster_id", None),
        "is_verified":    user.get("is_verified", False),
        "joined_at": (
            user["joined_at"].isoformat()
            if isinstance(user.get("joined_at"), datetime)
            else user.get("joined_at", "")
        ),
    }


# =============================================================
# Dependencies
# =============================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> dict:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token mein user ID nahi mili.")

    from bson import ObjectId
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila.")
    return user


async def get_current_student(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Sirf students yahan access kar sakte hain.")
    return current_user


async def get_current_teacher(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Sirf teachers yahan access kar sakte hain.")
    return current_user


# =============================================================
# Background Task — OTP Email
# =============================================================

async def send_otp_email(email: str, otp: str, name: str):
    """
    Production mein SMTP/SendGrid se replace karo.
    Abhi console pe print karta hai.
    """
    print(f"\n{'='*50}")
    print(f"  OTP EMAIL  (Simulated)")
    print(f"  To   : {email}")
    print(f"  Name : {name}")
    print(f"  OTP  : {otp}   (valid {OTP_EXPIRE_MINUTES} min)")
    print(f"{'='*50}\n")


# =============================================================
# ROUTE 1 — REGISTER
# =============================================================

@router.post("/register", status_code=status.HTTP_201_CREATED,
             summary="Naya student ya teacher register karo")
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    existing = await db["users"].find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{body.email}' se already ek account exist karta hai.",
        )

    new_user = {
        "name":           body.name.strip(),
        "email":          body.email.lower().strip(),
        "password_hash":  hash_password(body.password),
        "role":           body.role,
        "avatar_url":     "",
        "learning_style": None,
        "cluster_id":     None,
        "is_verified":    False,
        "total_completed": 0,
        "joined_at":      datetime.now(timezone.utc),
        "last_login":     None,
    }

    result        = await db["users"].insert_one(new_user)
    new_user["_id"] = result.inserted_id

    token_data    = {"sub": str(result.inserted_id), "role": body.role}
    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    await db["refresh_tokens"].insert_one({
        "user_id":    str(result.inserted_id),
        "token":      refresh_token,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE),
    })

    return {
        "message":       f"Registration successful! Welcome, {body.name}",
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "user":          format_user_response(new_user),
    }


# =============================================================
# ROUTE 2 — LOGIN
# =============================================================

@router.post("/login", response_model=TokenResponse,
             summary="Email + password se login karo")
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = await db["users"].find_one({"email": body.email.lower()})
    if not user:
        raise HTTPException(status_code=404,
                            detail="Is email se koi account nahi mila.")

    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401,
                            detail="Password galat hai.")

    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}},
    )

    token_data    = {"sub": str(user["_id"]), "role": user["role"]}
    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    await db["refresh_tokens"].delete_many({"user_id": str(user["_id"])})
    await db["refresh_tokens"].insert_one({
        "user_id":    str(user["_id"]),
        "token":      refresh_token,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE),
    })

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "user":          format_user_response(user),
    }


# =============================================================
# ROUTE 2b — OAuth2 Form Login (Swagger UI)
# =============================================================

@router.post("/token", include_in_schema=False)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = await db["users"].find_one({"email": form_data.username.lower()})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credentials galat hain.")
    access_token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}


# =============================================================
# ROUTE 3 — REFRESH TOKEN
# =============================================================

@router.post("/refresh", summary="Refresh token se naya access token lo")
async def refresh_token_route(
    body: RefreshRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        payload = jwt.decode(body.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise JWTError("Wrong type")
    except JWTError:
        raise HTTPException(status_code=401,
                            detail="Refresh token invalid ya expire ho gaya.")

    stored = await db["refresh_tokens"].find_one({"token": body.refresh_token})
    if not stored:
        raise HTTPException(status_code=401,
                            detail="Refresh token revoke ho chuka hai.")

    access_token = create_access_token({
        "sub":  payload.get("sub"),
        "role": payload.get("role"),
    })
    return {"access_token": access_token, "token_type": "bearer"}


# =============================================================
# ROUTE 4 — LOGOUT
# =============================================================

@router.post("/logout", summary="Logout — refresh token invalidate")
async def logout(
    body: RefreshRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    result = await db["refresh_tokens"].delete_one({"token": body.refresh_token})
    if result.deleted_count == 0:
        raise HTTPException(status_code=400, detail="Token mila nahi.")
    return {"message": "Successfully logout ho gaye!"}


# =============================================================
# ROUTE 5 — GET MY PROFILE
# =============================================================

@router.get("/me", summary="Apna profile dekho (protected)")
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
):
    return {"user": format_user_response(current_user)}


# =============================================================
# ROUTE 6 — UPDATE PROFILE
# =============================================================

@router.put("/me", summary="Profile update karo")
async def update_profile(
    body: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    updates = {}
    if body.name:
        updates["name"] = body.name.strip()
    if body.avatar_url:
        updates["avatar_url"] = body.avatar_url
    if body.new_password:
        if not body.old_password:
            raise HTTPException(status_code=400,
                                detail="Purana password bhi dena padega.")
        if not verify_password(body.old_password, current_user["password_hash"]):
            raise HTTPException(status_code=401,
                                detail="Purana password galat hai.")
        updates["password_hash"] = hash_password(body.new_password)

    if not updates:
        raise HTTPException(status_code=400, detail="Koi update field nahi di.")

    await db["users"].update_one({"_id": current_user["_id"]}, {"$set": updates})
    updated_user = await db["users"].find_one({"_id": current_user["_id"]})

    return {"message": "Profile update ho gaya!", "user": format_user_response(updated_user)}


# =============================================================
# ROUTE 7 — FORGOT PASSWORD
# =============================================================

@router.post("/forgot-password", summary="OTP email pe bhejo")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = await db["users"].find_one({"email": body.email.lower()})
    if not user:
        return {"message": "Agar ye email registered hai toh OTP bhej diya gaya hai."}

    otp = generate_otp()
    await db["otps"].update_one(
        {"email": body.email.lower()},
        {"$set": {
            "email":      body.email.lower(),
            "otp":        otp,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
            "used":       False,
        }},
        upsert=True,
    )
    background_tasks.add_task(send_otp_email, body.email, otp, user["name"])
    return {"message": "OTP bhej diya gaya hai. Inbox check karo. (10 min valid)"}


# =============================================================
# ROUTE 8 — RESET PASSWORD
# =============================================================

@router.post("/reset-password", summary="OTP se naya password set karo")
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    otp_record = await db["otps"].find_one({"email": body.email.lower(), "used": False})
    if not otp_record:
        raise HTTPException(status_code=400,
                            detail="OTP nahi mila ya already use ho chuka hai.")

    expires_at = otp_record["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400,
                            detail="OTP expire ho gaya. Dobara try karo.")

    if otp_record["otp"] != body.otp:
        raise HTTPException(status_code=400, detail="OTP galat hai.")

    await db["users"].update_one(
        {"email": body.email.lower()},
        {"$set": {"password_hash": hash_password(body.new_password)}},
    )
    await db["otps"].update_one(
        {"email": body.email.lower()},
        {"$set": {"used": True}},
    )

    user = await db["users"].find_one({"email": body.email.lower()})
    if user:
        await db["refresh_tokens"].delete_many({"user_id": str(user["_id"])})

    return {"message": "Password reset ho gaya! Ab naye password se login karo."}