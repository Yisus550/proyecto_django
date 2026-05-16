from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from user.forms import UsuarioCreationForm


def login_view(request):
    """Handle user authentication."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
        return render(
            request,
            "registration/login.html",
            {"form": form, "error": "Credenciales inválidas"},
        )
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def register_view(request):
    """Handle new user registration."""
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
    """Handle user logout."""
    logout(request)
    return redirect("index")
