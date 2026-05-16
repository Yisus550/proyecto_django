from django.db import models


class Estado(models.Model):
    """Political state representation."""
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    """City representation within a state."""
    nombre = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name="ciudades")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"

    def __str__(self):
        return f"{self.nombre}, {self.estado.nombre}"


class Destino(models.Model):
    """Specific travel destination area."""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name="destinos")
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name="destinos")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"

    def __str__(self):
        return f"{self.nombre}, {self.ciudad.nombre}, {self.estado.nombre}"
