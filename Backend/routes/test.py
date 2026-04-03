# =============================================================
# backend/routes/test.py  — FIXED VERSION
# Edu-Platform — Aptitude Test Routes
#
# Changes from previous version:
#   - predict_cluster() now uses predict_cluster.py (ensemble model)
#   - confidence score bhi return hota hai
#   - ML path config se aata hai
#   - Better error handling
# =============================================================

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import APIRouter, HTTPException, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone, timedelta

from database.db import get_db
from routes.auth import get_current_user, get_current_student
from Backend.models import AnswerItem, TestSubmitRequest

# Config se settings lo
try:
    from config import settings
    RETEST_COOLDOWN_DAYS = settings.RETEST_COOLDOWN_DAYS
except Exception:
    RETEST_COOLDOWN_DAYS = 30

# ML predict karo
try:
    from ML.predict_cluster import predict_learning_style, predict_cluster_id, get_model_info
    ML_AVAILABLE = True
    print("[test.py] ML models loaded successfully")
except Exception as e:
    ML_AVAILABLE = False
    print(f"[test.py] ML not available: {e} — rule-based fallback will be used")

from ..models import AnswerItem, TestSubmitRequest

router = APIRouter(prefix="/test", tags=["Aptitude Test"])
ML_FEATURES = ["logical", "verbal", "numerical", "memory", "attention"]


# =============================================================
# Questions Bank — 25 questions, 5 sections
# =============================================================

