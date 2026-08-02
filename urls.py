"""
Root URL configuration for the CorrectWay project.

Maps to the original Express routes:
  server.js            -> "/" (health check dropped; Django serves pages directly)
  routes/auth.js        -> /register, /login, /logout ("/api/auth/*" in the original)
  routes/quiz.js         -> /quiz, /quiz/submit, /history ("/api/quiz/*" in the original)
"""
from django.contrib import admin
from django.urls import path

from careers import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("quiz/", views.quiz_view, name="quiz"),
    path("quiz/submit/", views.quiz_submit, name="quiz_submit"),
    path("results/", views.results_view, name="results"),
    path("history/", views.history_view, name="history"),
    # New pages that round this out into a complete official website:
    path("about/", views.about_view, name="about"),
    path("careers-directory/", views.careers_directory_view, name="careers_directory"),
    path("faq/", views.faq_view, name="faq"),
    path("contact/", views.contact_view, name="contact"),
    path("privacy/", views.privacy_view, name="privacy"),
    path("terms/", views.terms_view, name="terms"),
    path("profile/", views.profile_view, name="profile"),
]
