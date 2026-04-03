# =============================================================
# backend/models/content.py
# Edu-Platform — Content & Progress Database Models
#
# Models:
#   ContentItem       -> Content library ka ek item
#   ContentProgress   -> Student ne content complete kiya / rating di
#   ContentFilter     -> API filtering ke liye query params
#   RecommendedItem   -> Recommendation response mein ek item
#   RecommendationResponse -> /recommendations endpoint ka full response
#   CompleteContentRequest -> Content complete karne ka request body
#   RateContentRequest     -> Rating dene ka request body
#   SearchResponse         -> Search results ka response
# =============================================================

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


# =============================================================
# Enums — Fixed Values
# =============================================================

class SubjectEnum(str, Enum):
    """Platform pe available subjects."""
    PYTHON      = "Python"
    DSA         = "DSA"
    ML          = "ML"
    MATHEMATICS = "Mathematics"
    WEB_DEV     = "Web Dev"
    DBMS        = "DBMS"


class ContentTypeEnum(str, Enum):
    """Content kis format mein hai."""
    VIDEO       = "video"        # Visual learners ke liye best
    ARTICLE     = "article"      # Conceptual thinkers ke liye
    EXERCISE    = "exercise"     # Practice-based ke liye
    NOTES       = "notes"        # Step-by-step ke liye
    INFOGRAPHIC = "infographic"  # Visual learners ke liye
    TUTORIAL    = "tutorial"     # Step-by-step ke liye
    PROJECT     = "project"      # Practice-based ke liye


class DifficultyEnum(int, Enum):
    """Content ka difficulty level."""
    BEGINNER     = 1   # Bilkul naya topic
    EASY_MEDIUM  = 2   # Thoda basics pata ho
    MEDIUM_HARD  = 3   # Practice chahiye
    ADVANCED     = 4   # Deep knowledge required


class LearningStyleEnum(str, Enum):
    """ML model ke 4 clusters."""
    VISUAL_LEARNER     = "visual_learner"
    CONCEPTUAL_THINKER = "conceptual_thinker"
    PRACTICE_BASED     = "practice_based"
    STEP_BY_STEP       = "step_by_step"


# =============================================================
# Model 1: ContentItem
# JSON file ka ek content entry represent karta hai
# =============================================================

class ContentItem(BaseModel):
    """
    content_metadata.json ka ek item.
    Content library mein store hota hai — MongoDB mein nahi.
    """

    content_id:    str             = Field(...,  example="C001",
                                           description="Unique content ID — C001 se C044")
    title:         str             = Field(...,  min_length=5,  max_length=150,
                                           example="Python Variables Animated Video")
    subject:       SubjectEnum     = Field(...,  example="Python",
                                           description="Kaun se subject ka content hai")
    type:          ContentTypeEnum = Field(...,  example="video",
                                           description="Content format — video, article, etc.")
    difficulty:    DifficultyEnum  = Field(...,  example=1,
                                           description="1=Beginner, 2=Easy, 3=Medium, 4=Hard")
    duration_min:  int             = Field(...,  ge=1, le=300,
                                           example=12,
                                           description="Content complete karne ke liye approximate minutes")
    tags:          list[str]       = Field(...,  min_length=1,
                                           example=["visual", "animation", "basics"],
                                           description="Recommendation scoring ke liye keywords")
    description:   str             = Field(...,  min_length=10, max_length=500,
                                           example="Variables aur data assignment animated visuals ke zariye.",
                                           description="Content ka short summary — chatbot bhi use karta hai")
    url:           str             = Field(...,  example="https://example.com/content/C001",
                                           description="Actual content ka link")
    thumbnail:     str             = Field(...,  example="https://example.com/thumbnails/C001.jpg",
                                           description="Dashboard pe dikhne wali preview image")
    suitable_for:  list[LearningStyleEnum] = Field(
                                           ...,
                                           example=["visual_learner", "step_by_step"],
                                           description="Kaun se learning styles ke liye best hai")
    prerequisites: list[str]       = Field(default=[],
                                           example=["C001", "C002"],
                                           description="Pehle ye content complete karo — tab ye recommend hoga")
    created_at:    str             = Field(...,  example="2024-01-10",
                                           description="Content kab add kiya gaya")

    @field_validator("tags")
    @classmethod
    def tags_lowercase(cls, v):
        """Tags lowercase mein hone chahiye recommendation scoring ke liye."""
        return [tag.lower().strip() for tag in v]

    @field_validator("content_id")
    @classmethod
    def valid_content_id(cls, v):
        """content_id 'C' se shuru hona chahiye."""
        if not v.startswith("C"):
            raise ValueError("content_id 'C' se shuru hona chahiye, jaise C001")
        return v

    class Config:
        use_enum_values = True


