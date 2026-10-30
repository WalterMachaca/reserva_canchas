from django.contrib import admin
from .models import Usuario, Reserva
 
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "telefono", "rol")
    list_filter = ("rol",)
    
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    # Columnas que se verán en la lista general de reservas
    list_display = ("codigo_seguimiento", "usuario", "fecha", "hora_inicio", "hora_fin","monto_total", "estado_pago", "origen")
    # Filtros laterales para buscar rápidamente en el panel    
    list_filter = ("fecha", "estado_pago", "origen","estado_sincronizacion")
    # Buscador por nombre de cliente o código de ticket
    search_fields = ("usuario__nombre_completo", "codigo_seguimiento")
    # Hace que el código de seguimiento sea de solo lectura para que no lo alteren a mano
    readonly_fields = ("codigo_seguimiento",) 
 

