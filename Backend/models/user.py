# =============================================================
# backend/models/user.py
# Edu-Platform — User Database Models
#
# Models:
#   RoleEnum              -> Student ya Teacher
#   UserBase              -> Common fields — name, email, role
#   UserCreate            -> Signup request body
#   UserLogin             -> Login request body
#   UserInDB              -> MongoDB mein store hone wala document
#   UserResponse          -> API response — sensitive fields hate hue
#   UserUpdateRequest     -> Profile update request body
#   TokenData             -> JWT token ke andar ka data
#   TokenResponse         -> Login/Register ke baad milne wala response
#   ForgotPasswordRequest -> OTP bhejne ka request
#   ResetPasswordRequest  -> OTP se password reset karne ka request
#   OTPRecord             -> MongoDB mein OTP store karne ka model
#   RefreshTokenRecord    -> MongoDB mein refresh token store karne ka model
# =============================================================

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


# =============================================================
# Enums
# =============================================================

class RoleEnum(str, Enum):
    """Platform pe do types ke users hain."""
    STUDENT = "student"
    TEACHER = "teacher"


class LearningStyleEnum(str, Enum):
    """
    ML model ke 4 clusters.
    Pehle None hota hai — aptitude test ke baad set hota hai.
    """
    VISUAL_LEARNER     = "visual_learner"
    CONCEPTUAL_THINKER = "conceptual_thinker"
    PRACTICE_BASED     = "practice_based"
    STEP_BY_STEP       = "step_by_step"


# =============================================================
# Model 1: UserBase
# Common fields jo sabhi user models mein hain
# =============================================================

class UserBase(BaseModel):
    """
    Base model — sabhi user-related models isse inherit karte hain.
    Sirf common fields hain yahan.
    """

    name:  str       = Field(
        ...,
        min_length=2,
        max_length=60,
        example="Rahul Sharma",
        description="Student ya teacher ka poora naam"
    )
    email: EmailStr  = Field(
        ...,
        example="rahul@gmail.com",
        description="Unique email — login ke liye use hoga"
    )
    role:  RoleEnum  = Field(
        default=RoleEnum.STUDENT,
        example="student",
        description="'student' ya 'teacher' — default student hai"
    )

    @field_validator("name")
    @classmethod
    def name_no_special_chars(cls, v):
        """Naam mein sirf letters, spaces, dots aur hyphens allowed hain."""
        cleaned = v.strip()
        if not re.match(r"^[A-Za-z\s.\-']+$", cleaned):
            raise ValueError(
                "Naam mein sirf letters, spaces, dots aur hyphens allowed hain."
            )
        return cleaned

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        """Email hamesha lowercase mein store karo."""
        return v.lower().strip()

    class Config:
        use_enum_values = True


# =============================================================
# Model 2: UserCreate
# POST /auth/register ka request body
# =============================================================

