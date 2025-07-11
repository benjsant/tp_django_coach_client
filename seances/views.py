from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import localtime, now, localdate

from .forms import PriseSeanceForm,FinRdvForm
from .forms import ModifierNoteHistoriqueForm 

from .models import Seance,RdvHistorique

from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

"""
Ce module contient des vues pour la gestion des rendez-vous et de l'historique des séances dans une application Django.

Fonctions :
- prise_rdv : Permet à un client de prendre un rendez-vous avec un coach.
- annuler_seance : Permet à un client ou à un coach d'annuler une séance.
- marquer_absent : Permet à un coach de marquer un client comme absent.
- confirmer_fin_rdv : Permet à un coach de confirmer la fin d'un rendez-vous.
- historique_client : Affiche l'historique des rendez-vous d'un client.
- historique_coach : Affiche l'historique des rendez-vous d'un coach et permet de modifier des notes.
- futures_sessions_coach : Affiche les séances futures d'un coach.

"""

User = get_user_model()

@login_required
def prise_rdv(request):
    """
    Permet à un client de prendre un rendez-vous avec un coach.

    Récupère la liste des coachs disponibles et affiche un formulaire pour la prise de rendez-vous.
    Si le formulaire est soumis et valide, le rendez-vous est enregistré.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page de prise de rendez-vous avec le formulaire et le coach sélectionné.
    """
    # Récupérer tous les coachs (users dans groupe 'coach')
    coachs = User.objects.filter(groups__name='coach')

    if not coachs.exists():
        #messages.error(request, "Aucun coach disponible pour le moment.")
        return redirect("accounts:dashboard_client")

    coach = coachs.first()

    if request.method == "POST":
        form = PriseSeanceForm(request.POST, client=request.user, coach=coach)
        if form.is_valid():
            form.save()
            # Activer modal dans la session pour affichage sur dashboard client
            messages.success(request, "Votre rendez-vous a bien été enregistré.<br /> Vous pouvez le consulter dans votre espace personnel.")
            return redirect("accounts:dashboard_client")
    else:
        form = PriseSeanceForm(client=request.user, coach=coach)

    return render(
        request,
        "seances/prise_rdv.html",
        {"form": form, "coach": coach},
    )

@require_POST
@login_required
def annuler_seance(request, seance_id):
    """
    Permet à un client ou à un coach d'annuler une séance.

    Vérifie que l'utilisateur a l'autorisation d'annuler la séance, puis archive le rendez-vous dans l'historique
    avant de supprimer la séance.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.
    - seance_id : L'identifiant de la séance à annuler.

    Retourne :
    - Une redirection vers le tableau de bord approprié avec un message de succès.
    """
    seance = get_object_or_404(Seance, id=seance_id)

    # Vérification : seul le client ou le coach concerné peut annuler
    if request.user != seance.client and request.user != seance.coach:
        messages.error(request, "Vous n’avez pas l’autorisation d’annuler ce rendez-vous.")
        return redirect("accounts:dashboard")

    note = request.POST.get("note", "")
    code_rdv = 3 if request.user == seance.client else 4  # Code 3 = client, 4 = coach

    # Transfert vers historique
    RdvHistorique.objects.create(
        client=seance.client,
        coach=seance.coach,
        date=seance.date,
        heure_debut=seance.heure_debut,
        objet=seance.objet,
        code_rdv=code_rdv,
        notes=note
    )

    # Suppression du rendez-vous
    seance.delete()

    messages.success(request, "Le rendez-vous a été annulé et archivé.")
    return redirect("accounts:dashboard_client" if request.user.groups.filter(name="client").exists() else "accounts:dashboard_coach")

@login_required
@require_POST
def marquer_absent(request, seance_id):
    """
    Permet à un coach de marquer un client comme absent.

    Crée un enregistrement dans l'historique des rendez-vous avec le code d'absence, puis supprime la séance.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.
    - seance_id : L'identifiant de la séance à marquer comme absente.

    Retourne :
    - Une redirection vers le tableau de bord du coach avec un message de succès.
    """
    seance = get_object_or_404(Seance, id=seance_id, coach=request.user)

    RdvHistorique.objects.create(
        client=seance.client,
        coach=seance.coach,
        date=seance.date,
        heure_debut=seance.heure_debut,
        objet=seance.objet,
        code_rdv=2,  # 🚫 Absent
        notes="Marqué comme absent par le coach."
    )

    seance.delete()

    messages.success(request, "Le client a été marqué comme absent.")
    return redirect("accounts:dashboard_coach")

