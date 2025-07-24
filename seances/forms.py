from datetime import datetime, timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone 

from .models import Seance


class PriseSeanceForm(forms.ModelForm):
    OBJET_CHOICES = [
        ("Coaching personnel", "Coaching personnel"),
        ("Gestion du stress", "Gestion du stress"),
        ("Développement de la confiance en soi", "Développement de la confiance en soi"),
    ]

    objet = forms.ChoiceField(
        choices=OBJET_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Objet de la séance",
        initial="Coaching personnel"
    )

    class Meta:
        model = Seance
        fields = ["date", "heure_debut", "objet"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "heure_debut": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }

    def __init__(self, *args, client=None, coach=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = client
        self.coach = coach

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get("date")
        heure = cleaned.get("heure_debut")

        if not date or not heure:
            return cleaned

        # Créneau dans le futur
        dt = datetime.combine(date, heure)
        if timezone.make_aware(dt) < timezone.now():
            raise ValidationError("Impossible de réserver un créneau dans le passé.")

        # Interdire les weekends
        if date.weekday() in (5, 6):
            raise ValidationError("Les rendez-vous ne sont pas disponibles le week-end (samedi ou dimanche).")

        # Conflit de créneaux pour le coach
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

    def save(self, commit=True):
        seance = super().save(commit=False)
        seance.client = self.client
        seance.coach = self.coach
        if commit:
            seance.full_clean()
            seance.save()
        return seance


class FinRdvForm(forms.Form):
    notes = forms.CharField(
        label="Note ou commentaire (facultatif)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': "Notes ou retour sur la séance"
        }),
        required=False
    )


class ModifierNoteHistoriqueForm(forms.ModelForm):
    class Meta:
        model = Seance  # ✅ Changement ici : on utilise Seance au lieu de RdvHistorique
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "Modifier ou ajouter une note sur cette séance"
            }),
        }
        labels = {
            'message': "Note ou commentaire",
        }
