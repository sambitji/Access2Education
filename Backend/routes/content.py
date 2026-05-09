# =============================================================
# backend/routes/content.py
# Edu-Platform — Content & Recommendation Routes (MySQL Version)
# =============================================================

import os, sys
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from typing import Optional, List

from database.db import get_db, User, Progress
from routes.auth import get_current_user, get_current_student
from ML.recommender import get_recommender, Recommender
from models import CompleteContentRequest, RateContentRequest

router = APIRouter(prefix="/content", tags=["Content & Recommendations"])

# =============================================================
# Routes
# =============================================================

@router.get("/recommendations")
async def get_recommendations(
    subject:      Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    difficulty:   Optional[int] = Query(None, ge=1, le=4),
    top_n:        int           = Query(6, ge=1, le=20),
    current_user: User          = Depends(get_current_student),
    db:           AsyncSession  = Depends(get_db),
    rec:          Recommender   = Depends(get_recommender),
):
    if not current_user.learning_style:
        raise HTTPException(status_code=400, detail="Pehle test do!")

    # Completed content fetch karo
    result = await db.execute(select(Progress.content_id).where(Progress.user_id == current_user.id, Progress.completed == True))
    completed_ids = [r[0] for r in result.all()]

    recs = rec.get_recommendations(
        learning_style=current_user.learning_style,
        completed_ids=completed_ids,
        completed_count=len(completed_ids),
        subject=subject,
        content_type=content_type,
        difficulty=difficulty,
        top_n=top_n
    )
    return recs

@router.get("/progress")
async def get_my_progress(
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
    rec: Recommender = Depends(get_recommender),
):
    result = await db.execute(select(Progress).where(Progress.user_id == current_user.id, Progress.completed == True).order_by(desc(Progress.last_accessed)))
    completed_records = result.scalars().all()
    
    total_available = len(rec.content_library)
    total_completed = len(completed_records)
    
    # Simple breakdown
    subject_stats = {}
    for r in completed_records:
        s = r.subject
        if s not in subject_stats: subject_stats[s] = 0
        subject_stats[s] += 1
        
    return {
        "learning_style": current_user.learning_style,
        "total_completed": total_completed,
        "total_available": total_available,
        "overall_percentage": round((total_completed / total_available) * 100, 1) if total_available > 0 else 0,
        "subject_stats": subject_stats
    }

@router.post("/complete/{content_id}")
async def mark_complete(
    content_id: str,
    body: CompleteContentRequest,
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
    rec: Recommender = Depends(get_recommender),
):
    content = rec.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content nahi mila")

    # Check existing
    result = await db.execute(select(Progress).where(Progress.user_id == current_user.id, Progress.content_id == content_id))
    existing = result.scalar_one_or_none()
    
    if existing and existing.completed:
        return {"message": "Pehle se complete hai"}

    if not existing:
        existing = Progress(user_id=current_user.id, content_id=content_id, subject=content["subject"])
        db.add(existing)
        
    existing.completed = True
    existing.score = 100 # Default
    current_user.total_completed += 1
    
    await db.commit()
    return {"message": f"'{content['title']}' complete!"}

@router.get("/all")
async def get_all_content(rec: Recommender = Depends(get_recommender)):
    return {"content": rec.content_library, "total": len(rec.content_library)}

@router.get("/subjects")
async def get_subjects(rec: Recommender = Depends(get_recommender)):
    return {"subjects": rec.get_all_subjects()}