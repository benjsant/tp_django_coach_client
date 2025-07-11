from django.urls import path

from . import views
# path("futur_coach/", views.historique_client , name="histo_client")
app_name = "seances"
urlpatterns = [
     path("prise_rdv/", views.prise_rdv, name="prise_rdv"),
     path("annuler/<int:seance_id>/", views.annuler_seance, name="annuler_seance"),
     path("rdv/<int:rdv_id>/fin/", views.confirmer_fin_rdv, name="confirmer_fin_rdv"),
     path("absent/<int:seance_id>/", views.marquer_absent, name="marquer_absent"),
     path("historique_client/", views.historique_client , name="historique_client"),
     path("historique_coach/", views.historique_coach , name="historique_coach"),
     path('futures_sessions/', views.futures_sessions_coach, name='futures_sessions_coach'),
]
