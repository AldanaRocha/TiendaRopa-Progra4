# chat_ai/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from productos.models import Product 
from .models import ProductEmbedding
from .gemini_client import GEMINI_SERVICE_INSTANCE # <- Usa esta importación
from django.db import IntegrityError


@receiver(post_save, sender=Product)
def compute_product_embedding(sender, instance, created, **kwargs):
    # 🚨 CORRECCIÓN CRÍTICA 2: Verificar si el servicio está disponible
    if GEMINI_SERVICE_INSTANCE is None:
        print("ADVERTENCIA: El servicio Gemini no está activo (problema con la clave API). No se generarán embeddings.")
        return

    # Crea o actualiza embedding
    text = f"{instance.title}. {instance.description or ''}. Marca: {instance.marca or ''}" 
    
    try:
        # 🚨 CORRECCIÓN CRÍTICA 3: Llamar al MÉTODO de la INSTANCIA
        # 'embed_text' ahora se llama a través del objeto GEMINI_SERVICE_INSTANCE
        emb = GEMINI_SERVICE_INSTANCE.embed_text(text) 
    
    except Exception as e:
        # Maneja cualquier error del API (ej. 429 cuota agotada)
        print(f"ERROR: Fallo al generar embedding para Producto ID {instance.pk}: {e}")
        return
    
    # Si se obtuvo el embedding
    if emb:
        try:
            ProductEmbedding.objects.update_or_create(
                product=instance,
                defaults={"vector": emb})
        except IntegrityError:
            # Manejar caso si la relación ya existe (aunque update_or_create lo previene)
            pass
        except Exception as e:
             print(f"ERROR: Fallo al guardar el embedding en la BD: {e}")