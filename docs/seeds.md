# Seed de Datos en Django — Estructura y Lógica

## 1. Introducción

Los archivos **seed** son scripts que pueblan la base de datos con datos iniciales o de prueba. En Django se implementan como **management commands** — comandos ejecutables via `python manage.py <comando>`. Esta estrategia evita los problemas de scripts independientes: no necesitas configurar manualmente `DJANGO_SETTINGS_MODULE`, el ORM está disponible, y los comandos son descubribles (aparecen en `python manage.py help`).

Este proyecto tiene tres seeds que forman una cadena de dependencias:

```
seed_destino.py  (Estados → Ciudades → Destinos)
      ↓
seed_lugar.py    (Categorías → Lugares → Visitas)
      ↓
seed_usuario.py  (Usuarios) — independiente, puede ejecutarse en cualquier orden
```

---

## 2. Arquitectura de Management Commands

Django descubre automáticamente comandos en el directorio:

```
<app>/
  management/
    __init__.py
    commands/
      __init__.py
      seed_destino.py
      seed_lugar.py
      seed_usuario.py
```

Cada archivo debe contener una clase `Command` que hereda de `BaseCommand` e implementa `handle(self, *args, **options)`.

### ¿Por qué management commands y no scripts?

| Aspecto | Management command | Script suelto |
|---------|------------------|---------------|
| Carga de Django | Automática | Requiere `setup()` manual |
| ORM disponible | Sí | Sí (tras setup) |
| Argumentos CLI | `ArgumentParser` integrado | Manual |
| Output coloreado | `self.style.SUCCESS`, `self.style.ERROR` | No |
| Descubrimiento | `python manage.py help` | No |

### BaseCommand — API básica usada

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Descripción visible en manage.py help"

    def handle(self, *args, **options):
        self.stdout.write("mensaje")             # stdout con formato consistente
        self.stderr.write("error", self.style.ERROR)  # stderr coloreado
        self.style.SUCCESS("texto")              # output verde (éxito)
```

---

## 3. Patrón General: Clean → Create → Report

Los tres seeds siguen el mismo ciclo:

1. **Clean** — Borrar datos existentes para garantizar idempotencia
2. **Create** — Insertar datos nuevos con logging progresivo
3. **Report** — Resumen final con conteo de registros creados

### Idempotencia

`python manage.py seed_destino` puede ejecutarse N veces y el resultado es el mismo. Esto se logra borrando primero:

```python
Destino.objects.all().delete()
Ciudad.objects.all().delete()
Estado.objects.all().delete()
```

El orden del `delete()` importa: se borran las tablas con FK primero (hijas) antes que las referenciadas (padres), o se usa el mismo orden que la creación pero inverso. Alternativa: `Estado.objects.all().delete()` con `on_delete=models.CASCADE` limpia todo automáticamente, pero ser explícito evita sorpresas si cambia el modelo.

### Estructura de datos

Los datos se definen como **constantes a nivel de módulo** (no dentro de `handle()`) por dos razones:

- **Legibilidad**: separa datos de lógica
- **Rendimiento**: se cargan una vez, no en cada ejecución del comando

```python
ESTADOS = ["Aguascalientes", "Baja California", ...]              # lista plana
CIUDADES = {"Aguascalientes": ["Aguascalientes", "Jesús María"]}  # dict agrupado
DESTINOS = [("nombre", "descripción"), ...]                       # tuplas posicionales
USUARIOS = [("username", "email", "pass", ...), ...]              # tuplas con flags
```

---

## 4. Análisis por Seed

### 4.1 `seed_destino.py` — Datos jerárquicos con relaciones FK

**Modelos involucrados:** `Estado → Ciudad → Destino` (cadena de FK).

**Flujo:**

1. Crear `Estado` objects, guardar en `estado_objs = {}` keyeado por nombre
2. Iterar `CIUDADES` dict, crear `Ciudad` con FK al estado correspondiente
3. Crear `Destino` usando `zip(DESTINOS, ESTADOS)` para emparejar cada destino con su estado

**Claves técnicas:**

```python
# Lookup dictionary para evitar consultas repetidas a DB
estado_objs = {}
for nombre in ESTADOS:
    estado = Estado.objects.create(nombre=nombre)
    estado_objs[nombre] = estado

