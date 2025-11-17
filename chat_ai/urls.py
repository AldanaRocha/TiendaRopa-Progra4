# chat_ai/urls.py

from django.urls import path
from . import views

# Este app_name debe coincidir con el namespace usado en el archivo principal (chat_ai)
app_name = "chat_ai" 

urlpatterns = [
    # Módulo Sugeridor de Precios
    path("price-suggest/", views.price_suggest, name="price-suggest"),
    
    # Módulo Chat Asistente
    path("chat/", views.ai_chat, name="ai-chat"),
    
    # Módulo Recomendador (usa PK)
    path("recommend/<int:pk>/", views.recommend_similar, name="recommend-similar"),
    
    path('webhook/', views.telegram_webhook, name='telegram-webhook'),
]