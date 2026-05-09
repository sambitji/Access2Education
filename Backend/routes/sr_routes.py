# =============================================================
# backend/routes/sr_routes.py
# Edu-Platform — Spaced Repetition Routes (MySQL Version)
# =============================================================

import os, sys
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc

from database.db import get_db, User, SRCard, SRReviewHistory
from routes.auth import get_current_user
from ML.spaced_repetition import SM2Card, SpacedRepetitionEngine, Quality

router = APIRouter()

# =============================================================
# Pydantic Schemas
# =============================================================

class CardCreateRequest(BaseModel):
    concept_id: str
    subject: str
    concept_title: str

class ReviewRequest(BaseModel):
    concept_id: str
    quality: int = Field(..., ge=0, le=5)

# =============================================================
# Routes
# =============================================================

@router.post("/cards")
async def add_card(
    req: CardCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check existing
    result = await db.execute(select(SRCard).where(SRCard.user_id == current_user.id, SRCard.concept_id == req.concept_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Card pehle se deck mein hai")

    card = SRCard(
        user_id=current_user.id,
        concept_id=req.concept_id,
        subject=req.subject,
        concept_title=req.concept_title,
        learning_style=current_user.cluster_id or 0
    )
    db.add(card)
    await db.commit()
    return {"message": "Card added"}

@router.post("/review")
async def submit_review(
    req: ReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SRCard).where(SRCard.user_id == current_user.id, SRCard.concept_id == req.concept_id))
    card_row = result.scalar_one_or_none()
    if not card_row:
        raise HTTPException(status_code=404, detail="Card nahi mila")

    # ML SM-2 Logic
    sm2_card = SM2Card(
        concept_id=card_row.concept_id,
        user_id=str(card_row.user_id),
        subject=card_row.subject,
        concept_title=card_row.concept_title,
        interval=card_row.interval,
        easiness=card_row.easiness,
        repetition=card_row.repetition,
        next_review=card_row.next_review
    )
    
    updated_state = sm2_card.review(req.quality)
    
    # Update DB row
    card_row.interval = updated_state["interval"]
    card_row.easiness = updated_state["easiness"]
    card_row.repetition = updated_state["repetition"]
    card_row.next_review = updated_state["next_review"]
    
    # History log
    history = SRReviewHistory(
        user_id=current_user.id,
        concept_id=req.concept_id,
        quality=req.quality,
        interval_after=card_row.interval,
        easiness_after=card_row.easiness
    )
    db.add(history)
    
    await db.commit()
    return {"message": "Review recorded", "next_review": card_row.next_review.isoformat()}

@router.get("/due")
async def get_due_cards(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SRCard).where(SRCard.user_id == current_user.id))
    cards_rows = result.scalars().all()
    
    # Convert to SM2Card objects for the engine
    sm2_cards = [SM2Card(
        concept_id=c.concept_id, user_id=str(c.user_id), subject=c.subject, concept_title=c.concept_title,
        interval=c.interval, easiness=c.easiness, repetition=c.repetition, next_review=c.next_review
    ) for c in cards_rows]
    
    engine = SpacedRepetitionEngine(sm2_cards)
    due = engine.get_due_cards()
    
    return {"due_count": len(due), "cards": [c.to_dict() for c in due]}