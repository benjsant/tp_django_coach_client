from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import time


class Seance(models.Model):
    """
    Représente une séance entre un client et un coach.

    Attributs :
    - client (ForeignKey) : L'utilisateur client participant à la séance.
    - coach (ForeignKey) : L'utilisateur coach qui dirige la séance.
    - date (DateField) : La date de la séance.
    - heure_debut (TimeField) : L'heure de début de la séance.
    - objet (CharField) : L'objet ou le sujet de la séance.

    Méthodes :
    - __str__() : Retourne une représentation sous forme de chaîne de caractères de la séance.
    - clean() : Valide que l'heure de début de la séance est comprise entre 08h00 et 20h00.

    Meta :
    - unique_together : Assure qu'il n'y a pas de conflits de rendez-vous pour un même coach à la même date et heure.
    - ordering : Définit l'ordre par défaut des séances, triées par date et heure de début.
    """
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
    """
    Enregistre l'historique des rendez-vous.

    Attributs :
    - client (ForeignKey) : L'utilisateur client associé à l'historique du rendez-vous.
    - coach (ForeignKey) : L'utilisateur coach associé à l'historique du rendez-vous.
    - date (DateField) : La date du rendez-vous.
    - heure_debut (TimeField) : L'heure de début du rendez-vous.
    - objet (CharField) : L'objet ou le sujet du rendez-vous.
    - code_rdv (IntegerField) : Le code de statut du rendez-vous, avec des choix prédéfinis (Présent, Absent, Annulé par le client, Annulé par le coach).
    - notes (TextField) : Des notes supplémentaires concernant le rendez-vous, pouvant être laissées vides.

    Méthodes :
    - __str__() : Retourne une représentation sous forme de chaîne de caractères de l'historique du rendez-vous.

    Meta :
    - ordering : Définit l'ordre par défaut des historiques de rendez-vous, triés par date et heure de début, en ordre décroissant.

    NOTES: 
    A changer absolument !!!!! 
    """
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
