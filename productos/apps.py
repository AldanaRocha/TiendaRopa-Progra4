from django.apps import AppConfig


class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productos'


def ready(self):
        # 🚨 Importa el archivo de señales para que se cargue
        import productos.signals