# =============================================================
# Model 2: ContentProgress
# MongoDB mein store hota hai — student ki progress track karta hai
# Collection name: "progress"
# =============================================================

class ContentProgress(BaseModel):
    """
    Ek student ne ek content ke saath kya kiya — DB mein store hota hai.

    MongoDB document structure:
    {
        "user_id":        "664abc123...",
        "content_id":     "C001",
        "subject":        "Python",
        "content_type":   "video",
        "difficulty":     1,
        "completed":      true,
        "completed_at":   "2024-03-15T10:30:00Z",
        "time_spent_min": 14,
        "notes":          "Variables mein int aur float ka difference samjha",
        "rating":         5,
        "comment":        "Bahut achha video tha!",
        "rated_at":       "2024-03-15T10:45:00Z"
    }
    """

    user_id:         str                    = Field(..., description="Student ka MongoDB ObjectId (string)")
    content_id:      str                    = Field(..., example="C001")
    subject:         Optional[str]          = Field(None, example="Python")
    content_type:    Optional[str]          = Field(None, example="video")
    difficulty:      Optional[int]          = Field(None, ge=1, le=4)

    # Completion fields
    completed:       bool                   = Field(False)
    completed_at:    Optional[datetime]     = Field(None)
    time_spent_min:  Optional[int]          = Field(None, ge=0,
                                                    description="Student ne kitne minute is content mein lagaye")
    notes:           Optional[str]          = Field(None, max_length=500,
                                                    description="Student ke apne notes ya observations")

    # Rating fields (sirf completed content pe)
    rating:          Optional[int]          = Field(None, ge=1, le=5,
                                                    description="1 se 5 stars")
    comment:         Optional[str]          = Field(None, max_length=300)
    rated_at:        Optional[datetime]     = Field(None)

    @field_validator("rating")
    @classmethod
    def rating_only_if_completed(cls, v):
        """Rating 1-5 ke beech honi chahiye."""
        if v is not None and not (1 <= v <= 5):
            raise ValueError("Rating 1 se 5 ke beech honi chahiye")
        return v

    class Config:
        use_enum_values = True


# =============================================================
# Model 3: ContentFilter
# GET /content/all ke query parameters validate karta hai
# =============================================================

class ContentFilter(BaseModel):
    """
    Content list ke liye filtering options.
    Routes mein Query() se aate hain — directly use nahi hota usually.
    """

    subject:    Optional[SubjectEnum]     = Field(None, description="Subject filter")
    type:       Optional[ContentTypeEnum] = Field(None, description="Content type filter")
    difficulty: Optional[DifficultyEnum]  = Field(None, description="Difficulty filter")
    page:       int                       = Field(1,    ge=1,       description="Page number")
    limit:      int                       = Field(10,   ge=1, le=50, description="Items per page")

    class Config:
        use_enum_values = True


# =============================================================
# Model 4: RecommendedItem
# Recommendation list mein ek item — score ke saath
# =============================================================

class RecommendedItem(BaseModel):
    """
    /recommendations endpoint mein har recommended content item.
    ContentItem ke saath recommendation_score aur prerequisites_met add hota hai.
    """

    content_id:             str             = Field(..., example="C001")
    title:                  str             = Field(..., example="Python Variables Animated Video")
    subject:                str             = Field(..., example="Python")
    type:                   str             = Field(..., example="video")
    difficulty:             int             = Field(..., example=1)
    duration_min:           int             = Field(..., example=12)
    tags:                   list[str]       = Field(...)
    description:            str             = Field(...)
    url:                    str             = Field(...)
    thumbnail:              str             = Field(...)
    suitable_for:           list[str]       = Field(...)
    prerequisites:          list[str]       = Field(default=[])

    # Recommendation-specific fields
    recommendation_score:   float           = Field(..., ge=0, le=100,
                                                    example=80.0,
                                                    description="ML scoring se mila hua score — higher = better match")
    prerequisites_met:      bool            = Field(...,
                                                    description="Saare prerequisites complete hain ya nahi")


# =============================================================
# Model 5: RecommendationResponse
# GET /content/recommendations ka poora response
# =============================================================

