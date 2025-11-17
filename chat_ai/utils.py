# chat_ai/utils.py

import requests
from django.conf import settings
from .gemini_client import GEMINI_SERVICE_INSTANCE as gemini_service

def get_simple_ai_response_for_telegram(user_message: str) -> str:
    """
    Función de IA que añade un prompt de sistema simple para Telegram.
    NOTA: No maneja historial de chat aquí, solo respuestas directas.
    """
    if not gemini_service:
        return "Error: El servicio de IA no está activo."

    system_prompt = (
        "Sos un asistente amable de una tienda de ropa. Responde a preguntas sobre productos, "
        "stock, o el marketplace. Mantén la respuesta breve y usa el español."
    )
    
    # Construimos el prompt completo para la IA
    full_prompt = f"{system_prompt}\n\nUsuario: {user_message}"
    
    try:
        # Llamamos a la función de generación de texto simple (sin historial)
        # Reutilizamos la lógica que creamos para el Sugeridor de Precios si es compatible,
        # o usamos generate_text con un historial vacío.
        return gemini_service.generate_simple_text(full_prompt) 
        
    except Exception as e:
        print(f"Error en la lógica de IA para Telegram: {e}")
        return "Lo siento, tengo problemas técnicos para responder."



def enviar_notificacion_telegram(mensaje, chat_id=None):
    """Envía un mensaje de texto simple a Telegram."""
    
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = chat_id if chat_id else settings.TELEGRAM_DEFAULT_CHAT_ID
    
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