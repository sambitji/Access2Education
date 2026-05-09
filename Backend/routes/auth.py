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
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import random
import string
import sys
import os

# Add Backend and Root to path for direct execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
if BACKEND_DIR not in sys.path: sys.path.append(BACKEND_DIR)

from limiter import limiter
from database.db import get_db, User, RefreshToken, OTP

# =============================================================
# Config
# =============================================================
SECRET_KEY           = "9825b4130d23589b27a3c3f87376c66cf01844b7067d0f1a92df55c421713e71"
REFRESH_SECRET_KEY   = "b8dffc24335f2bfc668b3b993b63fd8ce65a5f48f47f6bdfdab973a492df58b1"
ALGORITHM            = "HS256"
ACCESS_TOKEN_EXPIRE  = 30
REFRESH_TOKEN_EXPIRE = 7
OTP_EXPIRE_MINUTES   = 10

# ── Router ─────────────────────────────────────────────────────
router = APIRouter(prefix="/auth", tags=["Authentication"])

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
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


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


def format_user_response(user: User) -> dict:
    return {
        "id":             user.id,
        "name":           user.name,
        "email":          user.email,
        "role":           user.role,
        "avatar_url":     user.avatar_url,
        "learning_style": user.learning_style,
        "cluster_id":     user.cluster_id,
        "is_verified":    user.is_verified,
        "joined_at":      user.joined_at.isoformat() if user.joined_at else None,
    }


# =============================================================
# Dependencies
# =============================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token mein user ID nahi mila.")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User nahi mila.")
    return user


async def get_current_student(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Sirf students yahan access kar sakte hain.")
    return current_user


async def get_current_teacher(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "teacher":
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

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"'{body.email}' se already ek account exist karta hai.",
        )

    new_user = User(
        name=body.name.strip(),
        email=body.email.lower().strip(),
        password_hash=hash_password(body.password),
        role=body.role
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token_data    = {"sub": str(new_user.id), "role": new_user.role}
    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    new_rt = RefreshToken(
        user_id=new_user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE)
    )
    db.add(new_rt)
    await db.commit()

    return {
        "message":       f"Registration successful! Welcome, {new_user.name}",
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "user":          format_user_response(new_user),
    }


# =============================================================
# ROUTE 2 — LOGIN
# =============================================================

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credentials galat hain.")

    token_data    = {"sub": str(user.id), "role": user.role}
    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    new_rt = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE)
    )
    db.add(new_rt)
    await db.commit()

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
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username.lower()))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credentials galat hain.")
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


# =============================================================
# ROUTE 3 — REFRESH TOKEN
# =============================================================

@router.post("/refresh", summary="Refresh token se naya access token lo")
async def refresh_token_route(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(body.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise JWTError("Wrong type")
    except JWTError:
        raise HTTPException(status_code=401,
                            detail="Refresh token invalid ya expire ho gaya.")

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == body.refresh_token))
    stored = result.scalar_one_or_none()
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
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == body.refresh_token))
    refresh_token_obj = result.scalar_one_or_none()
    
    if not refresh_token_obj:
        raise HTTPException(status_code=400, detail="Token mila nahi.")
    
    await db.delete(refresh_token_obj)
    await db.commit()
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
        if not verify_password(body.old_password, current_user.password_hash):
            raise HTTPException(status_code=401,
                                detail="Purana password galat hai.")
        updates["password_hash"] = hash_password(body.new_password)

    if not updates:
        raise HTTPException(status_code=400, detail="Koi update field nahi di.")

    for key, value in updates.items():
        setattr(current_user, key, value)
    
    await db.commit()
    await db.refresh(current_user)

    return {"message": "Profile update ho gaya!", "user": format_user_response(current_user)}


# =============================================================
# ROUTE 7 — FORGOT PASSWORD
# =============================================================

@router.post("/forgot-password", summary="OTP email pe bhejo")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()
    if not user:
        return {"message": "Agar ye email registered hai toh OTP bhej diya gaya hai."}

    otp = generate_otp()
    
    # Delete existing OTP for this email
    result = await db.execute(select(OTP).where(OTP.email == body.email.lower()))
    existing_otp = result.scalar_one_or_none()
    if existing_otp:
        await db.delete(existing_otp)
    
    # Create new OTP
    new_otp = OTP(
        email=body.email.lower(),
        otp=otp,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES),
        used=False
    )
    db.add(new_otp)
    await db.commit()
    
    background_tasks.add_task(send_otp_email, body.email, otp, user.name)
    return {"message": "OTP bhej diya gaya hai. Inbox check karo. (10 min valid)"}


# =============================================================
# ROUTE 8 — RESET PASSWORD
# =============================================================

@router.post("/reset-password", summary="OTP se naya password set karo")
async def reset_password(
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(OTP).where(
            (OTP.email == body.email.lower()) & 
            (OTP.used == False)
        )
    )
    otp_record = result.scalar_one_or_none()
    
    if not otp_record:
        raise HTTPException(status_code=400,
                            detail="OTP nahi mila ya already use ho chuka hai.")

    if datetime.now(timezone.utc) > otp_record.expires_at:
        raise HTTPException(status_code=400,
                            detail="OTP expire ho gaya. Dobara try karo.")

    if otp_record.otp != body.otp:
        raise HTTPException(status_code=400, detail="OTP galat hai.")

    # Update password
    result = await db.execute(select(User).where(User.email == body.email.lower()))
    user = result.scalar_one_or_none()
    if user:
        user.password_hash = hash_password(body.new_password)
        await db.commit()
    
    # Mark OTP as used
    otp_record.used = True
    await db.commit()
    
    # Delete all refresh tokens for this user
    if user:
        result = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
        refresh_tokens = result.scalars().all()
        for rt in refresh_tokens:
            await db.delete(rt)
        await db.commit()

    return {"message": "Password reset ho gaya! Ab naye password se login karo."}