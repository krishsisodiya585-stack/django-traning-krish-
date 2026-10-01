from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tests/<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    path("results/<int:attempt_id>/", views.result, name="result"),
    path("history/", views.history, name="history"),
]