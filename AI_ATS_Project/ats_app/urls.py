from django.urls import path
from ats_app import views

urlpatterns = [
    # Auth
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Pages
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("upload/", views.upload_view, name="upload"),
    path("result/<str:result_id>/", views.result_view, name="result"),
    path("career-path/<str:result_id>/", views.career_path_view, name="career_path"),
    path("admin-panel/", views.admin_panel_view, name="admin_panel"),

    # API Endpoints
    path("upload_resume", views.upload_resume, name="api_upload_resume"),
    path("analyze_resume", views.analyze_resume, name="api_analyze_resume"),
    path("ats_score", views.ats_score, name="api_ats_score"),
    path("skill_gap", views.skill_gap, name="api_skill_gap"),
    path("career_path", views.career_path_api, name="api_career_path"),
    path("ranking", views.ranking, name="api_ranking"),
]
