from django.core.management.base import BaseCommand
from destino.models import Estado, Ciudad, Destino


ESTADOS = [
    "Aguascalientes",
    "Baja California",
    "Campeche",
    "Chiapas",
    "Chihuahua",
    "Coahuila",
    "Colima",
    "Durango",
    "Guanajuato",
    "Guerrero",
]

CIUDADES = {
    "Aguascalientes": ["Aguascalientes", "Jesús María", "Calvillo"],
    "Baja California": ["Mexicali", "Tijuana", "Ensenada"],
    "Campeche": ["Campeche", "Ciudad del Carmen", "Champotón"],
    "Chiapas": ["Tuxtla Gutiérrez", "San Cristóbal de las Casas", "Tapachula"],
    "Chihuahua": ["Chihuahua", "Ciudad Juárez", "Delicias"],
    "Coahuila": ["Saltillo", "Torreón", "Monclova"],
    "Colima": ["Colima", "Manzanillo", "Tecomán"],
    "Durango": ["Durango", "Gómez Palacio", "Santiago Papasquiaro"],
    "Guanajuato": ["Guanajuato", "León", "San Miguel de Allende"],
    "Guerrero": ["Chilpancingo", "Acapulco", "Taxco"],
}

DESTINOS = [
    ("Feria de San Marcos, Sabores Tradicionales",
     "Recorrido gastronómico por la Feria de San Marcos con platillos típicos de Aguascalientes."),
    ("Ruta del Vino y Gastronomía",
     "Tour por los valles vinícolas con degustación de vinos y cocina bajacaliforniana."),
    ("Mercado Principal de Campeche",
     "Exploración de la cocina campechana en el mercado principal: pan de cazón, cochinita y mariscos."),
    ("Mercado de los Sabores Chiapanecos",
     "Degustación de cochito, tamales chiapanecos y pozol en el mercado de Tuxtla."),
    ("Zona Centro Gastronómica",
     "Recorrido por restaurantes tradicionales del centro de Chihuahua: machaca, asado y queso."),
    ("Mercado Zaragoza, Tradición Culinaria",
     "Tour gastronómico por el Mercado Zaragoza: cortes de carne, pan de pulque y dulces típicos."),
    ("Portal Morelos y Sopitos",
     "Ruta de sopitos, tatemados y bebidas tradicionales en el Portal Morelos de Colima."),
    ("Mercado Gómez Palacio",
     "Recorrido por la comida duranguense: caldillo, gorditas y asado de boda."),
    ("Mercado Hidalgo, Gueritos",
     "Tour por el mercado más emblemático de Guanajuato: enchiladas mineras, pacholas y guasanas."),
    ("Fiesta de la Nao, Gastronomía Tradicional",
     "Experiencia culinaria en Chilpancingo: pozole, adobo y tamales de elote."),
]


class Command(BaseCommand):
    help = "Siembra datos iniciales: 10 estados, 30 ciudades, 10 destinos"

    def handle(self, *args, **options):
        self.stdout.write("Limpiando datos existentes...")
        Destino.objects.all().delete()
        Ciudad.objects.all().delete()
        Estado.objects.all().delete()

        self.stdout.write("Creando estados...")
        estado_objs = {}
        for nombre in ESTADOS:
            estado = Estado.objects.create(nombre=nombre)
            estado_objs[nombre] = estado
            self.stdout.write(f"  Estado: {nombre}")

        self.stdout.write("Creando ciudades...")
        ciudad_objs = {}
        for estado_nombre, ciudades in CIUDADES.items():
            estado = estado_objs[estado_nombre]
            for ciudad_nombre in ciudades:
                ciudad = Ciudad.objects.create(nombre=ciudad_nombre, estado=estado)
                ciudad_objs[(estado_nombre, ciudad_nombre)] = ciudad
                self.stdout.write(f"  Ciudad: {ciudad_nombre} ({estado_nombre})")

        self.stdout.write("Creando destinos...")
        for (nombre, descripcion), estado_nombre in zip(DESTINOS, ESTADOS):
            estado = estado_objs[estado_nombre]
            primera_ciudad = CIUDADES[estado_nombre][0]
            ciudad = ciudad_objs[(estado_nombre, primera_ciudad)]
            Destino.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                estado=estado,
                ciudad=ciudad,
            )
            self.stdout.write(f"  Destino: {nombre} ({estado_nombre})")

        self.stdout.write(self.style.SUCCESS(
            f"Seed completo: {len(ESTADOS)} estados, "
            f"{sum(len(c) for c in CIUDADES.values())} ciudades, "
            f"{len(DESTINOS)} destinos"
        ))
