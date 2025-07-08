from datetime import datetime, time, timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone 

from .models import Seance 

class PriseSeanceForm(forms.ModelForm):
    """
    Formulaire Bootstrap pour qu’un client réserve un créneau chez le coach.
    Les validations métier (créneau dispo, marge de 10 min, horaires autorisés)
    sont faites ici.
    """

    class Meta:
        model = Seance
        fields = ["date","heure_debut","objet"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type":"date","class":"form-control"}
            ),
            "heure_debut":forms.TimeInput(
                attrs={"type":"time","class":"form-control"}
            ),
            "objet":forms.TextInput(
                attrs={"class":"form-control",
                        "placeholder":"Objet de la séance....",
                       }
            ),
        }

     # --- on injecte le client et le coach depuis la vue -------------------
    def __init__(self, *args, client=None, coach=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.coach = coach

    # --- validations globales --------------------------------------------
    def clean(self):
        cleaned = super().clean()
        date = cleaned.get("date")
        heure = cleaned.get("heure_debut")

        if not date or not heure:
            return cleaned
        
        # 1) Créneau dans le futur
        dt = datetime.combine(date,heure)
        if timezone.make_aware(dt) < timezone.now():
            raise ValidationError("Impossible de réserver un créneau dans le passé.")
        # # 2) Horaires autorisés (8h-20h)
        # HORAIRE_MIN = time(8,0)
        # HORAIRE_MAX = time(20,0)
        # if not (HORAIRE_MIN <= heure <= HORAIRE_MAX):
        #     raise ValidationError("Les rendez-vous doivent être pris entre 08h00 et 20h00.")
        
       
        
        # 🚫 Interdire les weekends
        if date.weekday() in (5, 6):
            raise ValidationError("Les rendez-vous ne sont pas disponibles le week-end (samedi ou dimanche).")

        # 3) Conflits et délai mini 10 min pour ce coach
        delta = timedelta(minutes=10)
        clash = (
            Seance.objects
            .filter(coach=self.coach, date=date)
            .exclude(heure_debut__lt=(datetime.combine(date, heure) - delta).time())
            .exclude(heure_debut__gt=(datetime.combine(date, heure) + delta).time())
        )
        if clash.exists():
            raise ValidationError("Ce créneau est trop proche d'un autre rendez-vous.")
        
        
        return cleaned
    
    # --- save ----------------------------------------------------------------
    def save(self, commit = True):
        seance = super().save(commit=False)
        seance.client = self.client
        seance.coach = self.coach
        if commit:
            seance.full_clean()
            seance.save()
        return seance