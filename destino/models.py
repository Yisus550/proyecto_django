from django.db import models


class Estado(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}, {self.estado.nombre}"


class Destino(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre}, {self.ciudad.nombre}, {self.estado.nombre}"
