from django.urls import path
from . import views

urlpatterns = [
    path("generar/", views.generar_presupuesto, name="generar-presupuesto"),
]
