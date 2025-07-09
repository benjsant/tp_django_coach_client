from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone

from .forms import PriseSeanceForm,FinRdvForm
from .models import Seance,RdvHistorique

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime, now, localdate
from django.views.decorators.cache import never_cache
from .forms import ModifierNoteHistoriqueForm 

User = get_user_model()

@login_required
def prise_rdv(request):
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