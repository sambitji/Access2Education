"""
routes/spaced_repetition.py

Spaced Repetition API routes for EduPlatform.
Mount this in main.py with:
    from routes.spaced_repetition import router as sr_router
    app.include_router(sr_router, prefix="/api/spaced-repetition", tags=["Spaced Repetition"])
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import sys
import os

# Add Backend and Root to path for direct execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
if BACKEND_DIR not in sys.path: sys.path.append(BACKEND_DIR)

from ML.spaced_repetition import SM2Card, SpacedRepetitionEngine, Quality
from database.db import get_db
from routes.auth import get_current_user

router = APIRouter()


# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class CardCreateRequest(BaseModel):
    concept_id: str
    subject: str
    concept_title: str


class ReviewRequest(BaseModel):
    concept_id: str
    quality: int = Field(..., ge=0, le=5, description="SM-2 quality rating 0-5")


class BulkCreateRequest(BaseModel):
    concept_ids: list[str]
    subject: str


# ─── Helper: load user's cards from MongoDB ──────────────────────────────────

async def get_user_cards(user_id: str, db) -> list[SM2Card]:
    """Load all SR cards for a user from MongoDB."""
    docs = await db["sr_cards"].find({"user_id": user_id}).to_list(length=1000)
    return [SM2Card.from_dict(doc) for doc in docs]


async def get_user_learning_style(user_id: str, db) -> int:
    """Get user's ML-predicted learning style cluster."""
    result = await db["test_results"].find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]  # Most recent result
    )
    if result:
        return result.get("cluster", 0)
    return 0


# ─── Routes ──────────────────────────────────────────────────────────────────

@router.post("/cards", summary="Add a concept to user's SR deck")
async def add_card(
    req: CardCreateRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Add a new concept card to the user's spaced repetition deck.
    Called when a student marks a lesson as 'learned'.
    """
    user_id = str(current_user["_id"])
    
    # Check if card already exists
    existing = await db["sr_cards"].find_one({
        "user_id": user_id,
        "concept_id": req.concept_id
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Card already in your deck"
        )
    
    learning_style = await get_user_learning_style(user_id, db)
    
    card = SM2Card(
        concept_id=req.concept_id,
        user_id=user_id,
        subject=req.subject,
        concept_title=req.concept_title,
        learning_style=learning_style
    )
    
    await db["sr_cards"].insert_one(card.to_dict())
    return {"message": "Card added to your learning deck", "card": card.to_dict()}


@router.post("/review", summary="Submit a review for a concept")
async def submit_review(
    req: ReviewRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Submit a review result for a concept.
    Updates SM-2 state and schedules next review.
    """
    user_id = str(current_user["_id"])
    
    doc = await db["sr_cards"].find_one({
        "user_id": user_id,
        "concept_id": req.concept_id
    })
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found in your deck"
        )
    
    card = SM2Card.from_dict(doc)
    updated = card.review(req.quality)
    
    # Persist updated state
    await db["sr_cards"].update_one(
        {"user_id": user_id, "concept_id": req.concept_id},
        {"$set": updated}
    )
    
    # Log review history
    await db["sr_review_history"].insert_one({
        "user_id": user_id,
        "concept_id": req.concept_id,
        "quality": req.quality,
        "interval_after": card.interval,
        "easiness_after": card.easiness,
        "reviewed_at": datetime.utcnow().isoformat()
    })
    
    return {
        "message": "Review recorded",
        "next_review_in_days": card.interval,
        "next_review_date": card.next_review.isoformat(),
        "card": updated
    }


@router.get("/due", summary="Get cards due for review today")
async def get_due_cards(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Returns cards due for review, sorted by urgency score.
    Each card includes learning-style-aware review format.
    """
    user_id = str(current_user["_id"])
    cards = await get_user_cards(user_id, db)
    engine = SpacedRepetitionEngine(cards)
    due = engine.get_due_cards(limit=limit)
    
    return {
        "due_count": len(due),
        "cards": [c.to_dict() for c in due]
    }


@router.get("/schedule", summary="Get 7-day review schedule")
async def get_schedule(
    days: int = 7,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Returns upcoming review schedule — used by frontend calendar.
    """
    user_id = str(current_user["_id"])
    cards = await get_user_cards(user_id, db)
    engine = SpacedRepetitionEngine(cards)
    
    return {
        "schedule": engine.get_upcoming_schedule(days=days),
        "total_cards": len(cards)
    }


@router.get("/retention", summary="Get subject-wise retention heatmap")
async def get_retention_heatmap(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Returns per-subject retention stats for Learning DNA dashboard.
    """
    user_id = str(current_user["_id"])
    cards = await get_user_cards(user_id, db)
    engine = SpacedRepetitionEngine(cards)
    
    return {
        "heatmap": engine.get_retention_heatmap(),
        "streak_stats": engine.get_streak_stats()
    }


@router.get("/learning-dna", summary="Get full Learning DNA profile")
async def get_learning_dna(
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Aggregated learning profile for the shareable Learning DNA card.
    Combines SR stats + ML cluster + activity heatmap.
    """
    user_id = str(current_user["_id"])
    cards = await get_user_cards(user_id, db)
    engine = SpacedRepetitionEngine(cards)
    
    # Activity heatmap — last 52 weeks
    history = await db["sr_review_history"].find(
        {"user_id": user_id}
    ).sort("reviewed_at", -1).to_list(length=2000)
    
    # Group reviews by date
    activity = {}
    for entry in history:
        date_key = entry["reviewed_at"][:10]  # YYYY-MM-DD
        activity[date_key] = activity.get(date_key, 0) + 1
    
    # Get ML cluster label
    learning_style = await get_user_learning_style(user_id, db)
    style_labels = {
        0: "Visual Learner",
        1: "Conceptual Thinker",
        2: "Practice-Based",
        3: "Step-by-Step"
    }
    
    return {
        "user_id": user_id,
        "learning_style": learning_style,
        "learning_style_label": style_labels.get(learning_style, "Unknown"),
        "streak_stats": engine.get_streak_stats(),
        "retention_heatmap": engine.get_retention_heatmap(),
        "schedule_preview": engine.get_upcoming_schedule(days=7),
        "activity_heatmap": activity,  # date -> review_count
        "total_cards": len(cards),
        "due_today": len(engine.get_due_cards())
    }


@router.delete("/cards/{concept_id}", summary="Remove a card from deck")
async def remove_card(
    concept_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db)
):
    result = await db["sr_cards"].delete_one({
        "user_id": str(current_user["_id"]),
        "concept_id": concept_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"message": "Card removed from deck"}