QUESTIONS_BANK = {
    "logical": [
        {"id":"L1","section":"logical",  "question":"Agar MANGO ko NBOHI likha jaaye toh APPLE ko kaise likhenge?",                             "options":["BQQMF","CQQNF","BQPMF","CQQOF"],           "correct":"BQQMF","marks":20},
        {"id":"L2","section":"logical",  "question":"Series mein agla number kya hoga? 2, 6, 12, 20, 30, ?",                                     "options":["40","42","38","44"],                       "correct":"42","marks":20},
        {"id":"L3","section":"logical",  "question":"Teen dost A, B, C hain. A, B se bada hai. C, A se bada hai. Sabse bada kaun?",              "options":["A","B","C","Barabar"],                     "correct":"C","marks":20},
        {"id":"L4","section":"logical",  "question":"Ek ghadi mein 3:15 baj rahe hain. Minute aur hour hand ka angle kya hoga?",                 "options":["0°","7.5°","15°","22.5°"],                 "correct":"7.5°","marks":20},
        {"id":"L5","section":"logical",  "question":"5 machines 5 min mein 5 widgets banaati hain. 100 machines 100 min mein kitne banayengi?",  "options":["100","500","1000","10000"],                "correct":"10000","marks":20},
    ],
    "verbal": [
        {"id":"V1","section":"verbal",   "question":"'Ephemeral' ka sahi arth kya hai?",                                                          "options":["Jo bahut purana ho","Jo bahut thodi der ke liye ho","Jo bahut bada ho","Jo mushkil ho"], "correct":"Jo bahut thodi der ke liye ho","marks":20},
        {"id":"V2","section":"verbal",   "question":"Ramesh roz 6 baje uthta hai, exercise karta hai, phir nashta, 9 baje office.\nOffice kab?", "options":["6 baje","Nashte ke pehle","9 baje","Exercise ke baad"],                               "correct":"9 baje","marks":20},
        {"id":"V3","section":"verbal",   "question":"'Benevolent' ka antonym kya hai?",                                                           "options":["Kind","Malevolent","Generous","Helpful"],                                               "correct":"Malevolent","marks":20},
        {"id":"V4","section":"verbal",   "question":"Sahi sentence choose karo:",                                                                  "options":["He don't know the answer.","He doesn't knows the answer.","He doesn't know the answer.","He not know."], "correct":"He doesn't know the answer.","marks":20},
        {"id":"V5","section":"verbal",   "question":"'Verbose' ka matlab hai:",                                                                    "options":["Bahut kam bolna","Seedha bolna","Bahut zyada bolna","Clearly explain karna"],            "correct":"Bahut zyada bolna","marks":20},
    ],
    "numerical": [
        {"id":"N1","section":"numerical","question":"Train 60 km/h pe chalti hai. 2.5 ghante mein kitni doori?",                                  "options":["120 km","140 km","150 km","160 km"],       "correct":"150 km","marks":20},
        {"id":"N2","section":"numerical","question":"Item Rs.800 mein kharida, Rs.1000 mein becha. Profit %?",                                    "options":["20%","25%","15%","30%"],                   "correct":"25%","marks":20},
        {"id":"N3","section":"numerical","question":"5 numbers ka average 18 hai. Ek 10 remove karo — baaki 4 ka average?",                      "options":["18","20","22","25"],                       "correct":"20","marks":20},
        {"id":"N4","section":"numerical","question":"2^2 + 3^3 + 4^0 = ?",                                                                        "options":["30","32","34","36"],                       "correct":"32","marks":20},
        {"id":"N5","section":"numerical","question":"Kaam A 10 din mein karta hai, B 15 din mein. Saath mein kitne din?",                         "options":["5 din","6 din","7 din","8 din"],           "correct":"6 din","marks":20},
    ],
    "memory": [
        {"id":"M1","section":"memory",   "question":"List yaad karo: Apple, Banana, Cherry, Date, Elderberry.\nTeesra fruit?",                    "options":["Banana","Cherry","Date","Apple"],          "correct":"Cherry","marks":20},
        {"id":"M2","section":"memory",   "question":"Numbers yaad karo: 47, 83, 29, 61, 15.\nDusra number?",                                      "options":["47","29","83","61"],                       "correct":"83","marks":20},
        {"id":"M3","section":"memory",   "question":"'The quick brown fox jumps over the lazy dog.'\n'fox' ke liye adjective?",                   "options":["quick","brown","lazy","slow"],             "correct":"brown","marks":20},
        {"id":"M4","section":"memory",   "question":"Colors: Red, Blue, Green, Yellow, Purple, Orange.\nChauthha?",                               "options":["Green","Yellow","Purple","Blue"],          "correct":"Yellow","marks":20},
        {"id":"M5","section":"memory",   "question":"Capitals: France-Paris, Japan-Tokyo, India-Delhi, Australia-Canberra.\nAustralia ki capital?","options":["Sydney","Melbourne","Canberra","Brisbane"], "correct":"Canberra","marks":20},
    ],
    "attention": [
        {"id":"A1","section":"attention","question":"'The cat sat on the mat near the window while the dog slept under the table.'\n'the' kitni baar?","options":["3","4","5","6"],                         "correct":"5","marks":20},
        {"id":"A2","section":"attention","question":"Odd one out:\n2, 4, 7, 8, 12, 16",                                                           "options":["4","7","12","16"],                         "correct":"7","marks":20},
        {"id":"A3","section":"attention","question":"Kya galat hai?\n'He buyed milk and payed at counter.'",                                       "options":["Sirf buyed galat","buyed aur payed dono galat","Kuch galat nahi","Sirf payed galat"], "correct":"buyed aur payed dono galat","marks":20},
        {"id":"A4","section":"attention","question":"Pattern: △○△△○△△△○?\nAgla?",                                                                "options":["△","○","□","△○"],                         "correct":"△","marks":20},
        {"id":"A5","section":"attention","question":"Odd one out:\nTable, Chair, Lamp, Sofa, Pen, Desk",                                          "options":["Lamp","Pen","Sofa","Table"],               "correct":"Pen","marks":20},
    ],
}


# =============================================================
# Utilities
# =============================================================

