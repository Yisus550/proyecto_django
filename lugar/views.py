from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import PermissionDenied

from .forms import VisitaForm
from .models import Lugar, Visita


def index(request):
    """Render the landing page."""
    return render(request, "index.html")


def lista_lugares(request):
    """Display a list of all places, optimized with select_related."""
    lugares = Lugar.objects.select_related("destino", "categoria", "destino__ciudad", "destino__estado").all()
    return render(request, "lista.html", {"lugares": lugares})


def detalle_lugar(request, lugar_id):
    """Display details for a specific place."""
    lugar = get_object_or_404(Lugar.objects.select_related("destino", "categoria"), id=lugar_id)
    return render(request, "detalles.html", {"lugar": lugar})


@login_required
def agregar_lugar(request):
    """Handle adding a new visit to any place."""
    if request.method == "POST":
        form = VisitaForm(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.usuario = request.user
            visita.save()
            return redirect("lugar_lista")
    else:
        form = VisitaForm()

    lugares = Lugar.objects.all()
    return render(request, "agregar_visita.html", {"form": form, "lugares": lugares})


@login_required
def visita_lugar(request, lugar_id):
    """Handle adding a visit to a specific place."""
    lugar = get_object_or_404(Lugar, id=lugar_id)
    if request.method == "POST":
        form = VisitaForm(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.usuario = request.user
            visita.lugar = lugar
            visita.save()
            return redirect("lugar_lista")
    else:
        form = VisitaForm(initial={"lugar": lugar})

    lugares = Lugar.objects.all()
    return render(request, "agregar_visita.html", {"form": form, "lugar": lugar, "lugares": lugares})


@login_required
def visitas_usuario(request):
    """Display visits belonging to the logged-in user."""
    visitas = Visita.objects.filter(usuario=request.user).select_related("lugar", "lugar__destino")
    return render(request, "visitas.html", {"visitas": visitas})


@login_required
def editar_visita(request, visita_id):
    """Edit an existing visit, with ownership check."""
    visita = get_object_or_404(Visita, id=visita_id)
    
    if visita.usuario != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = VisitaForm(request.POST, instance=visita)
        if form.is_valid():
            form.save()
            return redirect("visitas")
    else:
        form = VisitaForm(instance=visita)

    return render(request, "editar_visita.html", {"form": form, "visita": visita})


@login_required
def eliminar_visita(request, visita_id):
    """Delete an existing visit, with ownership check."""
    visita = get_object_or_404(Visita, id=visita_id)

    if visita.usuario != request.user:
        raise PermissionDenied

    if request.method == "POST":
        visita.delete()
        return redirect("visitas")

    return render(request, "eliminar_visita.html", {"visita": visita})
