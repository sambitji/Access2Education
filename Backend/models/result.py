# =============================================================
# backend/models/result.py
# Edu-Platform — Test Result & Score Database Models
#
# Models:
#   SectionScores         -> 5 aptitude sections ke scores
#   PerQuestionResult     -> Har question ka detailed result
#   TestResult            -> MongoDB mein store hone wala full result
#   TestSubmitRequest     -> Test submit karne ka request body
#   AnswerItem            -> Ek question ka answer
#   TestResultResponse    -> API response for latest result
#   TestHistoryItem       -> History list mein ek attempt
#   TestHistoryResponse   -> Poori history ka response
#   StyleDetails          -> Learning style ki detailed info
#   RetakeResponse        -> Retake eligibility response
# =============================================================

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


# =============================================================
# Enums
# =============================================================

class LearningStyleEnum(str, Enum):
    """ML model ke 4 clusters — test result mein assign hota hai."""
    VISUAL_LEARNER     = "visual_learner"
    CONCEPTUAL_THINKER = "conceptual_thinker"
    PRACTICE_BASED     = "practice_based"
    STEP_BY_STEP       = "step_by_step"


class SectionEnum(str, Enum):
    """Aptitude test ke 5 sections."""
    LOGICAL   = "logical"
    VERBAL    = "verbal"
    NUMERICAL = "numerical"
    MEMORY    = "memory"
    ATTENTION = "attention"


# =============================================================
# Model 1: SectionScores
# 5 sections ke normalized scores (0-100)
# =============================================================

class SectionScores(BaseModel):
    """
    Aptitude test ke 5 sections ke scores.
    Har score 0-100 ke beech hoga — normalized percentage.

    ML model inhi 5 values ko input ke roop mein leta hai
    aur cluster predict karta hai.
    """

    logical:   float = Field(..., ge=0, le=100, example=75.0,
                             description="Logical reasoning score — pattern, series, puzzles")
    verbal:    float = Field(..., ge=0, le=100, example=60.0,
                             description="Verbal ability score — comprehension, vocabulary, grammar")
    numerical: float = Field(..., ge=0, le=100, example=80.0,
                             description="Numerical ability score — arithmetic, percentage, ratio")
    memory:    float = Field(..., ge=0, le=100, example=100.0,
                             description="Memory retention score — recall, sequence, association")
    attention: float = Field(..., ge=0, le=100, example=40.0,
                             description="Attention span score — focus, detail, pattern spotting")
    total:     float = Field(..., ge=0, le=100, example=71.0,
                             description="Overall score — 5 sections ka weighted average")

    @model_validator(mode="after")
    def compute_total_if_missing(self):
        """Total automatically calculate karo agar nahi diya."""
        if self.total == 0:
            self.total = round(
                (self.logical + self.verbal + self.numerical + self.memory + self.attention) / 5, 1
            )
        return self

    @field_validator("logical", "verbal", "numerical", "memory", "attention", "total")
    @classmethod
    def round_to_one_decimal(cls, v):
        return round(v, 1)

    def to_ml_features(self) -> list[float]:
        """
        ML model ke liye ordered feature list banao.
        Order matter karta hai — scaler ne isi order mein train kiya tha.
        """
        return [self.logical, self.verbal, self.numerical, self.memory, self.attention]

    def dominant_section(self) -> str:
        """Sabse high score wala section kaun sa hai."""
        scores = {
            "logical":   self.logical,
            "verbal":    self.verbal,
            "numerical": self.numerical,
            "memory":    self.memory,
            "attention": self.attention,
        }
        return max(scores, key=scores.get)

    def weakest_section(self) -> str:
        """Sabse low score wala section kaun sa hai."""
        scores = {
            "logical":   self.logical,
            "verbal":    self.verbal,
            "numerical": self.numerical,
            "memory":    self.memory,
            "attention": self.attention,
        }
        return min(scores, key=scores.get)

    def performance_label(self) -> str:
        """Total score ke hisaab se performance label do."""
        if self.total >= 80:
            return "Excellent"
        elif self.total >= 60:
            return "Good"
        elif self.total >= 40:
            return "Average"
        else:
            return "Needs Improvement"


# =============================================================
# Model 2: PerQuestionResult
# Ek question ka detailed result — correct/incorrect aur marks
# =============================================================

class PerQuestionResult(BaseModel):
    """
    Test submit ke baad har question ka result.
    DB mein store hota hai — history mein exclude hota hai (bada hota hai).
    """

    question_id:     str  = Field(..., example="L1",
                                  description="Question ID — L1-L5, V1-V5, N1-N5, M1-M5, A1-A5")
    section:         str  = Field(..., example="logical",
                                  description="Kaun se section ka question tha")
    student_answer:  str  = Field(..., example="BQQMF",
                                  description="Student ne kya jawab diya")
    correct_answer:  str  = Field(..., example="BQQMF",
                                  description="Sahi jawab kya tha")
    is_correct:      bool = Field(..., example=True)
    marks_earned:    int  = Field(..., ge=0, le=20, example=20,
                                  description="Is question mein kitne marks mile — 20 ya 0")
    max_marks:       int  = Field(..., ge=0, le=20, example=20)

    @property
    def accuracy(self) -> float:
        """Is question pe accuracy percentage."""
        return 100.0 if self.is_correct else 0.0


