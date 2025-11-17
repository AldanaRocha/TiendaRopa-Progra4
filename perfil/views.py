from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# 🚨 Importación modificada: Ahora importamos los dos formularios
from .forms import UserUpdateForm, ProfileUpdateForm 
from .models import Profile
from django.contrib.auth.models import User # Para Type Hinting, aunque no estrictamente necesario aquí

# 🚨 La vista edit_profile se renombra a profile_update para mayor claridad
@login_required
def profile_update(request):
    
    # 1. Manejo del POST (Cuando el usuario envía los formularios)
    if request.method == 'POST':
        # Instanciamos formularios para el modelo User (username) y Profile (avatar/display_name)
        # request.FILES es crucial para manejar la subida de la imagen del avatar
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            
            messages.success(request, '¡Tu perfil y avatar han sido actualizados exitosamente!')
            
            # Redireccionar a la URL de edición para evitar el doble envío
            return redirect('perfil:profile-update') # 🚨 Asegúrate de que este 'profile-update' coincida con tu urls.py
            
    # 2. Manejo del GET (Cuando se visita la página)
    else:
        # Instanciamos los formularios con los datos actuales
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,  # Formulario del usuario
        'p_form': p_form   # Formulario del perfil
    }
    # 🚨 Se asume que la plantilla se llama 'perfil/profile_update.html'
    return render(request, "perfil/profile_update.html", context)


@login_required
def profile_view(request):
    # La vista de visualización del perfil no se modifica, pero ahora tendrá acceso a los nuevos campos.
    return render(request, "perfil/profile.html", {"profile": request.user.profile})

def politica_devolucion(request):
    return render(request, 'perfil/politica_devolucion.html')