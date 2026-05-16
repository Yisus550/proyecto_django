"""
URL configuration for viajes_gastronomia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from lugar import views as lugar_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("user.urls")),
    path("", lugar_views.index, name="index"),
    # Rutas para lugares
    path("lugares/lista", lugar_views.lista_lugares, name="lugar_lista"),
    path(
        "lugares/detalles/<int:lugar_id>",
        lugar_views.detalle_lugar,
        name="lugar_detalles",
    ),
    path(
        "lugares/visita/",
        lugar_views.agregar_lugar,
        name="agregar_visita",
    ),
    path(
        "lugares/visita/<int:lugar_id>",
        lugar_views.visita_lugar,
        name="lugar_visita",
    ),
    # Ruta para visitas del usuario
    path("usuario/visitas", lugar_views.visitas_usuario, name="visitas"),
    path(
        "usuario/visitas/editar/<int:visita_id>",
        lugar_views.editar_visita,
        name="editar_visita",
    ),
    path(
        "usuario/visitas/eliminar/<int:visita_id>",
        lugar_views.eliminar_visita,
        name="eliminar_visita",
    ),
]
