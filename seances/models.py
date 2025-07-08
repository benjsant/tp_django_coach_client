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
