from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    
    # 🚨 Modificación 1: Añadir imagen por defecto
    avatar = models.ImageField(
        default='profile_pics/default.png', # Ruta a tu imagen por defecto
        upload_to='profile_pics',           # Cambiado a 'profile_pics' (más común)
        blank=True, 
        null=True
    )
    
    # 🚨 Modificación 2: Campo para el nombre que el usuario quiere mostrar
    display_name = models.CharField(max_length=50, blank=True, null=True) 

    def __str__(self):
        return self.user.username
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Aseguramos que se cree el perfil cuando se crea el usuario
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Esto guarda el perfil cuando se guarda el usuario (mantiene la sincronía)
    instance.profile.save()