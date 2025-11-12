# chat_ai/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
# Asumo que tu modelo se llama 'Product' y está en la app 'productos'
from productos.models import Product 
from .models import ProductEmbedding
from .gemini_client import embed_text
from django.db import IntegrityError


@receiver(post_save, sender=Product)
def compute_product_embedding(sender, instance, created, **kwargs):
    # Crea o actualiza embedding
    # Nota: Llama al API en sincronía, lo que puede causar un retraso al guardar el producto.
    text = f"{instance.title}. {instance.description or ''}. Marca: {instance.marca or ''}" 
    emb = embed_text(text) 
    
    if emb:
        try:
            ProductEmbedding.objects.update_or_create(
                product=instance,
                defaults={"vector": emb})
        except IntegrityError:
            # Manejar caso si la relación ya existe
            pass