def calculate_section_scores(answers: list[AnswerItem]) -> dict:
    """Answers check karo, section-wise 0-100 scores return karo."""
    all_qs       = {q["id"]: q for sec in QUESTIONS_BANK.values() for q in sec}
    answers_dict = {a.question_id: a.answer for a in answers}

    section_earned = {s: 0 for s in ML_FEATURES}
    section_max    = {s: 0 for s in ML_FEATURES}
    per_question   = []

    for section, questions in QUESTIONS_BANK.items():
        for q in questions:
            student_ans = answers_dict.get(q["id"], "").strip()
            is_correct  = (student_ans == q["correct"].strip())
            earned      = q["marks"] if is_correct else 0
            section_earned[section] += earned
            section_max[section]    += q["marks"]
            per_question.append({
                "question_id":    q["id"],
                "section":        section,
                "student_answer": student_ans,
                "correct_answer": q["correct"],
                "is_correct":     is_correct,
                "marks_earned":   earned,
                "max_marks":      q["marks"],
            })

    normalized = {
        sec: round((section_earned[sec] / section_max[sec]) * 100, 1)
        if section_max[sec] > 0 else 0.0
        for sec in ML_FEATURES
    }
    normalized["total"]        = round(sum(normalized[f] for f in ML_FEATURES) / 5, 1)
    normalized["per_question"] = per_question
    return normalized


def run_ml_prediction(section_scores: dict) -> tuple[int, str, float]:
    """
    ML model se learning style predict karo.

    Returns:
        (cluster_id, learning_style, confidence)
    """
    scores = {f: section_scores[f] for f in ML_FEATURES}

    if ML_AVAILABLE:
        try:
            cluster_id, style = predict_cluster_id(scores)
            _, confidence     = predict_learning_style(scores)
            return cluster_id, style, round(confidence, 3)
        except Exception as e:
            print(f"[test.py] ML prediction failed: {e}")

    # Rule-based fallback
    dominant = max(scores, key=scores.get)
    fallback  = {
        'logical':   (1, 'conceptual_thinker'),
        'verbal':    (0, 'visual_learner'),
        'numerical': (2, 'practice_based'),
        'memory':    (3, 'step_by_step'),
        'attention': (2, 'practice_based'),
    }
    cluster_id, style = fallback.get(dominant, (0, 'visual_learner'))
    return cluster_id, style, 0.70


def _style_details(style: str) -> dict:
    details = {
        "visual_learner":     {"title":"Visual Learner 👁️","description":"Diagrams, animations aur visual content se best seekhte ho.","strengths":["Visual memory strong hai","Diagrams se jaldi samajhte ho","Colour-coded notes help karte hain"],"content_types":["Video Lectures","Infographics","Animated Explainers"],"study_tip":"Mind maps banao aur notes mein colours use karo!"},
        "conceptual_thinker": {"title":"Conceptual Thinker 🧠","description":"Deep theory aur 'why' samajhna pasand hai tumhe.","strengths":["Analytical thinking strong hai","Complex concepts samajhte ho","Connections dhundh lete ho"],"content_types":["Theory Articles","Case Studies","In-depth Videos"],"study_tip":"Pehle poora concept samjho, tab practice karo!"},
        "practice_based":     {"title":"Practice-Based Learner ⚙️","description":"Kar ke seekhte ho tum — theory baad mein.","strengths":["Hands-on kaam mein best ho","Problem solving strong hai","Projects mein best perform karte ho"],"content_types":["Coding Exercises","Mini Projects","Hands-on Labs"],"study_tip":"Pehle problem try karo, phir solution dekho!"},
        "step_by_step":       {"title":"Step-by-Step Learner 📋","description":"Structured, sequential content se best seekhte ho.","strengths":["Structured notes se jaldi yaad hota hai","Sequential thinking strong hai","Checklists helpful lagti hain"],"content_types":["Structured Notes","Guided Tutorials","Checklists"],"study_tip":"Ek concept complete karo, tab agla shuru karo!"},
    }
    return details.get(style, details["visual_learner"])


def _section_desc(section: str) -> str:
    return {
        "logical":   "Reasoning aur problem-solving ability",
        "verbal":    "Language understanding aur communication",
        "numerical": "Mathematical aur analytical ability",
        "memory":    "Information retain karne ki capability",
        "attention": "Focus aur detail-oriented thinking",
    }.get(section, "")


# =============================================================
# ROUTE 1 — GET QUESTIONS
# =============================================================

