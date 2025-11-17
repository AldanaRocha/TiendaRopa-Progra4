from django.urls import path
from . import views

app_name = 'perfil'

urlpatterns = [
   path('editar/', views.profile_update, name='profile-update'), # 🚨 Cambia esto
   path('', views.profile_view, name='profile-view'), 
   path('politicas/devolucion/', views.politica_devolucion, name='politica-devolucion'),
   ]