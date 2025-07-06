from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from .forms import CustomLoginForm, CustomSignupForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required 
# Create your views here.

def login_user(request):
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

    return render(request, "accounts/login.html", {"form": form})

def logout_user(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("core:index")

def signup_user(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            client_group, created = Group.objects.get_or_create(name="client")
            client_group.user_set.add(user)
            login(request,user)  # connexion automatique
            request.session['show_signup_modal'] = True  # flag pour modal
            return redirect("accounts:dashboard")  # redirige vers dashboard
        else:
            messages.error(request,"Une erreur est survenue. Veuillez corriger les champs .")
    else: 
        form = CustomSignupForm()

    return render(request, "accounts/signup.html",{"form":form})

@login_required
def dashboard(request):
    if request.user.groups.filter(name="coach").exists():
        return redirect("accounts:dashboard_coach")
    elif request.user.groups.filter(name="client").exists():
        return redirect("accounts:dashboard_client")
    else: 
        return redirect("core:index")
    
@login_required
def dashboard_client(request):
    # Récupérer et supprimer la clé 'show_signup_modal' de la session
    show_signup_modal = request.session.pop('show_signup_modal', None)
    context = {
        'is_client': True,
        'is_coach': False,
        'show_signup_modal': show_signup_modal,  # Passe ça au template,
        }
    return render(request, 'accounts/dashboard_client.html', context)

@login_required
def dashboard_coach(request):
    # Récupérer et supprimer la clé 'show_signup_modal' de la session
    show_signup_modal = request.session.pop('show_signup_modal', None)
    context = {
        'is_client': False,
        'is_coach': True,
    }
    return render(request, 'accounts/dashboard_coach.html', context)
    # rendez_vous = RendezVous.objects.filter(coach=request.user)
    # return render(request, 'dashboard_coach.html', {'rendez_vous': rendez_vous})