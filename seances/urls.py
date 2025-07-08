from django.urls import path

from . import views

app_name = "seances"
urlpatterns = [
     path("prise_rdv/", views.prise_rdv, name="prise_rdv"),
]
