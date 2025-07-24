from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time


class Seance(models.Model):
    """
    Représente une séance entre un client et un coach.

    Attributs :
    - client : utilisateur client
    - coach : utilisateur coach
    - date : date de la séance
    - heure_debut : heure de début de la séance
    - objet : sujet de la séance
    - code_rdv : statut du rendez-vous (1 = présent, 2 = absent, 3 = annulé client, 4 = annulé coach, 0 = non traité)
    - message : champ libre visible uniquement par le coach (remarques ou bilan)

    Méthodes :
    - __str__() : représentation en texte de la séance
    - clean() : valide l'heure
    """

    CODE_CHOIX = [
        (0, "Non traité"),
        (1, "Présent"),
        (2, "Absent"),
        (3, "Annulé par le client"),
        (4, "Annulé par le coach"),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seances")
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seances_coach")
    date = models.DateField()
    heure_debut = models.TimeField()
    objet = models.CharField(max_length=255)
    code_rdv = models.IntegerField(choices=CODE_CHOIX, default=0)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Rdv avec {self.client.username} avec {self.coach.username} le {self.date} à {self.heure_debut}"

    def clean(self):
        if self.heure_debut < time(8, 0) or self.heure_debut > time(20, 0):
            raise ValidationError("Les rendez-vous doivent être pris entre 08h00 et 20h00.")

    class Meta:
        unique_together = ("date", "heure_debut", "coach")
        ordering = ["date", "heure_debut"]
