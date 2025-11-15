from django.db import models
from django.contrib.auth.models import User
from productos.models import Product  # o la app donde tengas tus productos

class Presupuesto(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"Presupuesto #{self.id} - {self.comprador or 'Anónimo'}"

class PresupuestoItem(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
