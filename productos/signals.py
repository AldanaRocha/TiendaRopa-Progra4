# productos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product 
# 🚨 Ajusta esta importación a la ruta correcta de tu función de envío de Telegram
from chat_ai.utils import enviar_notificacion_telegram 

@receiver(post_save, sender=Product)
def notificar_nuevo_producto(sender, instance, created, **kwargs):
    """Envía una notificación de Telegram cuando se crea un nuevo producto."""
    
    if created: # Solo si el objeto Product fue creado
        mensaje = (
            f"✨ ¡Nuevo Producto Publicado! ✨\n\n"
            f"Título: {instance.title}\n"
            f"Marca: {instance.marca}\n"
            f"Precio: ${instance.price}\n"
            f"Publicado por: {instance.user.username}" # Asumiendo que Product tiene un campo 'user'
        )
        enviar_notificacion_telegram(mensaje)

# NOTA: Debes asegurar que esta señal se registre en tu AppConfig.