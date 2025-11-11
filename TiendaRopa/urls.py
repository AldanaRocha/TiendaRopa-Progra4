
from django.contrib import admin
from django.urls import path, include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),  # rutas de allauth
    path("", home, name="home"),
    path("productos/", include("productos.urls")),
    path('perfil/', include('perfil.urls')),

 
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
