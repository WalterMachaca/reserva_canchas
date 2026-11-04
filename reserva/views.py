from django.db import IntegrityError, transaction
from django.db.models import Max, Min
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Cancha, Reserva


def texto_rango(inicio, fin):
    return f"{inicio:02d}:00 – {fin:02d}:00"


def texto_turno(hora):
    return texto_rango(hora, hora + 1)


def horas_seguidas_libres(cancha, hora):
    """Cuántas horas seguidas se pueden reservar desde `hora`.

    Se detiene en la primera hora ocupada, en el cierre de la cancha
    o al llegar al máximo de horas permitido para esa cancha.
    """
    ocupadas = set(cancha.reservas.values_list("hora", flat=True))
    limite = min(cancha.max_horas, cancha.hora_cierre - hora)
    cantidad = 0
    while cantidad < limite and (hora + cantidad) not in ocupadas:
        cantidad += 1
    return cantidad


def inicio(request):
    """Lista de canchas. Los horarios se ven al elegir una."""
    canchas = []
    for cancha in Cancha.objects.all():
        total = len(cancha.horas())
        ocupadas = cancha.reservas.count()
        canchas.append({"cancha": cancha, "libres": max(total - ocupadas, 0)})
    return render(request, "reserva/inicio.html", {"canchas": canchas})


def cancha_detalle(request, cancha_id):
    """Horarios de una sola cancha."""
    cancha = get_object_or_404(Cancha, pk=cancha_id)
    reservas = {r.hora: r for r in cancha.reservas.all()}
    turnos = []
    for hora in cancha.horas():
        turnos.append({"hora": hora, "texto": texto_turno(hora),
                       "reserva": reservas.get(hora)})
    return render(request, "reserva/cancha.html",
                  {"cancha": cancha, "turnos": turnos})


def reservar(request, cancha_id, hora):
    cancha = get_object_or_404(Cancha, pk=cancha_id)
    if hora not in cancha.horas():
        return render(request, "reserva/reservar.html",
                      {"cancha": cancha, "mensaje": "Ese horario no existe."},
                      status=404)

    maximo = horas_seguidas_libres(cancha, hora)
    contexto = {"cancha": cancha, "hora": hora}

    if maximo == 0:
        contexto["mensaje"] = "Ese horario ya está reservado."
        contexto["ocupado"] = True
        return render(request, "reserva/reservar.html", contexto)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        try:
            duracion = int(request.POST.get("duracion", 1))
        except ValueError:
            duracion = 0

        if not nombre:
            contexto["mensaje"] = "Escribe tu nombre para reservar."
        elif not 1 <= duracion <= maximo:
            contexto["mensaje"] = "La cantidad de horas elegida no está disponible."
        else:
            ahora = timezone.now()  # mismo valor para todas las horas de esta reserva
            try:
                with transaction.atomic():
                    for h in range(hora, hora + duracion):
                        reserva = Reserva.objects.create(
                            cancha=cancha, hora=h, nombre=nombre, creada=ahora)
                        if h == hora:
                            primera = reserva
            except IntegrityError:
                contexto["mensaje"] = "Ese horario ya fue reservado por otra persona."
                contexto["ocupado"] = True
                maximo = 0
            else:
                return redirect("confirmacion", pk=primera.pk)

    if maximo:
        contexto["opciones"] = [
            {"duracion": n,
             "texto": f"{n} hora{'s' if n > 1 else ''} ({texto_rango(hora, hora + n)})"}
            for n in range(1, maximo + 1)
        ]
        contexto["texto"] = texto_turno(hora)
    return render(request, "reserva/reservar.html", contexto)


def confirmacion(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    # Todas las horas creadas en la misma reserva comparten cancha, nombre y fecha de creación.
    rango = Reserva.objects.filter(
        cancha=reserva.cancha, nombre=reserva.nombre, creada=reserva.creada
    ).aggregate(inicio=Min("hora"), ultima=Max("hora"))
    inicio_h, fin_h = rango["inicio"], rango["ultima"] + 1
    contexto = {"reserva": reserva,
                "texto": texto_rango(inicio_h, fin_h),
                "horas": fin_h - inicio_h}
    return render(request, "reserva/confirmacion.html", contexto)


def reservas(request):
    # Una fila por reserva: se unen las horas que se reservaron juntas.
    grupos = {}
    lista = Reserva.objects.select_related("cancha").order_by("cancha__nombre", "hora")
    for r in lista:
        clave = (r.cancha_id, r.nombre, r.creada)
        if clave in grupos:
            grupos[clave]["fin"] = r.hora + 1
        else:
            grupos[clave] = {"cancha": r.cancha, "nombre": r.nombre,
                             "inicio": r.hora, "fin": r.hora + 1}
    filas = []
    for g in grupos.values():
        g["texto"] = texto_rango(g["inicio"], g["fin"])
        g["horas"] = g["fin"] - g["inicio"]
        filas.append(g)
    return render(request, "reserva/reservas.html", {"reservas": filas})
