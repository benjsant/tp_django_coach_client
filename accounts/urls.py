from django.urls import path

from . import views


# app_name = "core"
# urlpatterns = [
#     path("", views.IndexView.as_view(), name="index"),

# ]

urlpatterns = [
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.signup_user, name="signup"),
    path("dashboard/", views.dashboard_user, name="dashboard"),
]