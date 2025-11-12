# chat_ai/apps.py
from django.apps import AppConfig

class ChatAiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_ai'

    def ready(self):
        import chat_ai.signals  # Esto registra el signal