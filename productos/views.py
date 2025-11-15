from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.http import HttpResponse, JsonResponse
import mercadopago
from django.conf import settings


@login_required
def product_list(request):
    products = Product.objects.filter(active=True).order_by("-created_at")
    
    # Filtro por nombre del producto
    search = request.GET.get('search')
    if search:
        products = products.filter(title__icontains=search)
    
    # Filtro por marca
    marca = request.GET.get('marca')
    if marca:
        products = products.filter(marca__icontains=marca)
    
    # Filtro por nuevo/usado
    nuevo = request.GET.get('nuevo')
    if nuevo != '' and nuevo is not None:
        products = products.filter(nuevo=int(nuevo))
    
    return render(request, "product_list.html", {"products": products})


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect("product-list")
    else:
        form = ProductForm()
    return render(request, "product_form.html", {"form": form})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product-list")
    else:
        form = ProductForm(instance=product)
    return render(request, "product_form.html", {"form": form})


def product_delete(request, pk):
    products = get_object_or_404(Product, pk=pk)
    products.delete()
    return redirect("product-list")


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Inicializar carrito en sesión
    if 'carrito' not in request.session:
        request.session['carrito'] = {}
    
    carrito = request.session['carrito']
    product_id_str = str(product_id)
    
    # Agregar o incrementar cantidad
    if product_id_str in carrito:
        carrito[product_id_str] += 1
    else:
        carrito[product_id_str] = 1
    
    request.session['carrito'] = carrito
    request.session.modified = True
    
    return redirect("view-cart")


