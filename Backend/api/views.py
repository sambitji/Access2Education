import os
import sys
import json
import uuid
import bcrypt
import random
import string
import httpx
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone as dj_timezone

# Add root folder to sys.path to enable ML imports
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ML Imports
from ML.predict_cluster import predict_learning_style, predict_cluster_id
from ML.recommender import get_recommender
from ML.spaced_repetition import SM2Card, SpacedRepetitionEngine

from .models import User, TestResult, Progress, SRCard, RefreshToken, OTP, SRReviewHistory
from .decorators import jwt_required

# =============================================================
# Helper Utilities
# =============================================================

def parse_json(request):
    try:
        return json.loads(request.body)
    except Exception:
        return {}

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    payload = data.copy()
    issued_at = datetime.now(timezone.utc)
    payload["exp"] = issued_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["iat"] = issued_at
    payload["jti"] = str(uuid.uuid4())
    payload["type"] = "access"
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    issued_at = datetime.now(timezone.utc)
    payload["exp"] = issued_at + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload["iat"] = issued_at
    payload["jti"] = str(uuid.uuid4())
    payload["type"] = "refresh"
    return jwt.encode(payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

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
# General & Health Views
# =============================================================

@csrf_exempt
def root_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    return JsonResponse({
        "message": "Edu-Platform API chal rahi hai!",
        "docs":    "/admin",
    })

@csrf_exempt
def health_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    return JsonResponse({"status": "healthy", "service": "Edu-Platform API"})

# =============================================================
# Auth Views
# =============================================================

@csrf_exempt
def register_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    name = body.get("name", "").strip()
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")
    role = body.get("role", "student")

    if not name or not email or not password:
        return JsonResponse({"detail": "Name, email, and password are required."}, status=400)
    
    if len(name) < 2 or len(name) > 60:
        return JsonResponse({"detail": "Name length must be between 2 and 60."}, status=400)
    
    if role not in ("student", "teacher"):
        return JsonResponse({"detail": "Role must be 'student' or 'teacher'."}, status=400)

    if len(password) < 8 or len(password) > 64:
        return JsonResponse({"detail": "Password must be between 8 and 64 characters."}, status=400)
    if not any(c.isupper() for c in password):
        return JsonResponse({"detail": "Password must contain at least one uppercase letter."}, status=400)
    if not any(c.isdigit() for c in password):
        return JsonResponse({"detail": "Password must contain at least one digit."}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"detail": f"'{email}' is already registered."}, status=409)

    new_user = User.objects.create(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role
    )

    token_data = {"sub": str(new_user.id), "role": new_user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    RefreshToken.objects.create(
        user=new_user,
        token=refresh_token,
        expires_at=dj_timezone.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return JsonResponse({
        "message":       f"Registration successful! Welcome, {new_user.name}",
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "user":          format_user_response(new_user),
    }, status=201)

@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    if not verify_password(password, user.password_hash):
        return JsonResponse({"detail": "Invalid credentials."}, status=401)

    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    RefreshToken.objects.create(
        user=user,
        token=refresh_token,
        expires_at=dj_timezone.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # Update last login
    user.last_login = dj_timezone.now()
    user.save()

    return JsonResponse({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "bearer",
        "user":          format_user_response(user),
    })

@csrf_exempt
def refresh_token_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return JsonResponse({"detail": "Refresh token is required."}, status=400)

    try:
        payload = jwt.decode(refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return JsonResponse({"detail": "Wrong token type"}, status=401)
    except JWTError:
        return JsonResponse({"detail": "Refresh token is invalid or expired."}, status=401)

    try:
        stored = RefreshToken.objects.get(token=refresh_token)
    except RefreshToken.DoesNotExist:
        return JsonResponse({"detail": "Refresh token has been revoked."}, status=401)

    access_token = create_access_token({
        "sub":  payload.get("sub"),
        "role": payload.get("role"),
    })
    return JsonResponse({"access_token": access_token, "token_type": "bearer"})

@csrf_exempt
def logout_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        return JsonResponse({"detail": "Refresh token is required."}, status=400)

    try:
        rt = RefreshToken.objects.get(token=refresh_token)
        rt.delete()
        return JsonResponse({"message": "Successfully logged out!"})
    except RefreshToken.DoesNotExist:
        return JsonResponse({"detail": "Token not found."}, status=400)

@csrf_exempt
@jwt_required()
def me_view(request):
    if request.method == "GET":
        return JsonResponse({"user": format_user_response(request.user)})
    
    elif request.method == "PUT":
        body = parse_json(request)
        name = body.get("name")
        avatar_url = body.get("avatar_url")
        old_password = body.get("old_password")
        new_password = body.get("new_password")

        updated = False
        if name:
            request.user.name = name.strip()
            updated = True
        if avatar_url is not None:
            request.user.avatar_url = avatar_url.strip()
            updated = True
        if new_password:
            if not old_password:
                return JsonResponse({"detail": "Old password is also required."}, status=400)
            if not verify_password(old_password, request.user.password_hash):
                return JsonResponse({"detail": "Old password is incorrect."}, status=401)
            request.user.password_hash = hash_password(new_password)
            updated = True

        if not updated:
            return JsonResponse({"detail": "No update fields provided."}, status=400)

        request.user.save()
        return JsonResponse({
            "message": "Profile updated successfully!",
            "user": format_user_response(request.user)
        })
    else:
        return JsonResponse({"detail": "Method not allowed"}, status=405)

@csrf_exempt
def forgot_password_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    email = body.get("email", "").lower().strip()
    if not email:
        return JsonResponse({"detail": "Email is required."}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Avoid user enumeration attacks, return mock message
        return JsonResponse({"message": "If this email is registered, an OTP has been sent."})

    otp = "".join(random.choices(string.digits, k=6))
    
    # Delete existing OTP for this email
    OTP.objects.filter(email=email).delete()
    
    # Create new OTP record
    OTP.objects.create(
        email=email,
        otp=otp,
        expires_at=dj_timezone.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    )

    # Simulated email sending
    print(f"\n{'='*50}")
    print(f"  OTP EMAIL  (Simulated)")
    print(f"  To   : {email}")
    print(f"  Name : {user.name}")
    print(f"  OTP  : {otp}   (valid {settings.OTP_EXPIRE_MINUTES} min)")
    print(f"{'='*50}\n")

    return JsonResponse({"message": "OTP has been sent. Check your inbox. (valid for 10 min)"})

@csrf_exempt
def reset_password_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    email = body.get("email", "").lower().strip()
    otp = body.get("otp", "").strip()
    new_password = body.get("new_password", "")

    if not email or not otp or not new_password:
        return JsonResponse({"detail": "Email, OTP, and new_password are required."}, status=400)

    try:
        otp_record = OTP.objects.get(email=email, used=False)
    except OTP.DoesNotExist:
        return JsonResponse({"detail": "OTP not found or already used."}, status=400)

    if dj_timezone.now() > otp_record.expires_at:
        return JsonResponse({"detail": "OTP has expired. Please try again."}, status=400)

    if otp_record.otp != otp:
        return JsonResponse({"detail": "OTP is incorrect."}, status=400)

    try:
        user = User.objects.get(email=email)
        user.password_hash = hash_password(new_password)
        user.save()
        
        # Mark OTP as used
        otp_record.used = True
        otp_record.save()
        
        # Revoke refresh tokens
        RefreshToken.objects.filter(user=user).delete()
        
        return JsonResponse({"message": "Password reset successful! Please login with your new password."})
    except User.DoesNotExist:
        return JsonResponse({"detail": "User not found."}, status=400)

# =============================================================
# Content & Recommendation Views
# =============================================================

@csrf_exempt
@jwt_required(role="student")
def get_recommendations_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    subject = request.GET.get("subject")
    content_type = request.GET.get("content_type")
    
    difficulty = request.GET.get("difficulty")
    if difficulty:
        try:
            difficulty = int(difficulty)
        except ValueError:
            return JsonResponse({"detail": "Difficulty must be an integer"}, status=400)

    top_n = request.GET.get("top_n", 6)
    try:
        top_n = int(top_n)
    except ValueError:
        top_n = 6

    if not request.user.learning_style:
        return JsonResponse({"detail": "Take the test first!"}, status=400)

    completed_ids = list(Progress.objects.filter(user=request.user, completed=True).values_list("content_id", flat=True))
    
    rec = get_recommender()
    recs = rec.get_recommendations(
        learning_style=request.user.learning_style,
        completed_ids=completed_ids,
        completed_count=len(completed_ids),
        subject=subject,
        content_type=content_type,
        difficulty=difficulty,
        top_n=top_n
    )
    return JsonResponse(recs)

@csrf_exempt
@jwt_required(role="student")
def get_my_progress_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    completed_records = Progress.objects.filter(user=request.user, completed=True).order_by("-last_accessed")
    
    rec = get_recommender()
    total_available = len(rec.content_library)
    total_completed = completed_records.count()
    
    subject_stats = {}
    for r in completed_records:
        subject_stats[r.subject] = subject_stats.get(r.subject, 0) + 1
        
    return JsonResponse({
        "learning_style": request.user.learning_style,
        "total_completed": total_completed,
        "total_available": total_available,
        "overall_percentage": round((total_completed / total_available) * 100, 1) if total_available > 0 else 0,
        "subject_stats": subject_stats
    })

@csrf_exempt
@jwt_required(role="student")
def mark_complete_view(request, content_id):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    rec = get_recommender()
    content = rec.get_content_by_id(content_id)
    if not content:
        return JsonResponse({"detail": "Content nahi mila"}, status=404)

    progress, created = Progress.objects.get_or_create(
        user=request.user,
        content_id=content_id,
        defaults={"subject": content["subject"]}
    )
    
    if progress.completed:
        return JsonResponse({"message": "Pehle se complete hai"})

    progress.completed = True
    progress.score = 100
    progress.save()
    
    request.user.total_completed += 1
    request.user.save()
    
    return JsonResponse({"message": f"'{content['title']}' complete!"})

@csrf_exempt
def get_all_content_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    rec = get_recommender()
    return JsonResponse({"content": rec.content_library, "total": len(rec.content_library)})

@csrf_exempt
def get_subjects_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    rec = get_recommender()
    return JsonResponse({"subjects": rec.get_all_subjects()})

# =============================================================
# Spaced Repetition Views
# =============================================================

@csrf_exempt
@jwt_required()
def add_card_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    concept_id = body.get("concept_id")
    subject = body.get("subject")
    concept_title = body.get("concept_title")

    if not concept_id or not subject or not concept_title:
        return JsonResponse({"detail": "concept_id, subject, and concept_title are required."}, status=400)

    if SRCard.objects.filter(user=request.user, concept_id=concept_id).exists():
        return JsonResponse({"detail": "Card already exists in deck"}, status=409)

    SRCard.objects.create(
        user=request.user,
        concept_id=concept_id,
        subject=subject,
        concept_title=concept_title,
        learning_style=request.user.cluster_id or 0
    )
    return JsonResponse({"message": "Card added"})

@csrf_exempt
@jwt_required()
def submit_review_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    concept_id = body.get("concept_id")
    quality = body.get("quality")

    if not concept_id or quality is None:
        return JsonResponse({"detail": "concept_id and quality are required."}, status=400)
    
    try:
        quality = int(quality)
        if quality < 0 or quality > 5:
            raise ValueError
    except ValueError:
        return JsonResponse({"detail": "Quality must be an integer between 0 and 5."}, status=400)

    try:
        card = SRCard.objects.get(user=request.user, concept_id=concept_id)
    except SRCard.DoesNotExist:
        return JsonResponse({"detail": "Card nahi mila"}, status=404)

    # ML SM-2 Logic
    sm2_card = SM2Card(
        concept_id=card.concept_id,
        user_id=str(card.user_id),
        subject=card.subject,
        concept_title=card.concept_title,
        interval=card.interval,
        easiness=card.easiness,
        repetition=card.repetition,
        next_review=card.next_review
    )
    
    updated_state = sm2_card.review(quality)
    
    # Update DB fields
    card.interval = updated_state["interval"]
    card.easiness = updated_state["easiness"]
    card.repetition = updated_state["repetition"]
    card.next_review = updated_state["next_review"]
    card.save()
    
    # Save History
    SRReviewHistory.objects.create(
        user=request.user,
        concept_id=concept_id,
        quality=quality,
        interval_after=card.interval,
        easiness_after=card.easiness
    )
    
    return JsonResponse({"message": "Review recorded", "next_review": card.next_review.isoformat()})

@csrf_exempt
@jwt_required()
def get_due_cards_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    cards_rows = SRCard.objects.filter(user=request.user)
    
    # Convert to SM2Card objects for processing
    sm2_cards = [
        SM2Card(
            concept_id=c.concept_id,
            user_id=str(c.user_id),
            subject=c.subject,
            concept_title=c.concept_title,
            interval=c.interval,
            easiness=c.easiness,
            repetition=c.repetition,
            next_review=c.next_review
        )
        for c in cards_rows
    ]
    
    engine = SpacedRepetitionEngine(sm2_cards)
    due = engine.get_due_cards()
    
    return JsonResponse({"due_count": len(due), "cards": [c.to_dict() for c in due]})

# =============================================================
# Chatbot Views
# =============================================================

@csrf_exempt
def summarize_lecture_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    lecture_text = body.get("lecture_text", "")
    student_style = body.get("learning_style", "general")

    prompt = f"""
    You are an educational assistant. A student who is a '{student_style}' 
    needs help understanding this lecture content.
    
    Summarize this in a way that suits their learning style.
    Use diagrams descriptions if visual, examples if practice-based, 
    step-by-step breakdown if sequential.
    
    Lecture content:
    {lecture_text}
    """

    key = settings.DEEPSEEK_API_KEY
    if not key or "YAHAN_APNI" in key:
        return JsonResponse({
            "summary": f"SUMMARY (Demo Mode): This lecture has been summarized in '{student_style}' style. This is a mock response because DeepSeek API key is missing.\n\nKey Points:\n1. Basic concepts\n2. Practical examples\n3. Next steps"
        })

    try:
        response = httpx.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": settings.DEEPSEEK_MAX_TOKENS,
                "temperature": settings.DEEPSEEK_TEMPERATURE
            },
            timeout=15.0
        )
        response.raise_for_status()
        result = response.json()
        return JsonResponse({"summary": result["choices"][0]["message"]["content"]})
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return JsonResponse({"summary": "Abhi summary generate nahi ho pa rahi. DeepSeek API check karein."})

@csrf_exempt
def ask_question_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    question = body.get("question")
    context = body.get("lecture_context", "")
    
    if not question:
        return JsonResponse({"detail": "question is required."}, status=400)

    prompt = f"Context: {context}\n\nStudent question: {question}\n\nAnswer clearly and simply:"
    
    key = settings.DEEPSEEK_API_KEY
    if not key or "YAHAN_APNI" in key:
        return JsonResponse({
            "answer": f"CHATBOT (Demo): Aapka sawaal '{question}' achha hai! DeepSeek key missing hone ki wajah se main detail mein nahi bata sakta, par aap lecture notes check kar sakte hain."
        })

    try:
        response = httpx.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": settings.DEEPSEEK_MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15.0
        )
        response.raise_for_status()
        result = response.json()
        return JsonResponse({"answer": result["choices"][0]["message"]["content"]})
    except Exception as e:
        print(f"Chatbot Error: {e}")
        return JsonResponse({"answer": "Maaf kijiye, abhi main jawab nahi de pa raha hoon."})

# =============================================================
# Cluster Prediction Views
# =============================================================

@csrf_exempt
def get_student_cluster_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    test_result = parse_json(request)
    try:
        learning_style, _ = predict_learning_style(test_result)
    except Exception as e:
        return JsonResponse({"detail": f"Error running ML model: {str(e)}"}, status=400)
    
    content_map = {
        "visual_learner": ["infographics", "video_lectures", "diagrams"],
        "conceptual_thinker": ["theory_articles", "case_studies", "debates"],
        "practice_based": ["coding_exercises", "quizzes", "projects"],
        "step_by_step": ["structured_notes", "guided_tutorials", "checklists"]
    }
    
    return JsonResponse({
        "learning_style": learning_style,
        "recommended_content_types": content_map.get(learning_style, ["video_lectures"])
    })

# =============================================================
# Aptitude Test Views
# =============================================================

QUESTIONS_BANK = {
    "logical": [
        {"id":"L1","section":"logical",  "question":"If MANGO is written as NBOHI, how will APPLE be written?",                             "options":["BQQMF","CQQNF","BQPMF","CQQOF"],           "correct":"BQQMF","marks":20},
        {"id":"L2","section":"logical",  "question":"What will be the next number in the series? 2, 6, 12, 20, 30, ?",                                     "options":["40","42","38","44"],                       "correct":"42","marks":20},
        {"id":"L3","section":"logical",  "question":"Three friends A, B, C. A is taller than B. C is taller than A. Who is tallest?",              "options":["A","B","C","Equal"],                     "correct":"C","marks":20},
        {"id":"L4","section":"logical",  "question":"A clock shows 3:15. What is the angle between minute and hour hand?",                 "options":["0°","7.5°","15°","22.5°"],                 "correct":"7.5°","marks":20},
        {"id":"L5","section":"logical",  "question":"5 machines make 5 widgets in 5 minutes. How many will 100 machines make in 100 minutes?",  "options":["100","500","1000","10000"],                "correct":"10000","marks":20},
    ],
    "verbal": [
        {"id":"V1","section":"verbal",   "question":"What is the correct meaning of 'Ephemeral'?",                                                          "options":["Very old","Very short-lived","Very big","Difficult"], "correct":"Very short-lived","marks":20},
        {"id":"V2","section":"verbal",   "question":"Ramesh wakes at 6, exercises, then breakfast, office at 9.\nWhen does he go to office?", "options":["At 6","Before breakfast","At 9","After exercise"],                               "correct":"At 9","marks":20},
        {"id":"V3","section":"verbal",   "question":"What is the antonym of 'Benevolent'?",                                                           "options":["Kind","Malevolent","Generous","Helpful"],                                               "correct":"Malevolent","marks":20},
        {"id":"V4","section":"verbal",   "question":"Choose the correct sentence:",                                                                  "options":["He don't know the answer.","He doesn't knows the answer.","He doesn't know the answer.","He not know."], "correct":"He doesn't know the answer.","marks":20},
        {"id":"V5","section":"verbal",   "question":"What does 'Verbose' mean?",                                                                    "options":["Speaking very little","Speaking directly","Speaking too much","Explaining clearly"],            "correct":"Speaking too much","marks":20},
    ],
    "numerical": [
        {"id":"N1","section":"numerical","question":"Train travels at 60 km/h. Distance in 2.5 hours?",                                  "options":["120 km","140 km","150 km","160 km"],       "correct":"150 km","marks":20},
        {"id":"N2","section":"numerical","question":"Item bought for Rs.800, sold for Rs.1000. Profit %?",                                    "options":["20%","25%","15%","30%"],                   "correct":"25%","marks":20},
        {"id":"N3","section":"numerical","question":"Average of 5 numbers is 18. Remove 10 — average of remaining 4?",                      "options":["18","20","22","25"],                       "correct":"20","marks":20},
        {"id":"N4","section":"numerical","question":"2^2 + 3^3 + 4^0 = ?",                                                                        "options":["30","32","34","36"],                       "correct":"32","marks":20},
        {"id":"N5","section":"numerical","question":"A can do work in 10 days, B in 15 days. Together how many days?",                         "options":["5 days","6 days","7 days","8 days"],           "correct":"6 days","marks":20},
    ],
    "memory": [
        {"id":"M1","section":"memory",   "question":"Remember list: Apple, Banana, Cherry, Date, Elderberry.\nThird fruit?",                    "options":["Banana","Cherry","Date","Apple"],          "correct":"Cherry","marks":20},
        {"id":"M2","section":"memory",   "question":"Remember numbers: 47, 83, 29, 61, 15.\nSecond number?",                                      "options":["47","29","83","61"],                       "correct":"83","marks":20},
        {"id":"M3","section":"memory",   "question":"'The quick brown fox jumps over the lazy dog.'\nAdjective for 'fox'?",                   "options":["quick","brown","lazy","slow"],             "correct":"brown","marks":20},
        {"id":"M4","section":"memory",   "question":"Colors: Red, Blue, Green, Yellow, Purple, Orange.\nFourth?",                               "options":["Green","Yellow","Purple","Blue"],          "correct":"Yellow","marks":20},
        {"id":"M5","section":"memory",   "question":"Capitals: France-Paris, Japan-Tokyo, India-Delhi, Australia-Canberra.\nAustralia's capital?","options":["Sydney","Melbourne","Canberra","Brisbane"], "correct":"Canberra","marks":20},
    ],
    "attention": [
        {"id":"A1","section":"attention","question":"'The cat sat on the mat near the window while the dog slept under the table.'\nHow many 'the'?", "options":["3","4","5","6"],                         "correct":"5","marks":20},
        {"id":"A2","section":"attention","question":"Odd one out:\n2, 4, 7, 8, 12, 16",                                                           "options":["4","7","12","16"],                         "correct":"7","marks":20},
        {"id":"A3","section":"attention","question":"What's wrong?\n'He buyed milk and payed at counter.'",                                       "options":["Only buyed wrong","Both buyed and payed wrong","Nothing wrong","Only payed wrong"], "correct":"Both buyed and payed wrong","marks":20},
        {"id":"A4","section":"attention","question":"Pattern: △○△△○△△△○?\nNext?",                                                                "options":["△","○","□","△○"],                         "correct":"△","marks":20},
        {"id":"A5","section":"attention","question":"Odd one out:\nTable, Chair, Lamp, Sofa, Pen, Desk",                                          "options":["Lamp","Pen","Sofa","Table"],               "correct":"Pen","marks":20},
    ],
}

ML_FEATURES = ["logical", "verbal", "numerical", "memory", "attention"]

def calculate_section_scores(answers: list) -> dict:
    all_qs = {q["id"]: q for sec in QUESTIONS_BANK.values() for q in sec}
    answers_dict = {a.get("question_id"): a.get("answer") for a in answers}
    section_earned = {s: 0 for s in ML_FEATURES}
    section_max = {s: 0 for s in ML_FEATURES}
    
    for section, questions in QUESTIONS_BANK.items():
        for q in questions:
            student_ans = (answers_dict.get(q["id"]) or "").strip()
            is_correct = (student_ans == q["correct"].strip())
            earned = q["marks"] if is_correct else 0
            section_earned[section] += earned
            section_max[section] += q["marks"]
            
    normalized = {sec: round((section_earned[sec] / section_max[sec]) * 100, 1) if section_max[sec] > 0 else 0.0 for sec in ML_FEATURES}
    normalized["total"] = round(sum(normalized[f] for f in ML_FEATURES) / 5, 1)
    return normalized

def run_ml_prediction(section_scores: dict) -> tuple[int, str, float]:
    scores = {f: section_scores[f] for f in ML_FEATURES}
    try:
        cluster_id, style = predict_cluster_id(scores)
        _, confidence = predict_learning_style(scores)
        return cluster_id, style, round(confidence, 3)
    except Exception:
        # Fallback if scikit-learn is not available
        dominant = max(scores, key=scores.get)
        fallback = {
            'logical': (1, 'conceptual_thinker'),
            'verbal': (0, 'visual_learner'),
            'numerical': (2, 'practice_based'),
            'memory': (3, 'step_by_step'),
            'attention': (2, 'practice_based')
        }
        fallback_res = fallback.get(dominant, (0, 'visual_learner'))
        return fallback_res[0], fallback_res[1], 0.70

def _style_details(style: str) -> dict:
    details = {
        "visual_learner":     {"title":"Visual Learner","description":"Diagrams aur visual content se best seekhte ho.","strengths":["Visual memory strong","Diagrams helpful"],"content_types":["Video Lectures","Infographics"],"study_tip":"Mind maps banao!"},
        "conceptual_thinker": {"title":"Conceptual Thinker","description":"Deep theory aur 'why' samajhna pasand hai.","strengths":["Analytical thinking","Complex concepts"],"content_types":["Theory Articles","Case Studies"],"study_tip":"Pehle theory samjho!"},
        "practice_based":     {"title":"Practice-Based Learner","description":"Kar ke seekhte ho tum.","strengths":["Hands-on projects","Problem solving"],"content_types":["Coding Exercises","Labs"],"study_tip":"Practice first!"},
        "step_by_step":       {"title":"Step-by-Step Learner","description":"Structured content se best seekhte ho.","strengths":["Sequential thinking","Checklists"],"content_types":["Structured Notes","Tutorials"],"study_tip":"One step at a time!"},
    }
    return details.get(style, details["visual_learner"])

@csrf_exempt
@jwt_required(role="student")
def get_questions_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    sections = []
    for section, questions in QUESTIONS_BANK.items():
        safe_qs = [{"id":q["id"],"section":q["section"],"question":q["question"],"options":q["options"],"marks":q["marks"]} for q in questions]
        sections.append({
            "section_id": section,
            "section_name": section.title(),
            "questions": safe_qs,
            "total_marks": sum(q["marks"] for q in questions),
        })
    return JsonResponse({"sections": sections, "total_marks": 500, "time_limit_min": 30})

@csrf_exempt
@jwt_required(role="student")
def submit_test_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    body = parse_json(request)
    answers = body.get("answers", [])
    
    # Cooldown check
    last_test = TestResult.objects.filter(user=request.user).order_by("-submitted_at").first()
    if last_test:
        delta = dj_timezone.now() - last_test.submitted_at
        if delta.days < settings.RETEST_COOLDOWN_DAYS:
            return JsonResponse({"detail": f"Test {settings.RETEST_COOLDOWN_DAYS - delta.days} din baad de sakte ho."}, status=429)

    scores = calculate_section_scores(answers)
    section_scores = {f: scores[f] for f in ML_FEATURES}
    cluster_id, style, confidence = run_ml_prediction(section_scores)
    
    # Save result
    TestResult.objects.create(
        user=request.user,
        scores=section_scores,
        cluster=cluster_id,
        learning_style=style
    )
    
    # Update User Profile
    request.user.learning_style = style
    request.user.cluster_id = cluster_id
    request.user.save()
    
    return JsonResponse({
        "message": "Test submitted successfully",
        "learning_style": style,
        "cluster_id": cluster_id,
        "result": {
            "score_summary": scores,
            "learning_style": style,
            "details": _style_details(style)
        }
    }, status=201)

@csrf_exempt
@jwt_required(role="student")
def get_results_view(request):
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    records = TestResult.objects.filter(user=request.user).order_by("-submitted_at")
    if not records.exists():
        return JsonResponse({"detail": "Pehle test dein!"}, status=404)
        
    latest = records.first()
    return JsonResponse({
        "latest": {
            "scores": latest.scores,
            "style": latest.learning_style,
            "date": latest.submitted_at.isoformat(),
            "details": _style_details(latest.learning_style)
        },
        "history": [{"id": r.id, "date": r.submitted_at.isoformat(), "style": r.learning_style} for r in records]
    })
