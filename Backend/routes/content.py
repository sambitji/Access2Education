# =============================================================
# backend/routes/content.py
# Edu-Platform — Content & Recommendation Routes
# =============================================================

import sys
import os

# Add Backend and Root to path for direct execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
if BACKEND_DIR not in sys.path: sys.path.append(BACKEND_DIR)

from fastapi import APIRouter, HTTPException, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

from database.db import get_db
from routes.auth import get_current_user, get_current_student
from ML.recommender import get_recommender, Recommender

router = APIRouter(prefix="/content", tags=["Content & Recommendations"])

from models import CompleteContentRequest, RateContentRequest


# =============================================================
# ROUTE 1 — RECOMMENDATIONS
# =============================================================

@router.get("/recommendations",
            summary="Personalized content recommendations")
async def get_recommendations(
    subject:      Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    difficulty:   Optional[int] = Query(None, ge=1, le=4),
    top_n:        int           = Query(6, ge=1, le=20),
    current_user: dict          = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
    rec:          Recommender   = Depends(get_recommender),
):
    learning_style = current_user.get("learning_style")
    if not learning_style:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pehle aptitude test do! /test/questions pe jao.",
        )

    completed_records = await db["progress"].find(
        {"user_id": str(current_user["_id"]), "completed": True},
        {"content_id": 1},
    ).to_list(None)

    completed_ids   = [r["content_id"] for r in completed_records]
    completed_count = len(completed_ids)

    result = rec.get_recommendations(
        learning_style  = learning_style,
        completed_ids   = completed_ids,
        completed_count = completed_count,
        subject         = subject,
        content_type    = content_type,
        difficulty      = difficulty,
        top_n           = top_n,
    )
    return result


# =============================================================
# ROUTE 2 — ALL CONTENT
# =============================================================

@router.get("/all", summary="Saara content — filters ke saath")
async def get_all_content(
    subject:    Optional[str] = Query(None),
    type:       Optional[str] = Query(None),
    difficulty: Optional[int] = Query(None, ge=1, le=4),
    page:       int           = Query(1,  ge=1),
    limit:      int           = Query(10, ge=1, le=50),
    current_user: dict        = Depends(get_current_user),
    rec:        Recommender   = Depends(get_recommender),
):
    content = rec.content_library.copy()

    if subject:
        content = [c for c in content if c["subject"].lower() == subject.lower()]
    if type:
        content = [c for c in content if c["type"].lower() == type.lower()]
    if difficulty:
        content = [c for c in content if c["difficulty"] == difficulty]

    total = len(content)
    start = (page - 1) * limit
    paged = content[start: start + limit]

    return {
        "total":       total,
        "page":        page,
        "limit":       limit,
        "total_pages": (total + limit - 1) // limit,
        "content":     paged,
    }


# =============================================================
# ROUTE 3 — SUBJECTS
# =============================================================

@router.get("/subjects", summary="Available subjects list")
async def get_subjects(
    current_user: dict      = Depends(get_current_user),
    rec:          Recommender = Depends(get_recommender),
):
    subjects = rec.get_all_subjects()
    return {"subjects": subjects, "total": len(subjects)}


# =============================================================
# ROUTE 4 — SEARCH
# =============================================================

@router.get("/search", summary="Content search karo")
async def search_content(
    q:            str       = Query(..., min_length=2),
    current_user: dict      = Depends(get_current_user),
    rec:          Recommender = Depends(get_recommender),
):
    results = rec.search(q)
    return {"query": q, "total": len(results), "results": results}


# =============================================================
# ROUTE 5 — PROGRESS
# =============================================================

@router.get("/progress", summary="Student ki learning progress")
async def get_my_progress(
    current_user: dict                = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
    rec:          Recommender         = Depends(get_recommender),
):
    user_id = str(current_user["_id"])

    completed_records = await db["progress"].find(
        {"user_id": user_id, "completed": True}
    ).sort("completed_at", -1).to_list(None)

    completed_ids   = [r["content_id"] for r in completed_records]
    total_available = len(rec.content_library)

    subject_breakdown: dict = {}
    for item in rec.content_library:
        s = item["subject"]
        if s not in subject_breakdown:
            subject_breakdown[s] = {"completed": 0, "total": 0, "percentage": 0.0}
        subject_breakdown[s]["total"] += 1

    for record in completed_records:
        s = record.get("subject", "")
        if s in subject_breakdown:
            subject_breakdown[s]["completed"] += 1

    for s in subject_breakdown:
        total = subject_breakdown[s]["total"]
        done  = subject_breakdown[s]["completed"]
        subject_breakdown[s]["percentage"] = round((done / total) * 100, 1) if total > 0 else 0.0

    recent = []
    for record in completed_records[:5]:
        item = rec.get_content_by_id(record["content_id"])
        if item:
            completed_at = record.get("completed_at", "")
            recent.append({
                "content_id":   record["content_id"],
                "title":        item.get("title", ""),
                "subject":      record.get("subject", ""),
                "completed_at": completed_at.isoformat()
                                if isinstance(completed_at, datetime)
                                else str(completed_at),
            })

    total_completed = len(completed_ids)
    return {
        "learning_style":     current_user.get("learning_style"),
        "total_completed":    total_completed,
        "total_available":    total_available,
        "overall_percentage": round((total_completed / total_available) * 100, 1)
                              if total_available > 0 else 0.0,
        "subject_breakdown":  subject_breakdown,
        "recently_completed": recent,
        "completed_ids":      completed_ids,
    }


