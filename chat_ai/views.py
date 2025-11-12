# chat_ai/views.py
from django.shortcuts import render
from .forms import ChatForm
from .gemini_client import generate_text

def ai_chat(request):
    # Inicializa el historial de chat en la sesión si no existe [cite: 202]
    if "ai_chat_history" not in request.session:
        request.session["ai_chat_history"] = []
    history = request.session["ai_chat_history"]
    
    if request.method == "POST": 
        form = ChatForm(request.POST) 
        if form.is_valid(): 
            user_msg = form.cleaned_data["message"] 
            
            # Definición del sistema y armado del prompt con historial (últimos 6 turnos)"So
            system = "Sos un asistente amablemente orientado a ayudar en una tienda de ropa (publicar, comprar, trueque). "
            "Tu objetivo es dar una bienvenida específica: 'Estoy aquí para ayudarte con todo lo relacionado a nuestra tienda de ropa.' "
            "Responde en español."
            accumulated = system + "\n\n" 
            
            # Bucle para incluir el historial en el prompt para mantener el contexto 
            for turn in history[-6:]: 
                accumulated += f"Usuario: {turn['user']}\nAsistente: {turn['ai']}\n" 
            accumulated += f"Usuario: {user_msg}\nAsistente: " 
            
            ai_resp = generate_text(accumulated) 
            
            # Guardamos el nuevo turno en el historial [cite: 217]
            history.append({"user": user_msg, "ai": ai_resp}) 
            request.session["ai_chat_history"] = history 
            request.session.modified = True 
    else:
        form = ChatForm() 
        
    return render(request, "chat_ai/ai_chat.html", {"form": form, "history": history}) 