# =============================================================
# Model 3: TestResult
# MongoDB mein store hone wala complete test result
# Collection name: "test_results"
# =============================================================

class TestResult(BaseModel):
    """
    Ek test attempt ka complete record — MongoDB mein store hota hai.

    MongoDB document structure:
    {
        "user_id":        "664abc123...",
        "attempt_number": 1,
        "scores": {
            "logical": 75.0, "verbal": 60.0,
            "numerical": 80.0, "memory": 100.0,
            "attention": 40.0, "total": 71.0
        },
        "cluster_id":     2,
        "learning_style": "practice_based",
        "per_question":   [...],
        "submitted_at":   "2024-03-15T10:30:00Z"
    }
    """

    user_id:        str                     = Field(...,
                                                    description="Student ka MongoDB ObjectId (string)")
    attempt_number: int                     = Field(..., ge=1,
                                                    example=1,
                                                    description="Pehla test = 1, dobara = 2, etc.")
    scores:         SectionScores           = Field(...,
                                                    description="5 sections ke scores + total")
    cluster_id:     int                     = Field(..., ge=0, le=3,
                                                    example=2,
                                                    description="KMeans ka output — 0, 1, 2, ya 3")
    learning_style: LearningStyleEnum       = Field(...,
                                                    example="practice_based",
                                                    description="Cluster ID se map kiya gaya style")
    per_question:   list[PerQuestionResult] = Field(default=[],
                                                    description="Har question ka detailed result")
    submitted_at:   datetime                = Field(default_factory=lambda: datetime.utcnow(),
                                                    description="Test kab submit kiya")

    class Config:
        use_enum_values = True


# =============================================================
# Model 4: AnswerItem
# Test submit ke waqt ek question ka answer
# =============================================================

class AnswerItem(BaseModel):
    """
    Student ka ek question ka answer.
    Test submit request mein 25 aise items aate hain.
    """

    question_id: str = Field(...,
                             example="L1",
                             description="Question ID — L1 se A5 tak")
    answer:      str = Field(...,
                             min_length=1,
                             max_length=200,
                             example="BQQMF",
                             description="Student ka chosen answer — options mein se ek")

    @field_validator("question_id")
    @classmethod
    def valid_question_id(cls, v):
        """Question ID valid format mein honi chahiye."""
        valid_prefixes = ("L", "V", "N", "M", "A")
        if not v or v[0] not in valid_prefixes:
            raise ValueError(
                f"Question ID '{v}' invalid hai. L, V, N, M, ya A se shuru hona chahiye."
            )
        return v.strip()

    @field_validator("answer")
    @classmethod
    def answer_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Answer empty nahi hona chahiye.")
        return v.strip()


# =============================================================
# Model 5: TestSubmitRequest
# POST /test/submit ka request body
# =============================================================

class TestSubmitRequest(BaseModel):
    """
    Student ke saare 25 answers ek saath submit hote hain.

    Example:
    {
        "answers": [
            {"question_id": "L1", "answer": "BQQMF"},
            {"question_id": "L2", "answer": "42"},
            ...  (25 total)
        ]
    }
    """

    answers: list[AnswerItem] = Field(
        ...,
        min_length=25,
        max_length=25,
        description="Saare 25 questions ke answers — ek bhi miss nahi hona chahiye"
    )

    @field_validator("answers")
    @classmethod
    def no_duplicate_question_ids(cls, v):
        """Ek question ID ek se zyada baar nahi aani chahiye."""
        ids = [a.question_id for a in v]
        duplicates = [qid for qid in ids if ids.count(qid) > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate question IDs mili hain: {set(duplicates)}. Har question ka answer ek hi baar dena hai."
            )
        return v

    @field_validator("answers")
    @classmethod
    def all_sections_present(cls, v):
        """
        Saare 5 sections ke questions hone chahiye:
        L1-L5, V1-V5, N1-N5, M1-M5, A1-A5
        """
        ids       = {a.question_id for a in v}
        sections  = {"L", "V", "N", "M", "A"}
        missing   = []

        for prefix in sections:
            for num in range(1, 6):
                qid = f"{prefix}{num}"
                if qid not in ids:
                    missing.append(qid)

        if missing:
            raise ValueError(
                f"Ye questions missing hain: {missing}. Saare 25 questions answer karne zaroori hain."
            )
        return v


# =============================================================
# Model 6: StyleDetails
# Learning style ki detailed information — result response mein
# =============================================================

class StyleDetails(BaseModel):
    """
    Predicted learning style ki poori information.
    Result response mein student ko dikhti hai.
    """

    title:         str       = Field(..., example="Practice-Based Learner ⚙️")
    description:   str       = Field(..., example="Tum karke seekhte ho — theory baad mein.")
    strengths:     list[str] = Field(..., example=["Haath se kaam karne mein maza aata hai"])
    content_types: list[str] = Field(..., example=["Coding exercises", "Mini projects"])
    study_tip:     str       = Field(..., example="Pehle problem try karo, phir solution dekho!")


