from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Lugar, Visita


# Create your views here.
def index(request):
    return render(request, "index.html")


def lista_lugares(request):
    lugares = Lugar.objects.all()

    return render(request, "lista.html", {"lugares": lugares})


def detalle_lugar(request, lugar_id):
    lugar = Lugar.objects.get(id=lugar_id)

    return render(request, "detalles.html", {"lugar": lugar})


@login_required
def agregar_lugar(request):
    lugares = Lugar.objects.all()

    if request.method == "POST":
        lugar = Lugar.objects.get(id=request.POST.get("lugar_id"))
        fecha = request.POST.get("fecha")
        resena = request.POST.get("resena")
        calificacion = request.POST.get("calificacion")
        platillo = request.POST.get("platillo")

        visita = Visita(
            usuario=request.user,
            lugar=lugar,
            fecha=fecha,
            resena=resena,
            calificacion=calificacion,
            platillo=platillo,
        )

        visita.save()
        return redirect("lugar_lista")

    return render(request, "agregar_visita.html", {"lugares": lugares})


@login_required
def visita_lugar(request, lugar_id):
    lugar = Lugar.objects.get(id=lugar_id)
    lugares = Lugar.objects.all()

    if request.method == "POST":
        fecha = request.POST.get("fecha")
        resena = request.POST.get("resena")
        calificacion = request.POST.get("calificacion")
        platillo = request.POST.get("platillo")

        visita = Visita(
            usuario=request.user,
            lugar=lugar,
            fecha=fecha,
            resena=resena,
            calificacion=calificacion,
            platillo=platillo,
        )

        visita.save()
        return redirect("lugar_lista")

    return render(request, "agregar_visita.html", {"lugar": lugar, "lugares": lugares})


def visitas_usuario(request):
    visitas = Visita.objects.filter(usuario=request.user)

    return render(request, "visitas.html", {"visitas": visitas})


def editar_visita(request, visita_id):
    visita = Visita.objects.get(id=visita_id)

    if request.method == "POST":
        visita.fecha = request.POST.get("fecha")
        visita.resena = request.POST.get("resena")
        visita.calificacion = request.POST.get("calificacion")
        visita.platillo = request.POST.get("platillo")

        visita.save()
        return redirect("visitas")

    return render(request, "editar_visita.html", {"visita": visita})


def eliminar_visita(request, visita_id):
    visita = Visita.objects.get(id=visita_id)

    if request.method == "POST":
        visita.delete()
        return redirect("visitas")

    return render(request, "eliminar_visita.html", {"visita": visita})
