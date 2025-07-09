from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time

class Seance(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seances")
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seances_coach")  # ✅ Ajout ici
    date = models.DateField()
    heure_debut = models.TimeField()
    objet = models.CharField(max_length=255)

    def __str__(self):
        return f"Rdv avec {self.client.username} avec {self.coach.username} le {self.date} à {self.heure_debut}"

    def clean(self):
        if self.heure_debut < time(8, 0) or self.heure_debut > time(20, 0):
            raise ValidationError("Les rendez-vous doivent être pris entre 08h00 et 20h00.")

    class Meta:
        unique_together = ("date", "heure_debut", "coach")  # ✅ Important : éviter conflit entre coachs
        ordering = ["date", "heure_debut"]


class RdvHistorique(models.Model):
    CODE_CHOIX = [
        (1, "Présent"),
        (2, "Absent"),
        (3, "Annulé par le client"),
        (4, "Annulé par le coach"),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rdv_historiques")
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rdv_historiques_coach")
    date = models.DateField()
    heure_debut = models.TimeField()
    objet = models.CharField(max_length=255)
    code_rdv = models.IntegerField(choices=CODE_CHOIX)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Historique {self.get_code_rdv_display()} - {self.client.username} avec {self.coach.username} le {self.date}"

    class Meta:
        ordering = ["-date", "-heure_debut"]
