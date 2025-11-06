from django.urls import path
from . import views

app_name = 'perfil'

urlpatterns = [
    path("editar/", views.edit_profile, name="edit_profile"),
    path("ver_perfil/", views.profile_view, name="profile"),
]
