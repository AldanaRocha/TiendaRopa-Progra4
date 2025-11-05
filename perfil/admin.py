from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin (admin.ModelAdmin):
    list_display=('user','bio','website')
    search_fields=('user_username','user_email')
# Register your models here.
