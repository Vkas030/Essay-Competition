from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("submit/", views.submit_task, name="submit_task"),
    path("ranking/", views.ranking, name="ranking"),
    path("check/", views.live_check, name="live_check"),   # live check endpoint
    path("score/<int:task_id>/", views.score_page, name="score_page"),

    # FIXED ↓↓↓ you must use views.all_scores_page
    path("all-scores/", views.all_scores_page, name="all_scores"),
]