# Tupla como key compuesto para lookup bidimensional
ciudad_objs = {}
for estado_nombre, ciudades in CIUDADES.items():
    for ciudad_nombre in ciudades:
        ciudad = Ciudad.objects.create(nombre=ciudad_nombre, estado=estado)
        ciudad_objs[(estado_nombre, ciudad_nombre)] = ciudad

# zip para alinear dos listas paralelas sin índices explícitos
for (nombre, descripcion), estado_nombre in zip(DESTINOS, ESTADOS):
    primera_ciudad = CIUDADES[estado_nombre][0]
    Destino.objects.create(...)
```

`zip()` evita usar `range(len(...))` y deja clara la relación 1:1 entre ambas listas.

**Por qué no `random.choice` aquí:** Los destinos tienen una relación semántica con su estado (ej. "Feria de San Marcos" pertenece naturalmente a Aguascalientes). Asignar aleatoriamente rompería esa coherencia.

---

### 4.2 `seed_usuario.py` — Datos planos con password hasheado

**Modelos involucrados:** `Usuario(AbstractUser)`.

**Flujo:**

1. Borrar todos los usuarios
2. Iterar tuplas y llamar `Usuario.objects.create_user()` con cada una

**Clave técnica: `create_user` vs `create`**

```python
# MAL: la password se guarda en texto plano
Usuario.objects.create(username="admin", password="admin123")

# BIEN: Django hashea la password automáticamente
Usuario.objects.create_user(username="admin", password="admin123")
```

`create_user()` es un método del `UserManager` que:
- Hashea el password con el algoritmo configurado (`PBKDF2` por defecto)
- Setea `is_active=True` automáticamente
- Normaliza el email (minúsculas)

**Flags de usuario:**

```python
("admin",  "admin@example.com",  "admin123",  "Admin",  "Sistema",  True,  True)   # superuser + staff
("staff1", "staff1@example.com", "staff123",  "María",  "López",    True,  False)  # staff, no superuser
("jperez", "juan.perez@...",     "pass123",   "Juan",   "Pérez",    False, False)  # regular user
```

La tupla posicional con 7 elementos no es ideal para legibilidad. Alternativa seria usar diccionarios o `namedtuple`, pero la tupla es suficiente para un seed pequeño y mantiene el archivo compacto.

---

### 4.3 `seed_lugar.py` — El más complejo: dependencias externas, aleatoriedad controlada, lógica condicional

**Modelos involucrados:** `Categoria → Lugar → Visita` + FK a `Destino` y `Usuario` (de otras apps).

#### 4.3.1 Validación pre-clean

```python
destinos = list(Destino.objects.all())
if not destinos:
    self.stderr.write(
        self.style.ERROR("¡Error! No hay destinos. Ejecuta seed_db primero.")
    )
    return
```

Esto es **fail fast**: si la dependencia no está satisfecha, el comando termina inmediatamente **sin tocar la base de datos**. En versiones anteriores de este seed, la validación ocurría después del cleanup, lo que dejaba las categorías borradas sin poder completar la operación — estado inconsistente.

#### 4.3.2 Determinismo con `random.seed(42)`

```python
random.seed(42)  # Misma semilla → mismos datos en cada ejecución
```

Sin `seed()`, cada ejecución asignaría categorías y destinos distintos a cada lugar, y las visitas variarían. Con seed fijo, el comportamiento es reproducible — crucial para debugging y entornos de prueba.

#### 4.3.3 `platillo` condicional por categoría

```python
CATEGORIAS_COMIDA = {"Restaurante", "Cafetería", "Bar", "Panadería"}

es_comida = lugar.categoria.nombre in CATEGORIAS_COMIDA
platillo=f"Especialidad {i+1}" if es_comida else ""
```

Usar un `set` para `CATEGORIAS_COMIDA` da lookups O(1). String vacío en lugar de `None` evita manejar `NULL` en templates y formularios.

#### 4.3.4 Fallback de usuarios

```python
usuarios = list(Usuario.objects.all())
if not usuarios:
    u = Usuario.objects.create_user(...)
    usuarios = [u]
