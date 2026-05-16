# Autenticación en Django — Estructura y Lógica

## 1. Introducción

Django incluye un sistema de autenticación completo (`django.contrib.auth`) que maneja usuarios, sesiones, permisos y grupos. En este proyecto se personalizó para usar un modelo de usuario propio (`Usuario`) con autenticación por username + password, registro de nuevos usuarios y protección de vistas.

### Componentes del sistema

| Componente | Archivo | Propósito |
|------------|---------|-----------|
| Modelo | `user/models.py` | `Usuario(AbstractUser)` — modelo de usuario personalizado |
| Formulario | `user/forms.py` | `UsuarioCreationForm` — validación y creación de usuarios |
| Vistas | `user/views.py` | `login_view`, `register_view`, `logout_view` |
| URLs | `user/urls.py` | Ruteo de los 3 endpoints |
| Templates | `user/templates/` | `base.html`, `registration/login.html`, `registration/register.html` |
| Settings | `viajes_gastronomia/settings.py` | `AUTH_USER_MODEL`, `LOGIN_URL`, `LOGIN_REDIRECT_URL` |

---

## 2. Modelo de Usuario Personalizado

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)

    lugares_visitados = models.ManyToManyField(
        "lugar.Lugar",
        through="lugar.Visita",
        related_name="usuarios_visitantes",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
```

### `AbstractUser` vs `AbstractBaseUser`

Django ofrece dos formas de personalizar el modelo de usuario:

| Aspecto | `AbstractUser` | `AbstractBaseUser` |
|---------|---------------|-------------------|
| ¿Qué incluye? | Todo el modelo `User` default (username, first_name, last_name, email, password, groups, permissions, etc.) | Solo `password`, `last_login`, `is_active` |
| ¿Cuándo usarlo? | Cuando el modelo default es casi suficiente y solo necesitas añadir campos | Cuando necesitas cambiar el campo de identificación (ej. email en vez de username) |
| Esfuerzo | Bajo — solo agregas campos nuevos | Alto — debes redefinir `USERNAME_FIELD`, manager, forms, etc. |

Se eligió `AbstractUser` porque el campo `username` como identificador funciona para este proyecto y solo se necesitaba añadir `email` como único y la relación M2M.

### Configuración en settings

```python
AUTH_USER_MODEL = "user.Usuario"
```

Esta línea **debe** estar antes de la primera migración. Cambiar `AUTH_USER_MODEL` después de ejecutar migraciones es complejo y propenso a errores.

### ManyToManyField con through

```python
lugares_visitados = models.ManyToManyField(
    "lugar.Lugar",
    through="lugar.Visita",
    related_name="usuarios_visitantes",
)
```

Usar `through="lugar.Visita"` permite:
- Acceder a lugares visitados por un usuario: `usuario.lugares_visitados.all()`
- Acceder a usuarios que visitaron un lugar: `lugar.usuarios_visitantes.all()`
- La tabla intermedia `Visita` contiene datos adicionales (`fecha`, `resena`, `calificacion`, `platillo`)

Sin `through`, Django crearía una tabla intermedia automática con solo las dos FK. Con `through`, se usa la tabla `Visita` existente que ya tenía esos campos extra.

---

## 3. Formulario de Registro

```python
from django.contrib.auth.forms import UserCreationForm
from user.models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = True
```

### Herencia de Meta

`class Meta(UserCreationForm.Meta)` hereda la configuración del `Meta` de `UserCreationForm`. Esto incluye:
- `model = User` → se sobreescribe con `Usuario`
- `fields = ("username",)` → se expande a `("username", "email", "first_name", "last_name")`
- Widgets y validaciones por defecto

Sobreescribir `Meta` completamente en vez de heredar es válido pero más verboso y propenso a omitir configuraciones internas de Django.

### ¿Qué hace `UserCreationForm` automáticamente?

1. Valida que `password1 == password2`
2. Aplica los validadores de `AUTH_PASSWORD_VALIDATORS` del settings
3. Hashea el password antes de guardar (via `save()`)
4. Setea `is_active = True` por defecto

### ¿Por qué forzar `required = True`?

`UserCreationForm` de Django no marca `email`, `first_name` ni `last_name` como requeridos por defecto (en el modelo `User` original, estos campos permiten `blank=True`). Forzarlos a `required = True` asegura que el usuario complete todos los campos en el registro.

---

## 4. Vistas de Autenticación

### `login_view`

```python
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        return render(request, "registration/login.html",
                      {"error": "Credenciales inválidas"})
    return render(request, "registration/login.html")
```

**Flujo:**

```
POST /login/
  → authenticate(username, password)
    → Si credenciales válidas: devuelve objeto Usuario
    → Si inválidas: devuelve None
  → login(request, user) crea sesión en servidor + cookie sessionid
  → redirect("index")

GET /login/
  → render login.html (sin error)
```

### `authenticate` + `login`: ¿por qué dos pasos?

| Función | Qué hace |
|---------|----------|
| `authenticate()` | Verifica username+password contra la DB. Devuelve el usuario o `None`. No modifica el estado |
| `login()` | Crea la sesión en el servidor, envía la cookie `sessionid` al cliente, vincula `request.user` |

Son separadas porque querrías poder verificar credenciales sin iniciar sesión (ej. API que devuelve token en vez de cookie). En este caso, se usan juntas.

### `register_view`

```python
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
```

**Flujo:**

```
POST /register/
  → UsuarioCreationForm(request.POST)
  → form.is_valid() aplica validaciones de password, campos requeridos, unicidad de username/email
  → form.save() llama a create_user() internamente → hashea password, guarda en DB
  → login(request, user) auto-loguea al usuario recién creado
  → redirect("index")
```

El auto-logueo post-registro es una decisión de UX: el usuario se registra y queda autenticado inmediatamente, sin necesidad de login separado. Alternativa: redirigir a login con mensaje "Registro exitoso, inicia sesión".

### `logout_view`

```python
def logout_view(request):
    logout(request)
    return redirect("index")
```

`logout()`:
- Vacía la sesión del servidor
- Elimina la cookie `sessionid`
- No lanza error si el usuario no estaba autenticado

---

## 5. Ruteo y Namespacing

### `user/urls.py`

```python
from django.urls import path
from user import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
```

### `viajes_gastronomia/urls.py` (root)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("user.urls")),     # Auth routes: /login/, /register/, /logout/
    path("", lugar_views.index, name="index"),
    ...
]
```

**Importante: el orden de los patrones importa.** Django prueba cada patrón en orden. `path("", include("user.urls"))` no matchea la raíz porque los subpatrones son `login/`, `register/`, `logout/` — ninguno es string vacío. El patrón `path("", lugar_views.index, name="index")` matchea la raíz después.

### Nombres de URL para templates

```html
<a href="{% url 'login' %}">Iniciar sesión</a>
<a href="{% url 'register' %}">Registrarse</a>
<a href="{% url 'logout' %}">Cerrar sesión</a>
```

Django resuelve `{% url 'login' %}` a `/login/` usando el `name=` definido en `user/urls.py`. Esto permite cambiar la URL sin modificar templates.

---

## 6. Templates y Contexto de Autenticación

### `base.html` — Navegación condicional

```html
<nav>
  <a href="{% url 'index' %}">Inicio</a>
  <a href="{% url 'lugar_lista' %}">Lugares</a>
  {% if user.is_authenticated %}
    <span>Hola, {{ user.first_name|default:user.username }}</span>
    <a href="{% url 'logout' %}">Cerrar sesión</a>
  {% else %}
    <a href="{% url 'login' %}">Iniciar sesión</a>
    <a href="{% url 'register' %}">Registrarse</a>
  {% endif %}
</nav>
```

### ¿De dónde viene `user` en el template?

El contexto processor `django.contrib.auth.context_processors.auth` (en `TEMPLATES.OPTIONS.context_processors`) agrega automáticamente `user` (el usuario de `request.user`) a todos los contextos de template. Sin esto, cada vista tendría que pasar `{"user": request.user}` explícitamente.

### ¿Qué es `user.is_authenticated`?

Es un `property` de `AbstractUser` que siempre devuelve `True` para usuarios autenticados y `False` para `AnonymousUser` (cuando no hay sesión). No es un campo de base de datos.

### `login.html` — Formulario manual

Se usan inputs HTML directos (no `form.as_p`) porque el login no requiere un form de Django — solo username + password. El manejo de errores se hace con una variable `error` pasada desde la vista:

```html
{% if error %}
  <p style="color:red">{{ error }}</p>
{% endif %}
```

### `register.html` — Formulario con `form.as_p`

```html
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Registrarse</button>
</form>
```

`form.as_p` renderiza cada campo del formulario envuelto en `<p>`, incluyendo:
- Labels
- Inputs
- Help text
- Errores de validación por campo

Esto es posible porque `UsuarioCreationForm` es un `ModelForm` de Django — sabe exactamente qué campos mostrar y cómo validarlos.

### CSRF

`{% csrf_token %}` es obligatorio en todo `<form method="post">`. Django genera un token único por sesión y lo verifica en cada POST. Sin esto, Django devuelve error 403 Forbidden.

---

## 7. Protección de Vistas con `@login_required`

```python
from django.contrib.auth.decorators import login_required

@login_required
def visita_lugar(request, lugar_id):
    ...
```

### Mecanismo

1. Usuario no autenticado intenta acceder a `/lugares/visita/5`
2. `@login_required` intercepta, detecta `request.user.is_authenticated == False`
3. Redirige a `LOGIN_URL + "?next=" + url_actual`
4. Resultado: `/login/?next=/lugares/visita/5`
5. Usuario se autentica → Django redirige a `?next=` → vuelve a la página original

### ¿Qué pasa si `LOGIN_URL` no está configurado?

Django asume `/accounts/login/` por defecto. Como nuestras URLs usan `/login/`, se configuró explícitamente:

```python
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"    # Dónde redirigir tras login exitoso sin ?next=
LOGOUT_REDIRECT_URL = "/"   # Dónde redirigir tras logout
```

### `request.user` en vistas protegidas

```python
visita = Visita(
    usuario=request.user,    # Siempre es un Usuario autenticado aquí
    ...
)
```

Dentro de una vista con `@login_required`, `request.user` nunca es `AnonymousUser`. Es seguro usarlo directamente sin verificar `is_authenticated`. Fuera de vistas protegidas, siempre verificar o usar `request.user.is_authenticated`.

---

## 8. Configuración del Proyecto

```python
# viajes_gastronomia/settings.py

INSTALLED_APPS = [
    ...
    "django.contrib.auth",
    "django.contrib.contenttypes",  # Requerido por auth
    ...
]

MIDDLEWARE = [
    ...
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    ...
]

TEMPLATES = [{
    "OPTIONS": {
        "context_processors": [
            ...
            "django.contrib.auth.context_processors.auth",
            ...
        ],
    },
}]

AUTH_USER_MODEL = "user.Usuario"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
```

### ¿Qué apps y middleware son necesarios?

| Componente | Requerido para |
|------------|---------------|
| `django.contrib.auth` | Modelos de usuario, permisos, grupos |
| `django.contrib.contenttypes` | Permisos genéricos (dependencia de auth) |
| `django.contrib.sessions` | Sesiones de usuario |
| `SessionMiddleware` | Manejar cookies de sesión |
| `AuthenticationMiddleware` | Vincular `request.user` al usuario de la sesión |
| `auth` context processor | Disponibilizar `user` en todos los templates |

Todos vienen activados por defecto en `django-admin startproject`.

---

## 9. Flujo Completo Request/Response

### Escenario: Usuario no autenticado intenta agregar una visita

```
1. GET /lugares/visita/5
2. Django resuelve la URL → lugar.visita_lugar (via root urls.py)
3. @login_required detecta request.user == AnonymousUser
4. Django redirige a /login/?next=/lugares/visita/5 (HTTP 302)
5. Navegador sigue la redirección → GET /login/?next=/lugares/visita/5
6. login_view: request.method == "GET" → render login.html
7. Usuario completa formulario y hace POST /login/?next=/lugares/visita/5
8. login_view: authenticate() → login() → redirect a ?next=
9. Navegador redirige a /lugares/visita/5
10. @login_required: ahora request.user está autenticado → pasa
11. visita_lugar: request.user es el Usuario → render agregar_visita.html
```

### ¿Por qué `?next=`?

El parámetro `?next=` lo agrega automáticamente `@login_required` si el decorador estándar de Django se usa. El `login` genérico de Django (`django.contrib.auth.views.LoginView`) también lo maneja. En nuestra vista manual `login_view`, el `?next=` está presente en la URL pero no se usa explícitamente — `redirect("index")` ignora el parámetro. Para soportar `next` completamente:

```python
from django.shortcuts import resolve_url

def login_view(request):
    next_url = request.GET.get("next") or "index"
    if request.method == "POST":
        ...
        if user is not None:
            login(request, user)
            return redirect(next_url)
```

Esto es una mejora potencial — la implementación actual siempre redirige al index.

---

## 10. Buenas Prácticas (Resumen)

1. **Configura `AUTH_USER_MODEL` antes de la primera migración.** Cambiarlo después es traumático.

2. **Usa `AbstractUser` a menos que necesites cambiar el campo de identificación.** `AbstractBaseUser` es para casos donde username no existe (ej. login con email).

3. **`authenticate()` + `login()` son dos pasos deliberados.** No los combines. `authenticate` verifica, `login` crea sesión.

4. **Siempre usa `create_user()` (no `create()`) para usuarios.** El password debe ser hasheado.

5. **`@login_required` en vistas que usan `request.user`.** Garantiza que `request.user` es un usuario real, no `AnonymousUser`.

6. **`{% csrf_token %}` en todo formulario POST.** Django lo exige y es protección básica contra CSRF.

7. **Usa nombres de URL en templates, no rutas hardcodeadas.** `{% url 'login' %}` en vez de `"/login/"`.

8. **El contexto processor `auth` da `user` gratis en todos los templates.** No necesitas pasarlo explícitamente.

9. **El formulario manual vs `form.as_p` depende del control que necesites.** `form.as_p` para velocidad, manual para control fino de HTML.

10. **Documenta el flujo `?next=` si decides implementarlo.** No es obvio para estudiantes que la URL contiene el destino post-login.