class UserCreate(UserBase):
    """
    Naya user register karne ke liye request body.
    UserBase se inherit karta hai — password extra field hai.

    Password rules:
    - Minimum 8 characters
    - Kam se kam ek uppercase letter
    - Kam se kam ek digit
    - Kam se kam ek special character (@, #, $, %, &, !, ?)
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        example="StrongPass@123",
        description="Min 8 chars — ek uppercase, ek digit, ek special character zaroori"
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        errors = []
        if len(v) < 8:
            errors.append("Minimum 8 characters chahiye")
        if not any(c.isupper() for c in v):
            errors.append("Kam se kam ek uppercase letter chahiye (A-Z)")
        if not any(c.isdigit() for c in v):
            errors.append("Kam se kam ek digit chahiye (0-9)")
        if not any(c in "@#$%&!?" for c in v):
            errors.append("Kam se kam ek special character chahiye (@#$%&!?)")
        if errors:
            raise ValueError(" | ".join(errors))
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v):
        if v not in (RoleEnum.STUDENT.value, RoleEnum.TEACHER.value, "student", "teacher"):
            raise ValueError("Role sirf 'student' ya 'teacher' ho sakta hai")
        return v


# =============================================================
# Model 3: UserLogin
# POST /auth/login ka request body
# =============================================================

class UserLogin(BaseModel):
    """
    Login ke liye sirf email aur password chahiye.
    """

    email:    EmailStr = Field(
        ...,
        example="rahul@gmail.com"
    )
    password: str      = Field(
        ...,
        min_length=1,
        example="StrongPass@123"
    )

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        return v.lower().strip()


# =============================================================
# Model 4: UserInDB
# MongoDB mein store hone wala complete user document
# Collection name: "users"
# =============================================================

class UserInDB(UserBase):
    """
    Database mein store hone wala user document.
    Password hash form mein store hota hai — plain text kabhi nahi.

    MongoDB document structure:
    {
        "_id":            ObjectId("664abc123..."),
        "name":           "Rahul Sharma",
        "email":          "rahul@gmail.com",
        "password_hash":  "$2b$12$...",
        "role":           "student",
        "avatar_url":     "",
        "learning_style": "practice_based",
        "cluster_id":     2,
        "is_verified":    false,
        "total_completed": 5,
        "last_test_date": "2024-03-15T10:30:00Z",
        "needs_recluster": false,
        "joined_at":      "2024-01-10T08:00:00Z",
        "last_login":     "2024-03-15T09:00:00Z"
    }
    """

    password_hash:   str                         = Field(
        ...,
        description="bcrypt hashed password — plain text kabhi store nahi karte"
    )
    avatar_url:      str                         = Field(
        default="",
        example="https://example.com/avatars/rahul.jpg",
        description="Profile picture ka URL"
    )
    learning_style:  Optional[LearningStyleEnum] = Field(
        default=None,
        example="practice_based",
        description="ML model se assigned — aptitude test ke baad set hota hai"
    )
    cluster_id:      Optional[int]               = Field(
        default=None,
        ge=0, le=3,
        example=2,
        description="KMeans cluster number — 0, 1, 2, ya 3"
    )
    is_verified:     bool                        = Field(
        default=False,
        description="Email verified hai ya nahi"
    )
    total_completed: int                         = Field(
        default=0,
        ge=0,
        description="Abhi tak kitna content complete kiya — difficulty progression ke liye"
    )
    last_test_date:  Optional[datetime]          = Field(
        default=None,
        description="Aakhri baar aptitude test kab diya"
    )
    needs_recluster: bool                        = Field(
        default=False,
        description="30 din baad re-test ki zaroorat hai — flag"
    )
    joined_at:       datetime                    = Field(
        default_factory=datetime.utcnow,
        description="Account kab banaya"
    )
    last_login:      Optional[datetime]          = Field(
        default=None,
        description="Aakhri baar kab login kiya"
    )

    class Config:
        use_enum_values = True


# =============================================================
# Model 5: UserResponse
# API response — sensitive fields hate hue (password_hash, etc.)
# =============================================================

class UserResponse(BaseModel):
    """
    API ke responses mein user data is model se bheja jaata hai.
    Password hash aur internal fields yahan nahi hote.

    Ye wahi data hai jo frontend ko milta hai — /auth/me, login, register.
    """

    id:              str                         = Field(
        ...,
        example="664abc123def456ghi789",
        description="MongoDB ObjectId — string form mein"
    )
    name:            str                         = Field(..., example="Rahul Sharma")
    email:           EmailStr                    = Field(..., example="rahul@gmail.com")
    role:            RoleEnum                    = Field(..., example="student")
    avatar_url:      str                         = Field(default="", example="")
    learning_style:  Optional[LearningStyleEnum] = Field(
        default=None,
        example="practice_based",
        description="Aptitude test ke baad set hota hai — tab tak None"
    )
    cluster_id:      Optional[int]               = Field(default=None, example=2)
    is_verified:     bool                        = Field(default=False)
    total_completed: int                         = Field(default=0, ge=0)
    needs_recluster: bool                        = Field(default=False)
    joined_at:       str                         = Field(
        ...,
        example="2024-01-10T08:00:00Z",
        description="Account creation date — ISO format string"
    )

    class Config:
        use_enum_values = True


# =============================================================
# Model 6: UserUpdateRequest
# PUT /auth/me ka request body
# =============================================================

class UserUpdateRequest(BaseModel):
    """
    Profile update ke liye request body.
    Saari fields optional hain — sirf jo update karni ho woh bhejo.

    Password change ke liye old_password bhi dena zaroori hai.
    """

    name:         Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=60,
        example="Rahul Kumar Sharma",
        description="Naya naam"
    )
    avatar_url:   Optional[str] = Field(
        default=None,
        example="https://example.com/avatars/new.jpg",
        description="Naya profile picture URL"
    )
    old_password: Optional[str] = Field(
        default=None,
        example="OldPass@123",
        description="Password change ke liye purana password — verification ke liye"
    )
    new_password: Optional[str] = Field(
        default=None,
        min_length=8,
        max_length=64,
        example="NewStrongPass@456",
        description="Naya password — old_password ke saath dena zaroori hai"
    )

    @model_validator(mode="after")
    def password_change_validation(self):
        """
        Agar new_password diya hai toh old_password bhi zaroori hai.
        Agar old_password diya hai toh new_password bhi dena chahiye.
        """
        if self.new_password and not self.old_password:
            raise ValueError(
                "Password change karne ke liye 'old_password' bhi dena zaroori hai."
            )
        if self.old_password and not self.new_password:
            raise ValueError(
                "old_password ke saath 'new_password' bhi dena zaroori hai."
            )
        return self

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v):
        """New password bhi strong hona chahiye."""
        if v is None:
            return v
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("Kam se kam ek uppercase letter chahiye")
        if not any(c.isdigit() for c in v):
            errors.append("Kam se kam ek digit chahiye")
        if not any(c in "@#$%&!?" for c in v):
            errors.append("Kam se kam ek special character chahiye (@#$%&!?)")
        if errors:
            raise ValueError(" | ".join(errors))
        return v

    @field_validator("name")
    @classmethod
    def name_valid(cls, v):
        if v is None:
            return v
        cleaned = v.strip()
        if not re.match(r"^[A-Za-z\s.\-']+$", cleaned):
            raise ValueError("Naam mein sirf letters, spaces, dots aur hyphens allowed hain.")
        return cleaned

    @model_validator(mode="after")
    def at_least_one_field(self):
        """Koi na koi field toh honi chahiye update ke liye."""
        if not any([self.name, self.avatar_url, self.new_password]):
            raise ValueError(
                "Koi update field nahi di. name, avatar_url, ya new_password mein se kuch bhejo."
            )
        return self


# =============================================================
# Model 7: TokenData
# JWT token ke andar stored data
# =============================================================

class TokenData(BaseModel):
    """
    JWT token decode karne ke baad milne wala data.
    'sub' = user_id, 'role' = student/teacher, 'type' = access/refresh.
    """

    sub:  str           = Field(..., description="User ka MongoDB ObjectId")
    role: RoleEnum      = Field(..., description="Student ya teacher")
    type: str           = Field(..., description="'access' ya 'refresh'")
    exp:  Optional[int] = Field(default=None, description="Token expiry timestamp")

    class Config:
        use_enum_values = True


# =============================================================
# Model 8: TokenResponse
# POST /auth/login aur /auth/register ka response
# =============================================================

class TokenResponse(BaseModel):
    """
    Successful login ya registration ke baad milne wala response.
    Frontend in tokens ko store karta hai (localStorage ya cookies mein).
    """

    access_token:  str          = Field(
        ...,
        description="Short-lived JWT — 30 minutes valid — API calls mein use karo"
    )
    refresh_token: str          = Field(
        ...,
        description="Long-lived token — 7 days valid — naya access token lene ke liye"
    )
    token_type:    str          = Field(
        default="bearer",
        description="Hamesha 'bearer' hoga — Authorization header mein: 'Bearer <token>'"
    )
    user:          UserResponse = Field(
        ...,
        description="Logged-in user ki complete profile information"
    )


# =============================================================
# Model 9: ForgotPasswordRequest
# POST /auth/forgot-password ka request body
# =============================================================

class ForgotPasswordRequest(BaseModel):
    """
    Password bhoolne pe email bhejo — OTP milega.
    """

    email: EmailStr = Field(
        ...,
        example="rahul@gmail.com",
        description="Registered email address — OTP yahan aayega"
    )

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        return v.lower().strip()


# =============================================================
# Model 10: ResetPasswordRequest
# POST /auth/reset-password ka request body
# =============================================================

class ResetPasswordRequest(BaseModel):
    """
    OTP se password reset karne ke liye.
    Email + OTP + naya password — teeno zaroori hain.
    """

    email:        EmailStr = Field(
        ...,
        example="rahul@gmail.com"
    )
    otp:          str      = Field(
        ...,
        min_length=6,
        max_length=6,
        example="482931",
        description="Email pe aaya 6-digit OTP — 10 minute valid hota hai"
    )
    new_password: str      = Field(
        ...,
        min_length=8,
        max_length=64,
        example="NewStrongPass@456"
    )

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v):
        return v.lower().strip()

    @field_validator("otp")
    @classmethod
    def otp_numeric(cls, v):
        """OTP sirf digits mein hona chahiye."""
        if not v.isdigit():
            raise ValueError("OTP sirf numbers mein hona chahiye — jaise '482931'")
        return v

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v):
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("Kam se kam ek uppercase letter chahiye")
        if not any(c.isdigit() for c in v):
            errors.append("Kam se kam ek digit chahiye")
        if not any(c in "@#$%&!?" for c in v):
            errors.append("Kam se kam ek special character chahiye")
        if errors:
            raise ValueError(" | ".join(errors))
        return v


# =============================================================
# Model 11: OTPRecord
# MongoDB mein OTP store karne ka model
# Collection name: "otps"
# =============================================================

class OTPRecord(BaseModel):
    """
    Forgot password ke liye generate kiya gaya OTP — DB mein store hota hai.

    MongoDB document structure:
    {
        "email":      "rahul@gmail.com",
        "otp":        "482931",
        "created_at": "2024-03-15T10:00:00Z",
        "expires_at": "2024-03-15T10:10:00Z",
        "used":       false
    }
    """

    email:      str      = Field(..., description="Kis email pe OTP bheja")
    otp:        str      = Field(..., min_length=6, max_length=6,
                                  description="6-digit numeric OTP")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="OTP kab tak valid hai — 10 min baad expire")
    used:       bool     = Field(default=False,
                                  description="True ho jaata hai ek baar use hone ke baad — replay attack prevent")

    def is_expired(self) -> bool:
        """OTP expire ho gaya hai kya?"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self, input_otp: str) -> bool:
        """OTP sahi hai aur expire nahi hua?"""
        return (
            not self.used
            and not self.is_expired()
            and self.otp == input_otp
        )


# =============================================================
# Model 12: RefreshTokenRecord
# MongoDB mein refresh token store karne ka model
# Collection name: "refresh_tokens"
# =============================================================

class RefreshTokenRecord(BaseModel):
    """
    Active refresh tokens DB mein store hote hain.
    Logout pe delete hote hain — tab access token bhi invalid ho jaata hai.

    MongoDB document structure:
    {
        "user_id":    "664abc123...",
        "token":      "eyJhbGc...",
        "created_at": "2024-03-15T10:00:00Z",
        "expires_at": "2024-03-22T10:00:00Z"
    }
    """

    user_id:    str      = Field(..., description="Kis user ka refresh token hai")
    token:      str      = Field(..., description="Full refresh token string")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="7 din baad expire hoga")

    def is_expired(self) -> bool:
        """Refresh token expire ho gaya hai kya?"""
        return datetime.utcnow() > self.expires_at