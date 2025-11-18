# productos/apps.py

from django.apps import AppConfig

class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productos'
    
    def ready(self):
        # 🚨 ESTA LÍNEA ES LA QUE ACTIVA LAS SEÑALES 🚨
        import productos.signals