@login_required
@require_POST
def confirmer_fin_rdv(request, rdv_id):
    """
    Permet à un coach de confirmer la fin d'un rendez-vous.

    Crée un enregistrement dans l'historique des rendez-vous avec le code de présence, puis supprime la séance.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.
    - rdv_id : L'identifiant du rendez-vous à confirmer.

    Retourne :
    - Une redirection vers le tableau de bord du coach avec un message de succès ou d'erreur.
    """
    rdv = get_object_or_404(Seance, id=rdv_id, coach=request.user)
    form = FinRdvForm(request.POST)

    if form.is_valid():
        RdvHistorique.objects.create(
            client=rdv.client,
            coach=rdv.coach,
            date=rdv.date,
            heure_debut=rdv.heure_debut,
            objet=rdv.objet,
            code_rdv=1,  # ✅ Présent
            notes=form.cleaned_data['notes']
        )
        rdv.delete()
        messages.success(request, "Le rendez-vous a été marqué comme terminé.")
    else:
        messages.error(request, "Une erreur est survenue. Merci de réessayer.")

    return redirect("accounts:dashboard_coach")

@login_required
@never_cache
def historique_client(request):
    """
    Affiche l'historique des rendez-vous d'un client.

    Récupère tous les anciens rendez-vous du client connecté et les affiche dans un rendu.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page d'historique des rendez-vous du client.
    """
    current_datetime = localtime(now())  # datetime aware au fuseau local

    # On récupère tous les anciens rendez-vous du client connecté
    mes_rdv_historiques = RdvHistorique.objects.filter(
        client=request.user
    ).filter(
        date__lt=current_datetime.date()
    ) | RdvHistorique.objects.filter(
        client=request.user,
        date=current_datetime.date(),
        heure_debut__lt=current_datetime.time()
    )

    mes_rdv_historiques = mes_rdv_historiques.order_by('-date', '-heure_debut')

    context = {
        'is_client': True,
        'is_coach': False,
        'mes_rdv_historiques': mes_rdv_historiques,
    }
    return render(request, 'seances/historique_client.html', context)

@login_required
@never_cache
def historique_coach(request):
    """
    Affiche l'historique des rendez-vous d'un coach et permet de modifier des notes.

    Récupère tous les anciens rendez-vous du coach et les séances oubliées, et gère la mise à jour des notes.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page d'historique des rendez-vous du coach.
    """
    coach = request.user
    today = timezone.localdate()

    # Tous les historiques passés du coach
    historiques = RdvHistorique.objects.filter(
        coach=coach,
        date__lte=today
    ).order_by('-date', '-heure_debut')

    # IDs séances déjà traitées (date + heure)
    seances_traitees = RdvHistorique.objects.filter(coach=coach).values_list('date', 'heure_debut')

    # Séances oubliées : séances passées non traitées
    seances_oubliees = Seance.objects.filter(
        coach=coach,
        date__lt=today
    ).exclude(
        date__in=[s[0] for s in seances_traitees],
        heure_debut__in=[s[1] for s in seances_traitees],
    ).order_by('-date', '-heure_debut')

    if request.method == "POST":
        rdv_id = request.POST.get("rdv_id")
        rdv = get_object_or_404(RdvHistorique, id=rdv_id, coach=coach)
        form = ModifierNoteHistoriqueForm(request.POST, instance=rdv)
        if form.is_valid():
            form.save()
            messages.success(request, "Note mise à jour avec succès.")
        else:
            messages.error(request, "Erreur lors de la mise à jour de la note.")
        return redirect("seances:historique_coach")

    context = {
        'historique_rdv': historiques,
        'form_note': ModifierNoteHistoriqueForm(),
        'seances_oubliees': seances_oubliees,
        'has_seances_oubliees': seances_oubliees.exists(),
        'is_coach': True,
    }
    return render(request, 'seances/historique_coach.html', context)

@login_required
@never_cache
def futures_sessions_coach(request):
    """
    Affiche les séances futures d'un coach.

    Récupère toutes les séances à venir pour le coach connecté et les affiche dans un rendu.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page des futures séances du coach.
    """
    coach = request.user
    tomorrow = timezone.localdate() + timezone.timedelta(days=1)

    # Séances futures à partir de J+1 inclus
    futures_seances = Seance.objects.filter(
        coach=coach,
        date__gte=tomorrow
    ).order_by('date', 'heure_debut')

    context = {
        'futures_seances': futures_seances,
        'is_coach': True,
    }
    return render(request, 'seances/futures_sessions_coach.html', context)