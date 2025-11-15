import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TiendaRopa.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Ver el sitio actual
site = Site.objects.get(id=1)
print(f"📍 Site ID: {site.id}")
print(f"📍 Site domain: {site.domain}")
print(f"📍 Site name: {site.name}")

# Ver las apps sociales
print("\n=== SOCIAL APPS ===")
apps = SocialApp.objects.all()
if not apps:
    print("❌ No hay aplicaciones sociales configuradas")
else:
    for app in apps:
        print(f"\n🔑 Provider: {app.provider}")
        print(f"🔑 Name: {app.name}")
        print(f"🔑 Client ID: {app.client_id[:20]}...")
        print(f"🔑 Sites asociados: {[s.domain for s in app.sites.all()]}")