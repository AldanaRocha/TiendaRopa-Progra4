from django.shortcuts import render
from .forms import ChatForm
from .gemini_client import generate_text

def ai_chat(request):
    # Inicializa el historial de chat en la sesión si no existe
    if "ai_chat_history" not in request.session:
        request.session["ai_chat_history"] = []
    history = request.session["ai_chat_history"]
    
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            user_msg = form.cleaned_data["message"]

            # Instrucciones del sistema (contexto del asistente)
            system = (
                "Sos un asistente amablemente orientado a ayudar en una tienda de ropa (publicar, comprar, trueque). "
                "Tu objetivo es dar una bienvenida específica: 'Estoy aquí para ayudarte con todo lo relacionado a nuestra tienda de ropa.' "
                "Responde siempre en español, de manera amable y breve."
            )
            accumulated = system + "\n\n"

            # Incluir últimos 6 turnos del historial para mantener contexto
            for turn in history[-6:]:
                accumulated += f"Usuario: {turn['user']}\nAsistente: {turn['ai']}\n"
            accumulated += f"Usuario: {user_msg}\nAsistente: "

            # Llamada a Gemini
            ai_resp = generate_text(accumulated)

            # Guardar el nuevo turno
            history.append({"user": user_msg, "ai": ai_resp})
            request.session["ai_chat_history"] = history
            request.session.modified = True
    else:
        form = ChatForm()

    return render(request, "chat_ai/ai_chat.html", {"form": form, "history": history})
