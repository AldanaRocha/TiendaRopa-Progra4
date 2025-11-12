# chat_ai/gemini_client.py (CÓDIGO FINAL CORREGIDO Y ROBUSTO)

import os
import logging
from google import genai
from google.genai import types
from django.conf import settings # <-- CLAVE: Necesitamos esto para leer la configuración

logger = logging.getLogger(__name__)

# Aquí definimos la clave directamente para forzar la prueba
# REMPLAZA EL CÓDIGO de get_client() con este:
def get_client():
    # Usamos el valor hardcodeado para la prueba final
    api_key_test = "AIzaSyAQS6wLuQ0lJik0rj0ivpFMsA3nTYhMawk" 
    
    if not api_key_test:
        raise ValueError("Error crítico: Clave no encontrada")
    
    # Intenta usar la clave hardcodeada
    client = genai.Client(api_key=api_key_test)
    return client
# ----------------------------------------------------------------------
# ELIMINAMOS el patrón singleton (_client y client()) para usar el patrón 'with'
# ----------------------------------------------------------------------


def generate_text(prompt, model="gemini-2.5-flash", max_output_tokens=300):
    """
    Genera contenido de texto usando el gestor de contexto 'with'.
    """
    try:
        # Usamos 'with get_client()' para inicializar y cerrar el cliente limpiamente
        with get_client() as c:
            # Configuración para la generación de contenido
            config = types.GenerateContentConfig(
                max_output_tokens=max_output_tokens,
                temperature=0.7
            )
            
            # Llamada al modelo
            response = c.models.generate_content(
                model=model, 
                contents=prompt,
                config=config
            )
            
            # Extraer el texto de la respuesta
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                # Manejo de bloqueo de seguridad o respuesta vacía
                if response.prompt_feedback.block_reason:
                    print(f"\n--- BLOQUEO DE SEGURIDAD DETECTADO ---")
                    print(f"Motivo: {response.prompt_feedback.block_reason}")
                    print("--------------------------------------\n")
                    return "Error de generación: La respuesta de Gemini fue bloqueada."
                else:
                    return "Error de generación: La respuesta de Gemini está vacía."
            
    except ValueError as e:
        # Captura errores de clave API faltante
        return "ERROR CRÍTICO: La clave GEMINI_API_KEY no se está leyendo. Verifica tu archivo .env."
        
    except Exception as e:
        logger.exception("Error al llamar a Gemini generate_content")
        print(f"\n--- ERROR DETALLADO DE GEMINI ---\n{e}\n----------------------------------\n")
        return "Lamento mucho la interrupción, pero estoy experimentando un problema técnico."


def embed_text(text, model="text-embedding-004"):
    """
    Genera embeddings, usando el patrón 'with' para cerrar el cliente.
    """
    try:
        with get_client() as c:
            response = c.models.embed_content(
                model=model, 
                contents=text
            )
            
            if hasattr(response, 'embeddings') and len(response.embeddings) > 0:
                embeddings = response.embeddings
                return embeddings[0].values if hasattr(embeddings[0], 'values') else embeddings[0]
            
            return None # Retorna None si no hay embedding
            
    except Exception as e:
        logger.exception("Error al generar embedding")
        return None