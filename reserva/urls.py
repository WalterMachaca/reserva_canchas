from django.urls import path
from . import views
 
urlpatterns = [
    path("", views.agenda_reservas, name="ordenes"), 
    path("seguimiento/", views.seguimiento_buscar, name="seguimiento_buscar"),
    path("seguimiento/<str:codigo>/", views.seguimiento, name="seguimiento"),
]
