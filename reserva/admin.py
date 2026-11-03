from django.contrib import admin
from .models import Cancha, Reserva
 
 
@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "deporte", "hora_apertura", "hora_cierre")
 
 
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("cancha", "hora", "nombre", "creada")
    list_filter = ("cancha",)

 