@router.get("/questions", summary="Aptitude test ke 25 questions fetch karo")
async def get_questions(current_user: dict = Depends(get_current_student)):
    sections        = []
    total_questions = 0
    for section, questions in QUESTIONS_BANK.items():
        safe_qs = [{"id":q["id"],"section":q["section"],"question":q["question"],
                    "options":q["options"],"marks":q["marks"]} for q in questions]
        total_questions += len(questions)
        sections.append({
            "section_id":   section,
            "section_name": section.replace("_"," ").title(),
            "description":  _section_desc(section),
            "questions":    safe_qs,
            "total_marks":  sum(q["marks"] for q in questions),
        })
    return {
        "total_questions": total_questions,
        "total_sections":  len(sections),
        "total_marks":     total_questions * 20,
        "time_limit_min":  30,
        "ml_model_active": ML_AVAILABLE,
        "instructions":    [
            "Saare 25 questions attempt karo",
            "Har question ke 4 options mein se ek choose karo",
            "Har sahi answer ke 20 marks milenge — no negative marking",
            "Test 30 minutes mein complete karo",
            "Submit karne ke baad 30 din tak dobara test nahi de sakte",
        ],
        "sections": sections,
    }


# =============================================================
# ROUTE 2 — SUBMIT TEST
# =============================================================

@router.post("/submit", status_code=status.HTTP_201_CREATED,
             summary="Test submit karo — ML model learning style predict karega")
async def submit_test(
    body:         TestSubmitRequest,
    current_user: dict = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
):
    user_id   = str(current_user["_id"])

    # Cooldown check
    last_test = await db["test_results"].find_one(
        {"user_id": user_id}, sort=[("submitted_at", -1)]
    )
    if last_test:
        last_time = last_test["submitted_at"]
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        days_since = (datetime.now(timezone.utc) - last_time).days
        if days_since < RETEST_COOLDOWN_DAYS:
            raise HTTPException(
                status_code=429,
                detail=f"Test {RETEST_COOLDOWN_DAYS - days_since} din baad de sakte ho.",
            )

    # Score calculate karo
    scores                     = calculate_section_scores(body.answers)
    section_scores             = {f: scores[f] for f in ML_FEATURES}

    # ML prediction (best accuracy: 93.3%)
    cluster_id, learning_style, confidence = run_ml_prediction(section_scores)

    # Correct answers count
    correct_count = sum(1 for q in scores["per_question"] if q["is_correct"])
    total_marks   = correct_count * 20

    now    = datetime.now(timezone.utc)
    result = {
        "user_id":        user_id,
        "attempt_number": (last_test.get("attempt_number", 0) + 1) if last_test else 1,
        "scores":         {**section_scores, "total": scores["total"]},
        "cluster_id":     cluster_id,
        "learning_style": learning_style,
        "confidence":     confidence,
        "correct_answers":correct_count,
        "total_marks":    total_marks,
        "per_question":   scores["per_question"],
        "submitted_at":   now,
        "ml_mode":        "ensemble" if ML_AVAILABLE else "rule_based",
    }
    await db["test_results"].insert_one(result)

    # User update karo
    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "learning_style":  learning_style,
            "cluster_id":      cluster_id,
            "last_test_date":  now,
            "needs_recluster": False,
        }},
    )

    return {
        "message":         "Test submit ho gaya! Tumhara learning style pata chal gaya! 🎉",
        "attempt_number":  result["attempt_number"],
        "scores":          {**section_scores, "total": scores["total"]},
        "cluster_id":      cluster_id,
        "learning_style":  learning_style,
        "confidence":      confidence,
        "correct_answers": correct_count,
        "total_marks":     total_marks,
        "out_of":          500,
        "style_details":   _style_details(learning_style),
        "next_test_date":  (now + timedelta(days=RETEST_COOLDOWN_DAYS)).strftime("%Y-%m-%d"),
        "ml_mode":         "ensemble" if ML_AVAILABLE else "rule_based",
    }


# =============================================================
# ROUTE 3 — GET RESULT
# =============================================================

