# chat_ai/models.py
from django.db import models

class ProductEmbedding(models.Model):
    # Enlaza con tu modelo Product (ajusta el import si hace falta)
    # Suponemos que el modelo Product está en tu app 'productos'
    product = models.OneToOneField('productos.Product', on_delete=models.CASCADE, related_name="embedding")
    
    model = models.CharField(max_length=100, default="gemini-embedding-001")
    vector = models.JSONField()  # Guardamos lista de floats
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Embedding {self.product_id} ({self.model})"