# =============================================================
# Model 7: TestResultResponse
# GET /test/result ka API response
# =============================================================

class TestResultResponse(BaseModel):
    """
    Latest test result ka complete response.
    Student ko result page pe ye sab dikhega.
    """

    attempt_number:      int             = Field(..., ge=1, example=1)
    scores:              SectionScores   = Field(...,
                                                 description="Section-wise aur total score")
    cluster_id:          int             = Field(..., ge=0, le=3, example=2)
    learning_style:      LearningStyleEnum = Field(..., example="practice_based")
    style_details:       StyleDetails    = Field(...,
                                                 description="Learning style ki poori information")
    submitted_at:        str             = Field(..., example="2024-03-15T10:30:00Z")
    next_test_date:      str             = Field(..., example="2024-04-14",
                                                 description="Kab dobara test de sakte hain (30 din baad)")
    days_until_retake:   int             = Field(..., ge=0, example=28,
                                                 description="Kitne din aur baaki hain retake ke liye")
    can_retake:          bool            = Field(..., example=False,
                                                 description="Kya abhi retake allowed hai")

    # Helpful insights
    dominant_section:    str             = Field(..., example="numerical",
                                                 description="Sabse strong section")
    weakest_section:     str             = Field(..., example="attention",
                                                 description="Improvement ki zaroorat wala section")
    performance_label:   str             = Field(..., example="Good",
                                                 description="Excellent / Good / Average / Needs Improvement")

    class Config:
        use_enum_values = True


# =============================================================
# Model 8: TestHistoryItem
# History list mein ek attempt — per_question exclude hota hai
# =============================================================

class TestHistoryItem(BaseModel):
    """
    Test history mein ek attempt ka summary.
    Per-question detail exclude hoti hai — sirf scores aur style.
    """

    attempt_number: int               = Field(..., ge=1, example=1)
    scores:         SectionScores     = Field(...)
    learning_style: LearningStyleEnum = Field(..., example="practice_based")
    cluster_id:     int               = Field(..., ge=0, le=3, example=2)
    submitted_at:   str               = Field(..., example="2024-03-15T10:30:00Z")

    # Score comparison ke liye
    dominant_section:  str = Field(..., example="numerical")
    weakest_section:   str = Field(..., example="attention")
    performance_label: str = Field(..., example="Good")

    class Config:
        use_enum_values = True


# =============================================================
# Model 9: TestHistoryResponse
# GET /test/history ka poora response
# =============================================================

class TestHistoryResponse(BaseModel):
    """
    Student ke saare test attempts ka complete history.
    Progress track karne ke liye use hota hai.
    """

    total_attempts:  int                  = Field(..., ge=0, example=2)
    latest_style:    Optional[str]        = Field(None,  example="practice_based",
                                                  description="Latest test ka learning style")
    history:         list[TestHistoryItem] = Field(...,
                                                   description="Saare attempts — newest pehle")

    # Style change tracking
    style_changed:   bool                 = Field(False,
                                                  description="Latest aur pichle test ki style alag hai?")
    previous_style:  Optional[str]        = Field(None,
                                                  description="Pichle test ka learning style")

    @model_validator(mode="after")
    def check_style_change(self):
        """Agar 2+ attempts hain toh style change detect karo."""
        if len(self.history) >= 2:
            latest   = self.history[0].learning_style
            previous = self.history[1].learning_style
            self.style_changed  = (latest != previous)
            self.previous_style = previous
        return self


# =============================================================
# Model 10: RetakeResponse
# POST /test/retake ka response
# =============================================================

class RetakeResponse(BaseModel):
    """
    Retake eligibility check ka response.
    """

    message:         str           = Field(..., example="Retake allowed hai! Test pe jao.")
    can_retake:      bool          = Field(..., example=True)
    previous_style:  Optional[str] = Field(None, example="visual_learner",
                                           description="Pichli baar kya style assign hua tha")


# =============================================================
# Model 11: TestSubmitResponse
# POST /test/submit ka response
# =============================================================

class TestSubmitResponse(BaseModel):
    """
    Test submit karne ke baad ka complete response.
    """

    message:         str             = Field(...,
                                             example="Test submit ho gaya! Tumhara learning style pata chal gaya!")
    attempt_number:  int             = Field(..., ge=1, example=1)
    scores:          SectionScores   = Field(...)
    cluster_id:      int             = Field(..., ge=0, le=3, example=2)
    learning_style:  LearningStyleEnum = Field(..., example="practice_based")
    style_details:   StyleDetails    = Field(...)
    next_test_date:  str             = Field(..., example="2024-04-14",
                                             description="30 din baad dobara test de sakte hain")

    # Quick insights
    dominant_section:  str = Field(..., example="numerical")
    weakest_section:   str = Field(..., example="attention")
    performance_label: str = Field(..., example="Good")
    correct_answers:   int = Field(..., ge=0, le=25, example=18,
                                   description="Kitne questions sahi hue — 25 mein se")
    total_marks:       int = Field(..., ge=0, le=500, example=360,
                                   description="Total marks — 500 mein se")

    class Config:
        use_enum_values = True