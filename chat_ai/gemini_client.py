# chat_ai/gemini_client.py

import os
import logging
from google import genai 
from django.conf import settings

logger = logging.getLogger(__name__)

# --- Clase del Cliente ---
class GeminiClient:
    def __init__(self):
        # 1. Obtener la clave de la configuración de Django
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        if not api_key:
            # Lanza un error de configuración si la clave no se encuentra
            raise ValueError("GEMINI_API_KEY no está configurada en settings.py")
        
        # 2. Inicializar el cliente de forma explícita
        self.client = genai.Client(api_key=api_key)
        
        # 3. Definir el modelo predeterminado 
        self.default_model = "gemini-2.5-flash" 

    def generate_text(self, prompt, history: list = None, model=None, max_output_tokens=300):
        """
        Genera contenido de texto usando Gemini. 
        Ahora acepta 'history' para manejar el chat.
        """
        try:
            model_name = model if model else self.default_model
            
            # ******************************************************
            # *** CÓDIGO CORREGIDO: Usar el servicio de 'chats' ***
            # ******************************************************
            
            # Configuración de generación
            generation_config = {
                "max_output_tokens": max_output_tokens,
                "temperature": 0.7,
            }
            
            # 1. Crear la sesión de chat con el historial previo
            chat = self.client.chats.create(
                model=model_name, 
                history=history if history is not None else [],
                config=generation_config
            )
            
            # 2. Enviar el mensaje
            response = chat.send_message(prompt)
            
            if response.text:
                return response.text
            else:
                return "Error: La respuesta de Gemini está vacía o bloqueada."
                
        except Exception as e:
            # Esto captura el error
            logger.exception("Error al llamar a Gemini")
            return f"Lo siento, hubo un error al comunicarme con la IA. Mensaje técnico: {str(e)}"
        
    def embed_text(self, text, model="models/text-embedding-004"):
        """Genera embeddings de texto usando el cliente inicializado."""
        try:
            # Correcto: El SDK moderno usa genai.embed_content()
            result = self.client.embed_content( 
                model=model,
                content=text
            )
            return result['embedding']
        except Exception as e:
            logger.exception("Error al generar embedding en GeminiClient")
            raise e 

# 🚨 OPCIONAL PERO RECOMENDADO: Inicializar la instancia que usará signals.py
try:
    # Exporta una instancia global de la clase
    GEMINI_SERVICE_INSTANCE = GeminiClient() 
except ValueError:
    GEMINI_SERVICE_INSTANCE = None
except Exception as e:
    # Manejo de error si la clave falla, pero con un objeto None
    GEMINI_SERVICE_INSTANCE = None