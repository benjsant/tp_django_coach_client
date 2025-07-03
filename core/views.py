# from django.shortcuts import render

# # Create your views here.
# # exemple dans myapp/views.py
# from django.db.models import F
# from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
# from django.views import generic

# class IndexView(generic.ListView):
#     template_name = "core/accueil.html"

from django.shortcuts import render

def index(request):
    return render(request, 'core/accueil.html')