```

Si no hay usuarios (seed_usuario no se ha ejecutado), el seed crea un testuser para no fallar. Esto hace al seed más tolerante, aunque el usuario recomendado es ejecutar `seed_usuario` primero explícitamente.

#### 4.3.5 Variable para constantes numéricas

```python
VISITAS_COUNT = 20  # En vez de hardcodear range(20) en el medio del código
```

---

## 5. Decisiones de Diseño (Justificación Técnica)

### 5.1 ¿Por qué limpiar antes de crear?

- **Idempotencia**: `python manage.py seed_X` se puede ejecutar N veces
- **Simplicidad**: evita lógica de "update si existe, create si no" (`get_or_create`, `update_or_create`)
- **Trade-off**: se pierden datos existentes. No es adecuado para producción.

### 5.2 ¿Por qué validar dependencias al inicio?

- **Fail fast**: el comando falla antes de hacer cualquier cambio en DB
- **UX claro**: el mensaje de error dice exactamente qué falta y qué comando ejecutar

### 5.3 ¿Por qué `random.seed(42)` en seed_lugar y no en seed_destino?

`seed_destino` usa datos fijos con relaciones semánticas fijas. No hay aleatoriedad. `seed_lugar` asigna categorías y destinos aleatoriamente a los lugares — sin seed fijo, cada ejecución produce asignaciones distintas, lo que dificulta debugging y pruebas.

### 5.4 ¿Por qué `create_user` en lugar de `create`?

`AbstractUser` espera password hasheada. `create` guardaría el string "admin123" como password literal, no como hash. `create_user` se encarga del hasheo y otras normalizaciones. Intentar autenticarse con un usuario creado via `create` siempre fallaría.

### 5.5 ¿Por qué tuplas posicionales para datos?

- **Conciso**: menos líneas que diccionarios para datos tabulares
- **Predecible**: el orden es fijo y conocido
- **Trade-off**: menos legible que `namedtuple` o dataclasses. Adecuado para seeds pequeños.

---

## 6. Orden de Ejecución

```bash
python manage.py seed_destino   # Estados → Ciudades → Destinos
python manage.py seed_lugar     # Categorías → Lugares → Visitas (requiere seed_destino)
python manage.py seed_usuario   # Usuarios (independiente)
```

Ejecutar fuera de orden:

| Comando sin dependencia | Resultado |
|------------------------|-----------|
| `seed_lugar` sin `seed_destino` | Error claro + return sin cambios |
| `seed_lugar` sin `seed_usuario` | Crea testuser automático (fallback) |
| `seed_usuario` sin otros | Funciona sin problemas |

Se recomienda un comando maestro que ejecute todo:

```bash
python manage.py seed_destino && python manage.py seed_lugar && python manage.py seed_usuario
```

---

## 7. Buenas Prácticas (Resumen para Estudiantes)

1. **Usa management commands**, no scripts sueltos. Django te da ORM, settings, y output consistente sin configuración adicional.

2. **Sé idempotente**: ejecutar el mismo seed N veces debe dar el mismo resultado. Limpia datos existentes antes de insertar.

3. **Fail fast**: valida dependencias al inicio, antes de modificar la DB. El error debe decir exactamente qué falta.

4. **Determinismo**: si usas `random`, fija `random.seed()`. Los tests y el debugging te lo agradecerán.

5. **Logging progresivo**: cada paso debe imprimir qué está haciendo. El usuario no debe preguntarse "¿se colgó o está trabajando?".

6. **`create_user` para passwords**: nunca guardes passwords con `create()`. Siempre usa `create_user()`.

7. **Constantes fuera de `handle()`**: datos como listas/dicts/tuplas van a nivel de módulo. La lógica va dentro de `handle()`.

8. **Elimina en orden inverso a la creación**: borra tablas hijas antes que padres (o usa CASCADE pero sé explícito).

9. **Resumen final**: muestra cuántos registros de cada tipo se crearon. Confirma visualmente que todo salió bien.

10. **Un solo propósito**: cada seed se enfoca en una app. Si necesitas datos de múltiples apps, crea seeds separados y documénta las dependencias.
