from django.core.management.base import BaseCommand
from user.models import Usuario


USUARIOS = [
    ("admin",     "admin@example.com",     "admin123",  "Admin",    "Sistema",   True,  True),
    ("staff1",    "staff1@example.com",    "staff123",  "María",    "López",     True,  False),
    ("jperez",    "juan.perez@example.com",  "pass123", "Juan",     "Pérez",     False, False),
    ("mgarcia",   "maria.garcia@example.com","pass123", "María",    "García",    False, False),
    ("lhernandez", "luis.hernandez@example.com","pass123","Luis",   "Hernández", False, False),
    ("agonzalez", "ana.gonzalez@example.com","pass123",  "Ana",     "González",  False, False),
    ("crodriguez", "carlos.rodriguez@example.com","pass123","Carlos","Rodríguez",False, False),
    ("mmartinez", "marta.martinez@example.com","pass123","Marta",   "Martínez",  False, False),
    ("rsanchez",  "raul.sanchez@example.com","pass123",  "Raúl",    "Sánchez",   False, False),
    ("lramirez",  "laura.ramirez@example.com","pass123","Laura",    "Ramírez",   False, False),
]


class Command(BaseCommand):
    help = "Siembra 10 usuarios: 1 superuser, 1 staff, 8 regulares"

    def handle(self, *args, **options):
        self.stdout.write("Limpiando usuarios existentes...")
        Usuario.objects.all().delete()

        self.stdout.write("Creando usuarios...")
        for username, email, password, first_name, last_name, is_staff, is_superuser in USUARIOS:
            Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff,
                is_superuser=is_superuser,
            )
            self.stdout.write(f"  Usuario: {username} ({first_name} {last_name})")

        self.stdout.write(self.style.SUCCESS(
            f"Seed completo: {len(USUARIOS)} usuarios"
        ))
