from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from user.forms import UsuarioCreationForm


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        return render(
            request,
            "registration/login.html",
            {"error": "Credenciales inválidas"},
        )
    return render(request, "registration/login.html")


def register_view(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UsuarioCreationForm()
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")