# =============================================================
# ROUTE 6 — SINGLE CONTENT DETAIL
# NOTE: Ye route /progress ke BAAD rakha hai — warna /progress
#       ko content_id samajh leta FastAPI
# =============================================================

@router.get("/{content_id}", summary="Ek content ki detail")
async def get_content_detail(
    content_id:   str,
    current_user: dict                = Depends(get_current_user),
    db:           AsyncIOMotorDatabase = Depends(get_db),
    rec:          Recommender         = Depends(get_recommender),
):
    content = rec.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404,
                            detail=f"Content '{content_id}' nahi mila.")

    progress = await db["progress"].find_one({
        "user_id":    str(current_user["_id"]),
        "content_id": content_id,
    })

    pipeline = [
        {"$match": {"content_id": content_id, "rating": {"$exists": True}}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}},
    ]
    rating_agg   = await db["progress"].aggregate(pipeline).to_list(1)
    avg_rating   = round(rating_agg[0]["avg_rating"], 1) if rating_agg else None
    rating_count = rating_agg[0]["count"]               if rating_agg else 0

    return {
        "content":      content,
        "avg_rating":   avg_rating,
        "rating_count": rating_count,
        "my_progress": {
            "completed":      progress.get("completed",      False) if progress else False,
            "completed_at":   str(progress.get("completed_at", "")) if progress else None,
            "time_spent_min": progress.get("time_spent_min")        if progress else None,
            "my_rating":      progress.get("rating")                if progress else None,
            "my_notes":       progress.get("notes")                 if progress else None,
        },
    }


# =============================================================
# ROUTE 7 — MARK COMPLETE
# =============================================================

@router.post("/complete/{content_id}", summary="Content complete mark karo")
async def mark_complete(
    content_id:   str,
    body:         CompleteContentRequest,
    current_user: dict                = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
    rec:          Recommender         = Depends(get_recommender),
):
    content = rec.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404,
                            detail=f"Content '{content_id}' nahi mila.")

    user_id  = str(current_user["_id"])
    existing = await db["progress"].find_one({"user_id": user_id, "content_id": content_id})

    if existing and existing.get("completed"):
        return {"message": "Ye content pehle se complete hai!",
                "completed_at": str(existing.get("completed_at", ""))}

    now = datetime.now(timezone.utc)
    await db["progress"].update_one(
        {"user_id": user_id, "content_id": content_id},
        {"$set": {
            "user_id":        user_id,
            "content_id":     content_id,
            "subject":        content["subject"],
            "content_type":   content["type"],
            "difficulty":     content["difficulty"],
            "completed":      True,
            "completed_at":   now,
            "time_spent_min": body.time_spent_min,
            "notes":          body.notes,
        }},
        upsert=True,
    )

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$inc": {"total_completed": 1}},
    )

    return {
        "message":      f"'{content['title']}' complete ho gaya! Shabaash! 🎉",
        "content_id":   content_id,
        "completed_at": now.isoformat(),
        "subject":      content["subject"],
    }


# =============================================================
# ROUTE 8 — RATE CONTENT
# =============================================================

@router.post("/rate/{content_id}", summary="Content ko rating do")
async def rate_content(
    content_id:   str,
    body:         RateContentRequest,
    current_user: dict                = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
    rec:          Recommender         = Depends(get_recommender),
):
    content = rec.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404,
                            detail=f"Content '{content_id}' nahi mila.")

    user_id  = str(current_user["_id"])
    progress = await db["progress"].find_one(
        {"user_id": user_id, "content_id": content_id, "completed": True}
    )
    if not progress:
        raise HTTPException(status_code=400,
                            detail="Pehle content complete karo, tab rating do.")

    await db["progress"].update_one(
        {"user_id": user_id, "content_id": content_id},
        {"$set": {
            "rating":   body.rating,
            "comment":  body.comment,
            "rated_at": datetime.now(timezone.utc),
        }},
    )

    return {
        "message":    f"Rating de di! {'⭐' * body.rating}",
        "content_id": content_id,
        "rating":     body.rating,
    }