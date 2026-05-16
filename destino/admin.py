from django.contrib import admin

from .models import Ciudad, Destino, Estado

# Register your models here.
admin.site.register(Estado)
admin.site.register(Ciudad)
admin.site.register(Destino)
