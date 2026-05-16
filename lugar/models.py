from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Lugar(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    destino = models.ForeignKey("destino.Destino", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({self.destino.ciudad.nombre}, {self.destino.estado.nombre})"


class Visita(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lugar = models.ForeignKey(Lugar, on_delete=models.CASCADE)
    fecha = models.DateField()
    resena = models.TextField(blank=True)
    calificacion = models.IntegerField()
    platillo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"({self.usuario.username}) Visita a {self.lugar.nombre} el {self.fecha}"
