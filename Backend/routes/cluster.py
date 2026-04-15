from fastapi import APIRouter
import sys
import os

# Add Backend and Root to path for direct execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "Backend")
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
if BACKEND_DIR not in sys.path: sys.path.append(BACKEND_DIR)

from ML.predict_cluster import predict_learning_style

router = APIRouter()

@router.post("/cluster/predict")
async def get_student_cluster(test_result: dict):
    """
    Receives aptitude test scores, returns learning style cluster
    """
    learning_style, _ = predict_learning_style(test_result)
    
    content_map = {
        "visual_learner": ["infographics", "video_lectures", "diagrams"],
        "conceptual_thinker": ["theory_articles", "case_studies", "debates"],
        "practice_based": ["coding_exercises", "quizzes", "projects"],
        "step_by_step": ["structured_notes", "guided_tutorials", "checklists"]
    }
    
    return {
        "learning_style": learning_style,
        "recommended_content_types": content_map[learning_style]
    }