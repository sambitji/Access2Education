from django.urls import path
from . import views

urlpatterns = [
    # General / Health
    path('', views.root_view, name='root'),
    path('health', views.health_view, name='health'),

    # Authentication
    path('auth/register', views.register_view, name='register'),
    path('auth/login', views.login_view, name='login'),
    path('auth/refresh', views.refresh_token_view, name='token_refresh'),
    path('auth/logout', views.logout_view, name='logout'),
    path('auth/me', views.me_view, name='profile'),
    path('auth/forgot-password', views.forgot_password_view, name='forgot_password'),
    path('auth/reset-password', views.reset_password_view, name='reset_password'),

    # Content & Recommendations
    path('content/recommendations', views.get_recommendations_view, name='content_recommendations'),
    path('content/progress', views.get_my_progress_view, name='content_progress'),
    path('content/complete/<str:content_id>', views.mark_complete_view, name='mark_complete'),
    path('content/all', views.get_all_content_view, name='all_content'),
    path('content/subjects', views.get_subjects_view, name='all_subjects'),

    # Spaced Repetition
    path('spaced-repetition/cards', views.add_card_view, name='add_card'),
    path('spaced-repetition/review', views.submit_review_view, name='submit_review'),
    path('spaced-repetition/due', views.get_due_cards_view, name='get_due_cards'),

    # Chatbot
    path('chatbot/summarize', views.summarize_lecture_view, name='chatbot_summarize'),
    path('chatbot/ask', views.ask_question_view, name='chatbot_ask'),

    # Learning DNA Cluster
    path('cluster/predict', views.get_student_cluster_view, name='predict_cluster'),

    # Aptitude Test
    path('test/questions', views.get_questions_view, name='test_questions'),
    path('test/submit', views.submit_test_view, name='test_submit'),
    path('test/result', views.get_results_view, name='test_result_alias'),
    path('test/results', views.get_results_view, name='test_results'),
]
