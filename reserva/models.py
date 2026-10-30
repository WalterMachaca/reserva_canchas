import uuid
import random
from datetime import date
from django.db import models

# =========================================================================
# FUNCIÓN AUXILIAR PARA EL CÓDIGO DE SEGUIMIENTO PÚBLICO
# =========================================================================
ALFABETO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def generar_codigo_ticket():
    """Genera un código único de 6 caracteres evitando confusiones visuales"""
    while True:
        codigo = "".join(random.choices(ALFABETO, k=6))
        # Verifica que el código no exista en ninguna reserva activa
        if not Reserva.objects.filter(codigo_seguimiento=codigo).exists():
            return codigo


# =========================================================================
# 1. CLASE USUARIO (Para Autenticación y Registro de Clientes)
# =========================================================================
class Usuario(models.Model):
    ROLES = [
        ("cliente", "Cliente Externo"),
        ("administrador", "Administrador de Cancha"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    nombre_completo = models.CharField(max_length=100, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20, unique=True, verbose_name="Teléfono (Usuario)")
    password_hash = models.CharField(max_length=128, verbose_name="Contraseña Encriptada")
    rol = models.CharField(max_length=20, choices=ROLES, default="cliente")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.nombre_completo} ({self.rol})"


# =========================================================================
# 2. CLASE RESERVA (El Núcleo del Negocio e Integración Híbrida)
# =========================================================================
class Reserva(models.Model):
    ESTADOS_PAGO = [
        ("Pendiente", "Pendiente"),
        ("Pagado", "Pagado"),
    ]
    ORIGEN_OPCIONES = [
        ("Web", "Web"),
        ("Escritorio", "Escritorio"),
    ]
    ESTADOS_SINC = [
        ("Sincronizado", "Sincronizado"),
        ("Pendiente_Subida", "Pendiente de Subida"),
    ]

    # Clave primaria universal para evitar que choquen los IDs de la app local y la web
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    
    # Relación Uno a Muchos: Un usuario puede tener muchas reservas
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reservas")
    
    # Datos específicos del turno (Fecha y Bloque de Horario)
    fecha = models.DateField(default=date.today)
    hora_inicio = models.CharField(max_length=5, verbose_name="Hora Inicio (HH:MM)") # Ej: "19:00"
    hora_fin = models.CharField(max_length=5, verbose_name="Hora Fin (HH:MM)")       # Ej: "20:00"
    
    # Contabilidad y Origen
    monto_total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default="Pendiente")
    origen = models.CharField(max_length=20, choices=ORIGEN_OPCIONES, default="Web")
    
    # Control para el algoritmo del módulo de sincronización
    estado_sincronizacion = models.CharField(max_length=20, choices=ESTADOS_SINC, default="Sincronizado")
    
    # Código público equivalente al del taller mecánico para consultar estados sin loguearse
    codigo_seguimiento = models.CharField(max_length=8, editable=False, unique=True, verbose_name="Código Ticket")

    # Auditoría de tiempos para resolver el conflicto: "El último en modificar gana"
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["fecha", "hora_inicio"]

    def save(self, *args, **kwargs):
        # Genera el ticket automático de 6 letras/números solo si es nuevo
        if not self.codigo_seguimiento:
            self.codigo_seguimiento = generar_codigo_ticket()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} [{self.hora_inicio}-{self.hora_fin}] — {self.usuario.nombre_completo}"



