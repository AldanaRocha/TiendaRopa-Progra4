from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .gemini_client import GeminiClient 
from productos.models import Product 
from .forms import PriceSuggestForm, ChatForm
from .models import ProductEmbedding 
import numpy as np 
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import enviar_notificacion_telegram

# --- INSTANCIA GLOBAL DEL CLIENTE ---
# Usar la instancia global si está definida en gemini_client.py
from .gemini_client import GEMINI_SERVICE_INSTANCE as gemini_service

# Si la instancia no existe (ej. por error de clave API), usamos None
if gemini_service is None:
    print("Advertencia: No se pudo inicializar GeminiClient. Revisa tu GEMINI_API_KEY.")

# ---

def _get_ai_response(prompt, history=None):
    """Función de ayuda para gestionar la llamada a Gemini para el CHAT."""
    if not gemini_service:
        return "Error crítico: El servicio de IA no está configurado (revisa GEMINI_API_KEY)."

    try:
        # LLAMADA A GEMINI USANDO generate_text (para CHAT con historial)
        return gemini_service.generate_text(prompt)
    except Exception as e:
        error_msg = f"Error al contactar a la IA. Código de error: {str(e).split(':')[0]}"
        return error_msg

def _get_simple_ai_response(prompt):
    """Función de ayuda para gestionar la llamada a Gemini para tareas SIMPLES (Sugerencia de Precio)."""
    if not gemini_service:
        return "Error crítico: El servicio de IA no está configurado (revisa GEMINI_API_KEY)."

    try:
        # LLAMADA A GEMINI USANDO generate_simple_text (para PRICE SUGGEST)
        return gemini_service.generate_simple_text(prompt)
    except Exception as e:
        error_msg = f"Error al contactar a la IA. Código de error: {str(e).split(':')[0]}"
        return error_msg


# 1. Módulo Sugeridor de Precios (CORREGIDO Y LIMPIO)
def price_suggest(request):
    sugerencia = None
    
    if request.method == "POST":
        form = PriceSuggestForm(request.POST)
        if form.is_valid():
            # 🚨 data AHORA ESTÁ DEFINIDA AQUÍ
            data = form.cleaned_data
            
            # --- PREPARACIÓN DEL PROMPT ROBUSTO ---
            details = [
                data['title'], 
                data['description'], 
                data['marca'],
                str(data.get('current_price', ''))
            ]
            # 🚨 product_details AHORA ESTÁ DEFINIDA AQUÍ
            product_details = " ".join([d for d in details if d])
            
            # --- PROMPT FINAL ENVIADO A GEMINI ---
            prompt = (
                "Analiza el siguiente producto para un marketplace en Argentina y sugiere un precio de venta "
                "en pesos argentinos (ARS) y una justificación breve, basado en los detalles. "
                "Responde de forma clara y profesional."
                f"\n\nDETALLES DEL PRODUCTO: {product_details}"
            )
            # -------------------------------------
            
            respuesta = _get_simple_ai_response(prompt) 
            sugerencia = respuesta
            
            if "Error" in sugerencia:
                messages.error(request, f"Fallo en la sugerencia de precio: {sugerencia}")

    else:
        form = PriceSuggestForm()
        
    return render(request, "chat_ai/price_suggest.html", {"form": form, "sugerencia": sugerencia})


