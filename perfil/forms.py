# perfil/forms.py

from django import forms
from django.contrib.auth.models import User # Necesitas importar el modelo User
from .models import Profile 

# 1. Formulario para editar campos del modelo USER (username)
class UserUpdateForm(forms.ModelForm):
    # Permite al usuario cambiar el nombre de usuario de Django
    username = forms.CharField(max_length=150, required=True) 

    class Meta:
        model = User
        fields = ['username']

# 2. Formulario para editar campos del modelo PROFILE (avatar, bio, etc.)
class ProfileUpdateForm(forms.ModelForm):
    # Añadimos el nuevo campo display_name y los campos existentes
    
    class Meta:
        model = Profile
        # Incluye todos los campos que el usuario puede editar
        fields = ["bio", "website", "avatar", "display_name"]