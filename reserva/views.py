from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Reserva
from datetime import date

def agenda_reservas(request):
    """
    Vista principal: Muestra las reservas de la cancha.
    Por defecto filtra las reservas para la fecha de hoy, permitiendo ver qué 
    horarios ya están ocupados.
    """
    # Obtiene la fecha del filtro (si no viene ninguna, usa la fecha de hoy)
    fecha_filtro_str = request.GET.get("fecha")
    
    if fecha_filtro_str:
        try:
            fecha_busqueda = date.fromisoformat(fecha_filtro_str)
        except ValueError:
            fecha_busqueda = date.today()
    else:
        fecha_busqueda = date.today()

    # Obtiene todas las reservas de esa fecha específica ordenadas por hora
    lista_reservas = Reserva.objects.filter(fecha=fecha_busqueda).order_by("hora_inicio")
    
    contexto = {
        "reservas": lista_reservas,
        "fecha_actual": fecha_busqueda,
        "hoy_string": fecha_busqueda.isoformat()
    }
    return render(request, "reserva/ordenes.html", contexto)


def seguimiento_buscar(request):
    """
    Página intermedia para que el usuario escriba el código de su ticket.
    Redirige automáticamente limpiando espacios y convirtiendo a mayúsculas.
    """
    codigo = request.GET.get("codigo", "").strip().upper()
    if codigo:
        return redirect("seguimiento", codigo=codigo)
    return render(request, "reserva/seguimiento_buscar.html")


def seguimiento(request, codigo):
    """
    Muestra la ficha de una reserva específica usando su código de seguimiento público.
    No requiere inicio de sesión. Si el código no existe, devuelve un error 404 controlado.
    """
    reserva = Reserva.objects.filter(codigo_seguimiento=codigo.upper()).first()
    contexto = {
        "reserva": reserva, 
        "codigo": codigo.upper()
    }
    estado = 200 if reserva else 404
    return render(request, "reserva/seguimiento.html", contexto, status=estado)


