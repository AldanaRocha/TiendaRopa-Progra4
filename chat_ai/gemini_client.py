# chat_ai/gemini_client.py

import os
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

# Configurar la API key
def configure_genai():
    api_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada")
    genai.configure(api_key=api_key)

# Inicializar al cargar el módulo
try:
    configure_genai()
except Exception as e:
    logger.error(f"Error configurando Gemini: {e}")


def generate_text(prompt, model="gemini-2.0-flash-exp", max_output_tokens=300):
    """
    Genera contenido de texto usando Gemini.
    """
    try:
        generation_config = {
            "max_output_tokens": max_output_tokens,
            "temperature": 0.7,
        }
        
        model_instance = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )
        
        response = model_instance.generate_content(prompt)
        
        if response.text:
            return response.text
        else:
            return "Error: La respuesta de Gemini está vacía."
            
    except Exception as e:
        logger.exception("Error al llamar a Gemini")
        return f"Error técnico: {str(e)}"


def embed_text(text, model="models/text-embedding-004"):
    """
    Genera embeddings de texto.
    """
    try:
        result = genai.embed_content(
            model=model,
            content=text
        )
        return result['embedding']
            
    except Exception as e:
        logger.exception("Error al generar embedding")
        return None