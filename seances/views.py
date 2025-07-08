from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .forms import PriseSeanceForm
from .models import Seance
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
            request.session['show_rdv_modal'] = True
            return redirect("accounts:dashboard_client")
    else:
        form = PriseSeanceForm(client=request.user, coach=coach)

    return render(
        request,
        "seances/prise_rdv.html",
        {"form": form, "coach": coach},
    )