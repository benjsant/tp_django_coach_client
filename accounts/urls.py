from django.urls import path

from . import views


# app_name = "core"
# urlpatterns = [
#     path("", views.IndexView.as_view(), name="index"),

# ]

app_name = "accounts"
urlpatterns = [
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("signup/", views.signup_user, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/client/", views.dashboard_client, name="dashboard_client"),
    path("dashboard/coach/", views.dashboard_coach, name="dashboard_coach"),
]