@router.get("/result", summary="Latest test result dekho")
async def get_my_result(
    current_user: dict = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(current_user["_id"])
    result  = await db["test_results"].find_one(
        {"user_id": user_id}, sort=[("submitted_at", -1)]
    )
    if not result:
        raise HTTPException(status_code=404, detail="Abhi tak test nahi diya. /test/questions pe jao!")

    submitted_at = result["submitted_at"]
    if submitted_at.tzinfo is None:
        submitted_at = submitted_at.replace(tzinfo=timezone.utc)

    next_date  = submitted_at + timedelta(days=RETEST_COOLDOWN_DAYS)
    days_left  = (next_date - datetime.now(timezone.utc)).days

    return {
        "attempt_number":    result.get("attempt_number", 1),
        "scores":            result["scores"],
        "cluster_id":        result["cluster_id"],
        "learning_style":    result["learning_style"],
        "confidence":        result.get("confidence", 0.85),
        "correct_answers":   result.get("correct_answers", 0),
        "total_marks":       result.get("total_marks", 0),
        "out_of":            500,
        "style_details":     _style_details(result["learning_style"]),
        "submitted_at":      submitted_at.isoformat(),
        "next_test_date":    next_date.strftime("%Y-%m-%d"),
        "days_until_retake": max(0, days_left),
        "can_retake":        days_left <= 0,
        "ml_mode":           result.get("ml_mode", "unknown"),
    }


# =============================================================
# ROUTE 4 — HISTORY
# =============================================================

@router.get("/history", summary="Saare test attempts ki history")
async def get_test_history(
    current_user: dict = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = str(current_user["_id"])
    records = await db["test_results"].find(
        {"user_id": user_id},
        {"per_question": 0},
        sort=[("submitted_at", -1)],
    ).to_list(None)

    if not records:
        return {"message":"Abhi tak koi test nahi diya.", "history":[], "total_attempts":0}

    history = []
    for r in records:
        st = r["submitted_at"]
        if st.tzinfo is None:
            st = st.replace(tzinfo=timezone.utc)
        history.append({
            "attempt_number": r.get("attempt_number", 1),
            "scores":         r["scores"],
            "learning_style": r["learning_style"],
            "cluster_id":     r["cluster_id"],
            "confidence":     r.get("confidence", 0.85),
            "correct_answers":r.get("correct_answers", 0),
            "submitted_at":   st.isoformat(),
        })

    return {
        "total_attempts": len(history),
        "latest_style":   history[0]["learning_style"] if history else None,
        "history":        history,
    }


# =============================================================
# ROUTE 5 — RETAKE
# =============================================================

@router.post("/retake", summary="30 din baad dobara test lo")
async def retake_test(
    current_user: dict = Depends(get_current_student),
    db:           AsyncIOMotorDatabase = Depends(get_db),
):
    user_id   = str(current_user["_id"])
    last_test = await db["test_results"].find_one(
        {"user_id": user_id}, sort=[("submitted_at", -1)]
    )

    if not last_test:
        return {"message":"Pehle test do! /test/questions pe jao.", "can_retake": True}

    last_time = last_test["submitted_at"]
    if last_time.tzinfo is None:
        last_time = last_time.replace(tzinfo=timezone.utc)

    days_since = (datetime.now(timezone.utc) - last_time).days
    if days_since < RETEST_COOLDOWN_DAYS:
        raise HTTPException(
            status_code=429,
            detail=f"Abhi retake nahi ho sakta. {RETEST_COOLDOWN_DAYS - days_since} din baaki hain.",
        )

    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": {"needs_recluster": True}},
    )
    return {
        "message":        "Retake allowed! /test/questions pe jao — style re-evaluate hogi.",
        "can_retake":     True,
        "previous_style": last_test.get("learning_style"),
    }


# =============================================================
# ROUTE 6 — MODEL INFO
# =============================================================

@router.get("/model-info", summary="ML model ki information")
async def model_info(current_user: dict = Depends(get_current_user)):
    if ML_AVAILABLE:
        return {"ml_available": True, **get_model_info()}
    return {"ml_available": False, "mode": "rule_based", "note": "ML models nahi mile. python train_model.py chalao."}