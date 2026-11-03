from django.urls import path
from . import views
 
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("reservar/<int:cancha_id>/<int:hora>/", views.reservar, name="reservar"),
    path("reserva/<int:pk>/", views.confirmacion, name="confirmacion"),    
    path("reservas/", views.reservas, name="reservas"),
]
