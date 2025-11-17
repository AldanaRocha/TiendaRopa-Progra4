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
        self.default_model = "gemini-2.5-pro" 

    def generate_text(self, prompt, history: list = None, model=None, max_output_tokens=300):
        """
        Genera contenido de texto para el CHAT usando una sesión con historial.
        """
        try:
            model_name = model if model else self.default_model
            
            generation_config = {
                "max_output_tokens": max_output_tokens,
                "temperature": 0.7,
            }
            
            # Crear la sesión de chat con el historial previo
            chat = self.client.chats.create(
                model=model_name, 
                history=history if history is not None else [],
                config=generation_config
            )
            
            # Enviar el mensaje
            response = chat.send_message(prompt)
            
            if response.text:
                return response.text
            else:
                return "Error: La respuesta de Gemini está vacía o bloqueada."
                
        except Exception as e:
            logger.exception("Error al llamar a Gemini en generate_text (CHAT)")
            return f"Lo siento, hubo un error al comunicarme con la IA. Mensaje técnico: {str(e)}"

    def generate_simple_text(self, prompt: str, model=None, max_output_tokens=300) -> str:
        """
        Genera contenido de texto SIN historial (ideal para Price Suggest).
        Utiliza el método models.generate_content para compatibilidad.
        """
        try:
            model_name = "gemini-2.5-pro"
            
            generation_config = {
                "max_output_tokens": max_output_tokens,
                "temperature": 0.7,
            }
            
            # 🚨 CORRECCIÓN: Usamos models.generate_content() para generación simple
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=generation_config
            )
            
            if response.text:
                return response.text
            else:
                # Este error se activa por filtros de seguridad o prompt vacío
                return "Error: La respuesta de Gemini está vacía o bloqueada (posiblemente por seguridad)."
            
        except Exception as e:
            # Esto captura el error si generate_content falla
            print(f"Error técnico en Sugerencia de Precio: {e}") 
            return f"Error técnico: {str(e)}"
        
    def embed_text(self, text, model="models/text-embedding-004"):
        """Genera embeddings de texto usando el cliente inicializado."""
        try:
            result = self.client.embed_content( 
                model=model,
                content=text
            )
            return result['embedding']
        except Exception as e:
            logger.exception("Error al generar embedding en GeminiClient")
            raise e 

# --- INSTANCIA GLOBAL ---
try:
    # Exporta una instancia global de la clase
    GEMINI_SERVICE_INSTANCE = GeminiClient() 
except ValueError:
    GEMINI_SERVICE_INSTANCE = None
except Exception as e:
    # Manejo de error si la clave falla, pero con un objeto None
    GEMINI_SERVICE_INSTANCE = None