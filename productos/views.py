from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.http import HttpResponse
import mercadopago
from django.conf import settings



@login_required
def product_list(request):
    products = Product.objects.filter(active=True).order_by("-created_at")
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


def checkout(request, product_id):
    product= get_object_or_404(Product, id=product_id)

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": product.title,
                "description": f"Descripción: {product.description}",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(product.price),
            }
        ],
        "back_urls": {
            "success": "http://localhost:8000/pago/exitoso/",
            "failure": "http://localhost:8000/pago/fallido/",
            "pending": "http://localhost:8000/pago/pendiente/",
        },
        # "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    print("📦 Respuesta Mercado Pago:", preference_response)

    response = preference_response.get("response", {})
    if "id" not in response:
        return render(request, "error_pago.html", {"error": response})

    return render(request, "checkout.html", {
        "product": product,
        "public_key": settings.MERCADOPAGO_PUBLIC_KEY,
        "preference_id": response["id"],
    })





def pago_exitoso(request):
    return HttpResponse("✅ Pago exitoso. ¡Gracias por tu compra!")

def pago_fallido(request):
    return HttpResponse("❌ Hubo un error con el pago.")

def pago_pendiente(request):
    return HttpResponse("⏳ El pago está pendiente de aprobación.")