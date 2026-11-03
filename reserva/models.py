from django.db import models
from django.utils import timezone
 
 
class Cancha(models.Model):
    nombre = models.CharField(max_length=60)
    deporte = models.CharField(max_length=40)
    hora_apertura = models.IntegerField(default=8, verbose_name="Abre a las (hora)")
    hora_cierre = models.IntegerField(default=22, verbose_name="Cierra a las (hora)")
 
    def horas(self):
        return range(self.hora_apertura, self.hora_cierre)
 
    def __str__(self):
        return f"{self.nombre} ({self.deporte})"
 
 
class Reserva(models.Model):
    cancha = models.ForeignKey(
        Cancha, on_delete=models.CASCADE, related_name="reservas")
    hora = models.IntegerField()
    nombre = models.CharField(max_length=80)
    creada = models.DateTimeField(default=timezone.now)
 
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cancha", "hora"], name="una_reserva_por_horario"),
        ]
 
    def __str__(self):
        return f"{self.cancha.nombre} {self.hora}:00 — {self.nombre}"



