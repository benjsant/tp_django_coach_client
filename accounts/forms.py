from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
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