def view_cart(request):
    carrito = request.session.get('carrito', {})
    
    # Reconstruir items del carrito
    items_carrito = []
    total = 0
    
    for product_id, cantidad in carrito.items():
        try:
            product = Product.objects.get(id=int(product_id))
            subtotal = cantidad * float(product.price)
            items_carrito.append({
                'product': product,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
        except Product.DoesNotExist:
            pass
    
    context = {
        'items': items_carrito,
        'total': total
    }
    return render(request, "cart.html", context)


def create_preference_cart(request):
    print("=== INICIO CREATE PREFERENCE ===")
    
    try:
        carrito = request.session.get('carrito', {})
        print(f"Carrito: {carrito}")
        
        if not carrito:
            return JsonResponse({"error": "Carrito vacío"}, status=400)
        
        # Verificar token
        token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
        if not token:
            return JsonResponse({"error": "Token de MercadoPago no configurado"}, status=500)
        
        sdk = mercadopago.SDK(token)
        
        # Construir items
        items = []
        for product_id, cantidad in carrito.items():
            try:
                product = Product.objects.get(id=int(product_id))
                print(f"Producto: {product.title}, Precio: {product.price}, Cantidad: {cantidad}")
                
                items.append({
                    "title": product.title,
                    "description": f"Marca: {product.marca}",  # ← CORREGIDO: usar description
                    "quantity": cantidad,
                    "currency_id": "ARS",
                    "unit_price": float(product.price),
                })
            except Product.DoesNotExist:
                print(f"Producto {product_id} no encontrado")
                continue
        
        if not items:
            return JsonResponse({"error": "No hay items válidos"}, status=400)
        
        print(f"Items: {items}")
        
        # IMPORTANTE: Actualizar URLs a tu dominio de Render
        preference_data = {
            "items": items,
            "back_urls": {
                "success": "https://tiendaropa-progra4.onrender.com/lib/pago/exitoso/",
                "failure": "https://tiendaropa-progra4.onrender.com/lib/pago/fallido/",
                "pending": "https://tiendaropa-progra4.onrender.com/lib/pago/pendiente/",
            },
            "auto_return": "approved",
        }
        
        print("Creando preferencia...")
        print(f"Preference data: {preference_data}")
        
        preference_response = sdk.preference().create(preference_data)
        print(f"📦 Respuesta Mercado Pago: {preference_response}")
        
        response = preference_response.get("response", {})
        
        # Verificar que tenga ID
        if "id" not in response:
            print(f"❌ Error: no hay ID en response")
            return JsonResponse({
                "error": "Error al crear preferencia",
                "details": str(response)
            }, status=500)
        
        # Buscar init_point
        init_point = response.get("init_point") or response.get("sandbox_init_point")
        
        if init_point:
            print(f"✅ Init point: {init_point}")
            return JsonResponse({
                "init_point": init_point,
                "preference_id": response["id"]
            })
        else:
            print(f"❌ No init_point. Keys: {response.keys()}")
            return JsonResponse({
                "error": "No se encontró init_point",
                "response": str(response)
            }, status=500)
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ EXCEPCIÓN: {str(e)}")
        print(error_trace)
        return JsonResponse({
            "error": str(e),
        }, status=500)
    
    
def remove_from_cart(request, product_id):
    carrito = request.session.get('carrito', {})
    product_id_str = str(product_id)
    
    if product_id_str in carrito:
        del carrito[product_id_str]
        request.session['carrito'] = carrito
        request.session.modified = True
    
    return redirect('view-cart')


def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        libro_id_str = str(product_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad <= 0:
            if libro_id_str in carrito:
                del carrito[libro_id_str]
        else:
            carrito[libro_id_str] = cantidad
        
        request.session['carrito'] = carrito
        request.session.modified = True
    
    return redirect('view-cart')


def clear_cart(request):
    if 'carrito' in request.session:
        del request.session['carrito']
    return redirect('view-cart')


def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Inicializa el SDK de Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    # ------------------ DATOS DE LA PREFERENCIA ------------------
    preference_data = {
        "items": [
            {
                "title": product.title,
                "marca": f"Marca: {product.marca}",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(product.price),
            }
        ],
            "back_urls": {
                "success": request.build_absolute_uri(reverse("pago_exitoso")),
                "failure": request.build_absolute_uri(reverse("pago_fallido")),
                "pending": request.build_absolute_uri(reverse("pago_pendiente")),
            },

    }
    
    # Crea la preferencia de pago
    preference_response = sdk.preference().create(preference_data)
    print("📦 Respuesta Mercado Pago:", preference_response)

    # ------------------ MANEJO DE ERRORES FINAL ------------------
    
    # Capturar el caso donde el SDK falla o retorna un estado de error (ej: 403)
    if 'response' not in preference_response or preference_response.get('status') in [403, 400]:
        error_status = preference_response.get('status', 'N/A')
        error_msg = (f"Error de Credenciales/Acceso (Status: {error_status}). "
                     "Verifica que tu MERCADOPAGO_ACCESS_TOKEN en el archivo .env sea válido.")
        print(error_msg)
        return render(request, "error_pago.html", {"error": error_msg})
        
    response = preference_response.get("response", {})
    
    # Verificar si la respuesta contiene el ID de preferencia
    if "id" not in response:
        error_msg = f"Error al crear preferencia: {response.get('message', 'Error desconocido')}"
        print(error_msg)
        return render(request, "error_pago.html", {"error": error_msg})
    # ------------------- FIN DE MANEJO DE ERRORES -------------------
    
    return render(request, "checkout.html", {
        "product": product,
        "public_key": settings.MERCADOPAGO_PUBLIC_KEY,
        "preference_id": response["id"],
    })


def pago_exitoso(request):
    # Limpiar carrito después del pago exitoso
    if 'carrito' in request.session:
        del request.session['carrito']
    
    payment_id = request.GET.get('payment_id', 'N/A')
    status = request.GET.get('status', 'N/A')
    
    return render(request, 'market/pago_exitoso.html', {
        'payment_id': payment_id,
        'status': status,
    })


def pago_fallido(request):
    return render(request, 'market/pago_fallido.html')


def pago_pendiente(request):
    return render(request, 'pago_pendiente.html')
