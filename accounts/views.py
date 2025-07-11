from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from .forms import CustomLoginForm, CustomSignupForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required 
from django.views.decorators.cache import never_cache
from django.utils.timezone import now, localtime,localdate
from seances.models import Seance
from datetime import date
"""
Ce module contient des vues pour la gestion de l'authentification des utilisateurs et des tableaux de bord dans une application Django.

Fonctions :
- login_user : Gère la connexion des utilisateurs.
- logout_user : Gère la déconnexion des utilisateurs.
- signup_user : Gère l'inscription des nouveaux utilisateurs.
- dashboard : Redirige les utilisateurs vers leur tableau de bord approprié.
- dashboard_client : Affiche le tableau de bord pour les clients.
- dashboard_coach : Affiche le tableau de bord pour les coachs.

"""
@never_cache
def login_user(request):
    """
    Gère la connexion des utilisateurs.

    Si la méthode de la requête est POST, le formulaire de connexion est validé.
    Si les identifiants sont corrects, l'utilisateur est connecté et redirigé vers le tableau de bord.
    Sinon, un message d'erreur est affiché.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page de connexion avec le formulaire ou une redirection vers le tableau de bord.
    """
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
    else:
        form = CustomLoginForm()

    return render(request, "accounts/login.html", {
        "form": form,
    })

def logout_user(request):
    """
    Gère la déconnexion des utilisateurs.

    Déconnecte l'utilisateur actuel et affiche un message de succès.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Une redirection vers la page d'accueil.
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("core:index")

@never_cache
def signup_user(request):
    """
    Gère l'inscription des nouveaux utilisateurs.

    Si la méthode de la requête est POST, le formulaire d'inscription est validé.
    Si les données sont valides, l'utilisateur est créé, ajouté au groupe "client", et connecté.
    Sinon, un message d'erreur est affiché.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page d'inscription avec le formulaire ou une redirection vers le tableau de bord.
    """
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            client_group, created = Group.objects.get_or_create(name="client")
            client_group.user_set.add(user)
            login(request,user)
            request.session['show_signup_modal'] = True
            return redirect("accounts:dashboard")
        else:
            messages.error(request,"Une erreur est survenue. Veuillez corriger les champs .")
    else:
        form = CustomSignupForm()

    return render(request, "accounts/signup.html", {
        "form": form,
    })


@login_required
@never_cache
def dashboard(request):
    """
    Redirige les utilisateurs vers leur tableau de bord approprié.

    Vérifie si l'utilisateur appartient au groupe "coach" ou "client" et redirige en conséquence.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Une redirection vers le tableau de bord du coach, du client ou la page d'accueil.
    """
    if request.user.groups.filter(name="coach").exists():
        return redirect("accounts:dashboard_coach")
    elif request.user.groups.filter(name="client").exists():
        return redirect("accounts:dashboard_client")
    else: 
        return redirect("core:index")


@login_required
@never_cache
def dashboard_client(request):
    """
    Affiche le tableau de bord pour les clients.

    Récupère les rendez-vous futurs du client connecté et les affiche dans un rendu.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page du tableau de bord du client avec les rendez-vous.
    """
    # Récupérer et supprimer la clé 'show_signup_modal' de la session
    show_signup_modal = request.session.pop('show_signup_modal', None)

    current_datetime = localtime(now())  # datetime aware au fuseau local

    mes_rendezvous = Seance.objects.filter(
        client=request.user
    ).filter(
        date__gt=current_datetime.date()
    ) | Seance.objects.filter(
        client=request.user,
        date=current_datetime.date(),
        heure_debut__gt=current_datetime.time()
    )
    mes_rendezvous = mes_rendezvous.order_by('date', 'heure_debut')

    context = {
        'is_client': True,
        'is_coach': False,
        'show_signup_modal': show_signup_modal,
        'mes_rendezvous': mes_rendezvous,
    }
    return render(request, 'accounts/dashboard_client.html', context)

@login_required
@never_cache
def dashboard_coach(request):
    """
    Affiche le tableau de bord pour les coachs.

    Récupère les rendez-vous du jour pour le coach connecté et les affiche dans un rendu.

    Paramètres :
    - request : L'objet HttpRequest contenant les données de la requête.

    Retourne :
    - Un rendu de la page du tableau de bord du coach avec les rendez-vous du jour.
    """
    today = localdate()  # Date du jour, timezone-aware

    # Ne récupérer que les séances du jour
    rendezvous_coach = Seance.objects.filter(
        coach=request.user,
        date=today
    ).order_by('heure_debut')

    context = {
        'is_client': False,
        'is_coach': True,
        'rendezvous_coach': rendezvous_coach,
    }
    return render(request, 'accounts/dashboard_coach.html', context)
