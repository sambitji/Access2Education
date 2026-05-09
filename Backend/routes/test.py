# =============================================================
# backend/routes/test.py
# Edu-Platform — Aptitude Test Routes (MySQL Version)
# =============================================================

import sys, os
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from database.db import get_db, User, TestResult
from routes.auth import get_current_user, get_current_student
from models import AnswerItem, TestSubmitRequest

# ML predict karo
try:
    from ML.predict_cluster import predict_learning_style, predict_cluster_id, get_model_info
    ML_AVAILABLE = True
except Exception as e:
    ML_AVAILABLE = False

router = APIRouter(prefix="/test", tags=["Aptitude Test"])
ML_FEATURES = ["logical", "verbal", "numerical", "memory", "attention"]
RETEST_COOLDOWN_DAYS = 30

# =============================================================
# Questions Bank
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
# Helper Functions
# =============================================================

def calculate_section_scores(answers: list[AnswerItem]) -> dict:
    all_qs = {q["id"]: q for sec in QUESTIONS_BANK.values() for q in sec}
    answers_dict = {a.question_id: a.answer for a in answers}
    section_earned = {s: 0 for s in ML_FEATURES}
    section_max = {s: 0 for s in ML_FEATURES}
    
    for section, questions in QUESTIONS_BANK.items():
        for q in questions:
            student_ans = answers_dict.get(q["id"], "").strip()
            is_correct = (student_ans == q["correct"].strip())
            earned = q["marks"] if is_correct else 0
            section_earned[section] += earned
            section_max[section] += q["marks"]
            
    normalized = {sec: round((section_earned[sec] / section_max[sec]) * 100, 1) if section_max[sec] > 0 else 0.0 for sec in ML_FEATURES}
    normalized["total"] = round(sum(normalized[f] for f in ML_FEATURES) / 5, 1)
    return normalized

def run_ml_prediction(section_scores: dict) -> tuple[int, str, float]:
    scores = {f: section_scores[f] for f in ML_FEATURES}
    if ML_AVAILABLE:
        try:
            cluster_id, style = predict_cluster_id(scores)
            _, confidence = predict_learning_style(scores)
            return cluster_id, style, round(confidence, 3)
        except Exception:
            pass
    dominant = max(scores, key=scores.get)
    fallback = {'logical': (1, 'conceptual_thinker'), 'verbal': (0, 'visual_learner'), 'numerical': (2, 'practice_based'), 'memory': (3, 'step_by_step'), 'attention': (2, 'practice_based')}
    return fallback.get(dominant, (0, 'visual_learner')) + (0.7,)

def _style_details(style: str) -> dict:
    details = {
        "visual_learner":     {"title":"Visual Learner","description":"Diagrams aur visual content se best seekhte ho.","strengths":["Visual memory strong","Diagrams helpful"],"content_types":["Video Lectures","Infographics"],"study_tip":"Mind maps banao!"},
        "conceptual_thinker": {"title":"Conceptual Thinker","description":"Deep theory aur 'why' samajhna pasand hai.","strengths":["Analytical thinking","Complex concepts"],"content_types":["Theory Articles","Case Studies"],"study_tip":"Pehle theory samjho!"},
        "practice_based":     {"title":"Practice-Based Learner","description":"Kar ke seekhte ho tum.","strengths":["Hands-on projects","Problem solving"],"content_types":["Coding Exercises","Labs"],"study_tip":"Practice first!"},
        "step_by_step":       {"title":"Step-by-Step Learner","description":"Structured content se best seekhte ho.","strengths":["Sequential thinking","Checklists"],"content_types":["Structured Notes","Tutorials"],"study_tip":"One step at a time!"},
    }
    return details.get(style, details["visual_learner"])

# =============================================================
# Routes
# =============================================================

@router.get("/questions")
async def get_questions(current_user: User = Depends(get_current_student)):
    sections = []
    for section, questions in QUESTIONS_BANK.items():
        safe_qs = [{"id":q["id"],"section":q["section"],"question":q["question"],"options":q["options"],"marks":q["marks"]} for q in questions]
        sections.append({
            "section_id": section,
            "section_name": section.title(),
            "questions": safe_qs,
            "total_marks": sum(q["marks"] for q in questions),
        })
    return {"sections": sections, "total_marks": 500, "time_limit_min": 30}

@router.post("/submit", status_code=status.HTTP_201_CREATED)
async def submit_test(
    body: TestSubmitRequest,
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id
    
    # Cooldown check
    result = await db.execute(select(TestResult).where(TestResult.user_id == user_id).order_by(desc(TestResult.submitted_at)))
    last_test = result.scalars().first()
    if last_test:
        days_since = (datetime.now(timezone.utc).replace(tzinfo=None) - last_test.submitted_at.replace(tzinfo=None)).days
        if days_since < RETEST_COOLDOWN_DAYS:
            raise HTTPException(status_code=429, detail=f"Test {RETEST_COOLDOWN_DAYS - days_since} din baad de sakte ho.")

    scores = calculate_section_scores(body.answers)
    section_scores = {f: scores[f] for f in ML_FEATURES}
    cluster_id, style, confidence = run_ml_prediction(section_scores)
    
    new_result = TestResult(user_id=user_id, scores=section_scores, cluster=cluster_id, learning_style=style)
    db.add(new_result)
    
    current_user.learning_style = style
    current_user.cluster_id = cluster_id
    
    await db.commit()
    await db.refresh(new_result)
    
    return {
        "message": "Test submitted successfully",
        "result": {
            "score_summary": scores,
            "learning_style": style,
            "details": _style_details(style)
        }
    }

@router.get("/results")
async def get_results(current_user: User = Depends(get_current_student), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestResult).where(TestResult.user_id == current_user.id).order_by(desc(TestResult.submitted_at)))
    records = result.scalars().all()
    if not records:
        raise HTTPException(status_code=404, detail="Pehle test dein!")
        
    latest = records[0]
    return {
        "latest": {
            "scores": latest.scores,
            "style": latest.learning_style,
            "date": latest.submitted_at.isoformat(),
            "details": _style_details(latest.learning_style)
        },
        "history": [{"id": r.id, "date": r.submitted_at.isoformat(), "style": r.learning_style} for r in records]
    }