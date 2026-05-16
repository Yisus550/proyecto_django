import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from destino.models import Destino
from lugar.models import Categoria, Lugar, Visita
from user.models import Usuario

CATEGORIAS = [
    "Restaurante",
    "Museo",
    "Parque",
    "Cafetería",
    "Bar",
    "Mercado",
    "Plaza",
    "Monumento",
    "Teatro",
    "Galería",
    "Mirador",
    "Tienda",
    "Panadería",
    "Cine",
    "Biblioteca",
    "Jardín",
    "Acuario",
    "Zoológico",
    "Templo",
    "Hotel",
]

CATEGORIAS_COMIDA = {"Restaurante", "Cafetería", "Bar", "Panadería"}

LUGARES = [
    ("Café Central", "Cafetería histórica con ambiente tranquilo."),
    ("Restaurante El Faro", "Especialidad en mariscos frescos."),
    ("Parque de la Paz", "Espacio verde ideal para caminar."),
    ("Museo de Arte", "Colección permanente de arte local."),
    ("Bar El Callejón", "Música en vivo y coctelería artesanal."),
    ("Mercado Hidalgo", "Puestos de comida típica y artesanías."),
    ("Plaza Mayor", "El corazón de la ciudad con arquitectura colonial."),
    ("Mirador del Valle", "Vista panorámica de toda la región."),
    ("Teatro Degollado", "Recinto histórico para artes escénicas."),
    ("Galería Libertad", "Exposiciones temporales de artistas emergentes."),
    ("Panadería La Tradición", "Pan de dulce horneado en leña."),
    ("Biblioteca Central", "Gran acervo bibliográfico y salas de estudio."),
    ("Jardín Botánico", "Gran variedad de flora regional."),
    ("Acuario Marino", "Túnel submarino con tiburones."),
    ("Zoológico de la Ciudad", "Hábitats naturales de diversas especies."),
    ("Templo del Carmen", "Arquitectura barroca impresionante."),
    ("Hotel Plaza", "Alojamiento con estilo y confort."),
    ("Cine Rialto", "Cine de arte y estrenos mundiales."),
    ("Monumento a los Héroes", "Escultura emblemática de la ciudad."),
    ("Tienda de Souvenirs", "Recuerdos únicos de tu visita."),
]

VISITAS_COUNT = 20


class Command(BaseCommand):
    help = "Siembra 20 categorías, 20 lugares y 20 visitas"

    def handle(self, *args, **options):
        random.seed(42)

        destinos = list(Destino.objects.all())
        if not destinos:
            self.stderr.write(
                self.style.ERROR("¡Error! No hay destinos. Ejecuta seed_db primero.")
            )
            return

        self.stdout.write("Limpiando datos de lugar...")
        Visita.objects.all().delete()
        Lugar.objects.all().delete()
        Categoria.objects.all().delete()

        self.stdout.write("Creando categorías...")
        cat_objs = []
        for nombre in CATEGORIAS:
            cat = Categoria.objects.create(nombre=nombre)
            cat_objs.append(cat)
            self.stdout.write(f"  Categoría: {nombre}")

        self.stdout.write("Creando lugares...")
        lugar_objs = []
        for nombre, descripcion in LUGARES:
            cat = random.choice(cat_objs)
            lugar = Lugar.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                categoria=cat,
                destino=random.choice(destinos),
            )
            lugar_objs.append(lugar)
            self.stdout.write(f"  Lugar: {nombre} ({cat.nombre})")

        usuarios = list(Usuario.objects.all())
        if not usuarios:
            self.stdout.write("  No hay usuarios. Creando testuser...")
            u = Usuario.objects.create_user(
                username="testuser", email="test@example.com", password="password123"
            )
            usuarios = [u]

        self.stdout.write("Creando visitas...")
        for i in range(VISITAS_COUNT):
            lugar = random.choice(lugar_objs)
            es_comida = lugar.categoria.nombre in CATEGORIAS_COMIDA
            visita = Visita.objects.create(
                usuario=random.choice(usuarios),
                lugar=lugar,
                fecha=date.today() - timedelta(days=random.randint(1, 60)),
                resena=f"Excelente experiencia en {lugar.nombre}.",
                calificacion=random.randint(1, 5),
                platillo=f"Especialidad {i+1}" if es_comida else "",
            )
            self.stdout.write(
                f"  Visita {i+1}: {lugar.nombre} "
                f"(calif: {visita.calificacion})"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed completo: {len(CATEGORIAS)} categorías, "
                f"{len(LUGARES)} lugares, {VISITAS_COUNT} visitas"
            )
        )
