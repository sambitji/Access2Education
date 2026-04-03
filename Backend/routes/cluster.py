from fastapi import APIRouter
import sys
sys.path.append("../ml")
from ML.predict_cluster import predict_student_cluster

router = APIRouter()

@router.post("/cluster/predict")
async def get_student_cluster(test_result: dict):
    """
    Receives aptitude test scores, returns learning style cluster
    """
    learning_style = predict_student_cluster(test_result)
    
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