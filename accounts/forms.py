from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
"""
Ce module contient des formulaires personnalisés pour la gestion de l'authentification des utilisateurs dans une application Django.

Classes :
- CustomLoginForm : Formulaire personnalisé pour la connexion des utilisateurs.
- CustomSignupForm : Formulaire personnalisé pour l'inscription des nouveaux utilisateurs.

"""
class CustomLoginForm(AuthenticationForm):
    """
    Formulaire personnalisé pour la connexion des utilisateurs.

    Attributs :
    - username : Champ de texte pour le nom d'utilisateur.
    - password : Champ de texte pour le mot de passe.

    Méthodes :
    - __init__() : Initialise le formulaire avec des attributs personnalisés pour les champs.
    """
    username = forms.CharField(
        label = "Utilisateur",
        widget=forms.TextInput(
            attrs={
                "class":"form-control",
                "placeholder":"Utilisateur"
            })  
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "placeholder":"Mot de passe"
        })
    )

class CustomSignupForm(UserCreationForm):
    """
    Formulaire personnalisé pour l'inscription des nouveaux utilisateurs.

    Attributs :
    - email : Champ de texte pour l'adresse e-mail, requis lors de l'inscription.

    Méthodes :
    - __init__() : Initialise le formulaire et applique des classes CSS aux champs.
    
    Meta :
    - model : Modèle associé (User).
    - fields : Liste des champs à inclure dans le formulaire (username, email, password1, password2).
    """
    email = forms.EmailField(required=True,widget=forms.EmailInput(
        attrs={"class":"form-control"}
    ))

    class Meta: 
        model = User
        fields = ['username','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"