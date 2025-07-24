from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import localtime, now

from .forms import PriseSeanceForm, FinRdvForm, ModifierNoteHistoriqueForm
from .models import Seance
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

User = get_user_model()

@login_required
def prise_rdv(request):
    coachs = User.objects.filter(groups__name='coach')
    if not coachs.exists():
        return redirect("accounts:dashboard_client")

    coach = coachs.first()
    if request.method == "POST":
        form = PriseSeanceForm(request.POST, client=request.user, coach=coach)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre rendez-vous a bien été enregistré.<br /> Vous pouvez le consulter dans votre espace personnel.")
            return redirect("accounts:dashboard_client")
    else:
        form = PriseSeanceForm(client=request.user, coach=coach)

    return render(request, "seances/prise_rdv.html", {"form": form, "coach": coach})


@require_POST
@login_required
def annuler_seance(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id)
    if request.user != seance.client and request.user != seance.coach:
        messages.error(request, "Vous n’avez pas l’autorisation d’annuler ce rendez-vous.")
        return redirect("accounts:dashboard")

    note = request.POST.get("note", "")
    code_rdv = 3 if request.user == seance.client else 4
    seance.code_rdv = code_rdv
    seance.message = note
    seance.save()

    messages.success(request, "Le rendez-vous a été annulé.")
    return redirect("accounts:dashboard_client" if request.user.groups.filter(name="client").exists() else "accounts:dashboard_coach")


@login_required
@require_POST
def marquer_absent(request, seance_id):
    seance = get_object_or_404(Seance, id=seance_id, coach=request.user)
    seance.code_rdv = 2
    seance.message = "Marqué comme absent par le coach."
    seance.save()
    messages.success(request, "Le client a été marqué comme absent.")
    return redirect("accounts:dashboard_coach")


@login_required
@require_POST
def confirmer_fin_rdv(request, rdv_id):
    rdv = get_object_or_404(Seance, id=rdv_id, coach=request.user)
    form = FinRdvForm(request.POST)
    if form.is_valid():
        rdv.code_rdv = 1
        rdv.message = form.cleaned_data['notes']
        rdv.save()
        messages.success(request, "Le rendez-vous a été marqué comme terminé.")
    else:
        messages.error(request, "Une erreur est survenue. Merci de réessayer.")
    return redirect("accounts:dashboard_coach")


@login_required
@never_cache
def historique_client(request):
    now_local = localtime(now())
    today = now_local.date()
    current_time = now_local.time()

    # Séances passées (date < aujourd’hui)
    anciennes_seances = Seance.objects.filter(
        client=request.user,
        date__lt=today
    )

    # Séances du jour dont l’heure est déjà passée
    seances_du_jour_terminees = Seance.objects.filter(
        client=request.user,
        date=today,
        heure_debut__lt=current_time
    )

    # Union des deux ensembles
    historiques = (anciennes_seances | seances_du_jour_terminees).order_by('-date', '-heure_debut')

    return render(request, 'seances/historique_client.html', {
        'historiques': historiques,
        'today': today,
        'is_client': True,
        'is_coach': False,
    })




@login_required
@never_cache
def historique_coach(request):
    coach = request.user
    today = timezone.localdate()

    historiques = Seance.objects.filter(
        coach=coach,
        date__lte=today
    ).exclude(code_rdv=0).order_by('-date', '-heure_debut')

    seances_oubliees = Seance.objects.filter(
        coach=coach,
        date__lt=today,
        code_rdv=0
    ).order_by('-date', '-heure_debut')

    if request.method == "POST":
        rdv_id = request.POST.get("rdv_id")
        rdv = get_object_or_404(Seance, id=rdv_id, coach=coach)
        notes = request.POST.get("notes", "").strip()
        if notes:
            rdv.message = notes
            rdv.save()
            messages.success(request, "Note mise à jour avec succès.")
        else:
            messages.error(request, "La note ne peut pas être vide.")
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

    futures_seances = Seance.objects.filter(
        coach=coach,
        date__gte=tomorrow,
        code_rdv=0  # seulement les futurs rdv non traités
    ).order_by('date', 'heure_debut')

    context = {
        'futures_seances': futures_seances,
        'is_coach': True,
    }
    return render(request, 'seances/futures_sessions_coach.html', context)
