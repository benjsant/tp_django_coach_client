from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 

# Create your views here.

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)   # ⚠️ utilisez le form pour la validation
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                #  ⬇️  redirection vers l’URL nommée "accueil" de l’app core
                return redirect("index")   
            else:
                messages.error(request, "Identifiant ou mot de passe incorrect.")
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})

def logout_user(request):
    logout(request)
    return redirect("core:accueil")

def signup_user(request):
    pass

def dashboard_user(request):
    pass