class RecommendationResponse(BaseModel):
    """
    Recommendation endpoint ka complete response body.
    """

    learning_style:    LearningStyleEnum  = Field(...,  example="visual_learner")
    description:       str                = Field(...,  example="Diagrams aur visuals se best seekhte ho tum.")
    study_tip:         str                = Field(...,  example="Mind maps banao!")
    completed_count:   int                = Field(...,  ge=0, example=5,
                                                       description="Abhi tak kitna content complete kiya")
    total_recommended: int                = Field(...,  ge=0, example=6)
    recommendations:   list[RecommendedItem] = Field(...)

    class Config:
        use_enum_values = True


# =============================================================
# Model 6: CompleteContentRequest
# POST /content/complete/{content_id} ka request body
# =============================================================

class CompleteContentRequest(BaseModel):
    """
    Student content complete karta hai — optional fields ke saath.
    """

    time_spent_min: Optional[int] = Field(
        None,
        ge=0, le=300,
        example=14,
        description="Kitne minute is content mein lagaye (0-300)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        example="Variables mein int aur float ka difference samjha",
        description="Student ke apne notes — future reference ke liye"
    )


# =============================================================
# Model 7: RateContentRequest
# POST /content/rate/{content_id} ka request body
# =============================================================

class RateContentRequest(BaseModel):
    """
    Student content ko rating deta hai.
    Pehle content complete karna zaroori hai.
    """

    rating: int = Field(
        ...,
        ge=1, le=5,
        example=5,
        description="1 = Bahut bura, 5 = Bahut achha"
    )
    comment: Optional[str] = Field(
        None,
        max_length=300,
        example="Bahut achha samjhaya gaya! Animation se concept ekdum clear ho gayi.",
        description="Optional feedback — kyun ye rating di"
    )

    @field_validator("rating")
    @classmethod
    def rating_in_range(cls, v):
        if not (1 <= v <= 5):
            raise ValueError("Rating 1 se 5 ke beech honi chahiye")
        return v


# =============================================================
# Model 8: ContentDetailResponse
# GET /content/{content_id} ka response
# =============================================================

class MyProgressDetail(BaseModel):
    """Ek content ke saath student ki apni progress."""
    completed:       bool            = False
    completed_at:    Optional[str]   = None
    time_spent_min:  Optional[int]   = None
    my_rating:       Optional[int]   = None
    my_notes:        Optional[str]   = None


class ContentDetailResponse(BaseModel):
    """
    Single content detail page ka response.
    Content info + ratings + student ki apni progress.
    """
    content:      ContentItem       = Field(..., description="Content ki poori information")
    avg_rating:   Optional[float]   = Field(None, example=4.3,
                                            description="Saare students ka average rating")
    rating_count: int               = Field(0,    description="Kitne students ne rate kiya")
    my_progress:  MyProgressDetail  = Field(...,  description="Is student ki is content ke saath progress")


# =============================================================
# Model 9: ProgressResponse
# GET /content/progress ka poora response
# =============================================================

class SubjectProgress(BaseModel):
    """Ek subject ki progress details."""
    completed:   int   = Field(..., ge=0, example=3)
    total:       int   = Field(..., ge=0, example=8)
    percentage:  float = Field(..., ge=0, le=100, example=37.5)


class RecentlyCompleted(BaseModel):
    """Recently complete kiya hua ek content."""
    content_id:   str = Field(...)
    title:        str = Field(...)
    subject:      str = Field(...)
    completed_at: str = Field(...)


class ProgressResponse(BaseModel):
    """
    Student ka complete learning progress dashboard.
    """
    learning_style:      Optional[str]                    = Field(None)
    total_completed:     int                              = Field(..., ge=0)
    total_available:     int                              = Field(..., ge=0)
    overall_percentage:  float                            = Field(..., ge=0, le=100)
    subject_breakdown:   dict[str, SubjectProgress]       = Field(...)
    recently_completed:  list[RecentlyCompleted]          = Field(...)
    completed_ids:       list[str]                        = Field(...)


# =============================================================
# Model 10: SearchResponse
# GET /content/search ka response
# =============================================================

class SearchResponse(BaseModel):
    """Content search results."""
    query:   str              = Field(..., example="python variables")
    total:   int              = Field(..., ge=0)
    results: list[ContentItem] = Field(...)


# =============================================================
# Model 11: SubjectInfo
# GET /content/subjects mein ek subject ki info
# =============================================================

class SubjectInfo(BaseModel):
    """Ek subject ki summary — frontend dropdown ke liye."""
    subject:       str       = Field(..., example="Python")
    total_content: int       = Field(..., ge=0, example=8)
    types:         list[str] = Field(..., example=["video", "article", "exercise"])


class SubjectsResponse(BaseModel):
    """GET /content/subjects ka response."""
    subjects: list[SubjectInfo] = Field(...)
    total:    int               = Field(..., ge=0)