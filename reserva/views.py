from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
 
from .models import Cancha, Reserva
 
 
def texto_turno(hora):
    return f"{hora:02d}:00 – {hora + 1:02d}:00"
 
 
def inicio(request):
    tablero = []
    for cancha in Cancha.objects.all():
        reservas = {r.hora: r for r in cancha.reservas.all()}
        turnos = []
        for hora in cancha.horas():
            turnos.append({"hora": hora, "texto": texto_turno(hora),
                           "reserva": reservas.get(hora)})
        tablero.append({"cancha": cancha, "turnos": turnos})
    return render(request, "reserva/inicio.html", {"tablero": tablero})
 
 
def reservar(request, cancha_id, hora):
    cancha = get_object_or_404(Cancha, pk=cancha_id)
    if hora not in cancha.horas():
        return render(request, "reserva/reservar.html",
                      {"cancha": cancha, "mensaje": "Ese horario no existe."},
                      status=404)
    contexto = {"cancha": cancha, "hora": hora, "texto": texto_turno(hora)}
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        if not nombre:
            contexto["mensaje"] = "Escribe tu nombre para reservar."
        else:
            try:
                reserva = Reserva.objects.create(
                    cancha=cancha, hora=hora, nombre=nombre)
            except IntegrityError:
                contexto["mensaje"] = "Ese horario ya fue reservado por otra persona."
                contexto["ocupado"] = True
            else:
                return redirect("confirmacion", pk=reserva.pk)
    elif Reserva.objects.filter(cancha=cancha, hora=hora).exists():
        contexto["mensaje"] = "Ese horario ya está reservado."
        contexto["ocupado"] = True
    return render(request, "reserva/reservar.html", contexto)
 
 
def confirmacion(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    contexto = {"reserva": reserva, "texto": texto_turno(reserva.hora)}
    return render(request, "reserva/confirmacion.html", contexto)

def reservas(request):
    lista = Reserva.objects.order_by("cancha__nombre", "hora")
    return render(request, "reserva/reservas.html", {"reservas": lista})
