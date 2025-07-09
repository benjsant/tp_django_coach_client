from django.contrib import admin

# Register your models here.

from .models import Seance,RdvHistorique

admin.site.register(Seance)
admin.site.register(RdvHistorique)