# 2. Módulo Chat Asistente (SIN CAMBIOS)
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
                "Sos un asistente amablemente orientado a ayudar en una tienda de ropa "
                "(publicar, comprar, trueque). Responde siempre en español, de manera amable y breve."
            )
            
            # Construir el prompt, incluyendo el historial
            accumulated = system + "\n\n"
            for turn in history[-6:]: # Incluir últimos 6 turnos
                accumulated += f"Usuario: {turn['user']}\nAsistente: {turn['ai']}\n"
            accumulated += f"Usuario: {user_msg}\nAsistente: "

            # Llamada a Gemini (usa la función _get_ai_response original)
            ai_resp = _get_ai_response(accumulated)

            if "Error" in ai_resp:
                messages.error(request, f"El chat falló: {ai_resp}")
                ai_resp = "Disculpa, hubo un error técnico. Inténtalo de nuevo."
            else:
                # Guardar el nuevo turno solo si fue exitoso
                history.append({"user": user_msg, "ai": ai_resp})
                request.session["ai_chat_history"] = history
                request.session.modified = True
                request.session.save() 
            
            # Redirección para evitar el doble envío del formulario (POST-Redirect-GET)
            return redirect("chat_ai:ai-chat") 
            
    else:
        form = ChatForm()

    return render(request, "chat_ai/ai_chat.html", {"form": form, "history": history})


# 3. Módulo Recomendador por Embeddings (SIN CAMBIOS)
def recommend_similar(request, pk):
    # Obtiene el producto base o lanza 404
    producto = get_object_or_404(Product, pk=pk)
    target = None

    try:
        # 1. Intenta usar el embedding cacheado
        target = producto.embedding.vector
    except Exception:
        # 2. Si no hay embedding, lo genera "en vuelo" (esto puede tardar)
        if not gemini_service:
            messages.error(request, "El servicio de embeddings no está configurado.")
            return render(request, "chat_ai/recommendations.html", {"product": producto, "recommended": []})

        text = f"{producto.title}. {producto.description or ''}"
        
        try:
            # LLAMADA A GEMINI
            target = gemini_service.embed_text(text)
        except Exception as e:
            messages.error(request, f"Fallo al generar embedding: {str(e).split(':')[0]}")
            target = None

    if target is None:
        return render(request, "chat_ai/recommendations.html", {"product": producto, "recommended": []})

    # 3. Búsqueda de similitud y cálculo
    candidates = ProductEmbedding.objects.exclude(product=producto)
    results = []
    tvec = np.array(target, dtype=float) 
    
    # Calcula la similitud coseno 
    for c in candidates:
        vec = np.array(c.vector, dtype=float)
        # Fórmula de similitud coseno
        cos = float(np.dot(tvec, vec) / (np.linalg.norm(tvec) * np.linalg.norm(vec)))
        results.append((c.product, cos))

    results.sort(key=lambda x: x[1], reverse=True)
    top = [p for p, score in results[:6]]

    return render(request, "chat_ai/recommendations.html", {"product": producto, "recommended": top})


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            # 1. Extraer ID del remitente, nombre y mensaje
            chat_id_remitente = data['message']['chat']['id']
            nombre_usuario = data['message']['from'].get('first_name', 'Usuario Desconocido')
            user_message = data['message']['text']
            
            # 2. Construir el mensaje de ALERTA para el ADMINISTRADOR
            mensaje_alerta = (
                f"🚨 NUEVA CONSULTA DE TELEGRAM 🚨\n\n"
                f"De: {nombre_usuario} (ID: {chat_id_remitente})\n"
                f"Mensaje: {user_message}\n\n"
                f"👉 Para responder, abre el chat con el usuario en Telegram."
            )
            
            # 3. Enviar la alerta a TI (Usando tu Chat ID como destino fijo)
            # Reutiliza el ID de tu chat personal/grupo de administradores.
            enviar_notificacion_telegram(mensaje_alerta) 
            
            # 4. (Opcional) Enviar un mensaje de confirmación al usuario (para que sepa que fue recibido)
            mensaje_confirmacion = "¡Hola! Hemos recibido tu consulta. Nuestro equipo te responderá pronto. ¡Gracias!"
            enviar_notificacion_telegram(mensaje_confirmacion, chat_id=chat_id_remitente)
            
            return JsonResponse({"status": "ok"})

        except Exception as e:
            print(f"Error procesando webhook (Alerta fallida): {e}")
            return HttpResponse(status=200)

    return HttpResponse(status=400)