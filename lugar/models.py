from django.conf import settings
from django.db import models


class Categoria(models.Model):
    """Category of place (e.g. Restaurant, Bar)."""
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Lugar(models.Model):
    """Specific point of interest venue."""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="lugares")
    destino = models.ForeignKey("destino.Destino", on_delete=models.CASCADE, related_name="lugares")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"

    def __str__(self):
        return f"{self.nombre} ({self.destino.ciudad.nombre}, {self.destino.estado.nombre})"


class Visita(models.Model):
    """Record of a user visiting a specific place."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visitas")
    lugar = models.ForeignKey(Lugar, on_delete=models.CASCADE, related_name="visitas")
    fecha = models.DateField()
    resena = models.TextField(blank=True)
    calificacion = models.IntegerField()
    platillo = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"

    def __str__(self):
        return f"({self.usuario.username}) Visita a {self.lugar.nombre} el {self.fecha}"
