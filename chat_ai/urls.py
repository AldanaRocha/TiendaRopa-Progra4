# chat_ai/urls.py
from django.urls import path
from . import views

app_name = "chat_ai"
urlpatterns = [
    path("chat/", views.ai_chat, name="ai-chat"), 
]