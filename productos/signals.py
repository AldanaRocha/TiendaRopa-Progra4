# productos/signals.py (Añadir un bloque try...except)

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product 
from chat_ai.utils import enviar_notificacion_telegram 
import logging # 🚨 Nuevo: para registrar el error
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def notificar_nuevo_producto(sender, instance, created, **kwargs):
    if created:
        mensaje = (
            f"✨ ¡Nuevo Producto Publicado! ✨\n\n"
            f"Título: {instance.title}\n"
            f"Marca: {instance.marca}\n"
            f"Precio: ${instance.price}\n"
           # f"Publicado por: {instance.user.username}" 
        )
        try:
            # 🚨 Intentamos enviar la notificación
            enviar_notificacion_telegram(mensaje)
            
        except Exception as e:
            # 🚨 Si falla, el error aparecerá en la terminal de Django (logs)
            logger.error(f"Error al enviar notificación de Telegram: {e}")