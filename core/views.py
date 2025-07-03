from django.shortcuts import render

# Create your views here.
# exemple dans myapp/views.py
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Bienvenue sur le site de coaching !</h1>")