# chat_ai/utils.py
# Este archivo contiene la función de envío de notificaciones de Telegram.

import requests
from django.conf import settings
# from .gemini_client import GEMINI_SERVICE_INSTANCE as gemini_service (Comentado para eliminar dependencia de IA)

def enviar_notificacion_telegram(mensaje, chat_id=None):
    """
    Envía un mensaje de texto simple a Telegram.
    Si no se proporciona chat_id, utiliza el ID por defecto (el ID del administrador).
    """
    
    # Asegúrate de que el token y el ID por defecto estén cargados en settings.py
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = chat_id if chat_id else settings.TELEGRAM_DEFAULT_CHAT_ID
    
    # URL de la API de Telegram para enviar mensajes
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': mensaje,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status() 
        print(f"Notificación de Telegram enviada a {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar notificación a Telegram: {e}")
        return False