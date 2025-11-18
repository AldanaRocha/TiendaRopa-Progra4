from django.shortcuts import render, get_object_or_404
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO
from decimal import Decimal
import fitz  # PyMuPDF

from .models import Presupuesto, PresupuestoItem
from productos.models import Product


# --- Función auxiliar para enviar email ---
def enviar_presupuesto_por_email(presupuesto, pdf_data):
    if not presupuesto.comprador or not presupuesto.comprador.email:
        print(f"Error: Presupuesto {presupuesto.id} no tiene email de comprador.")
        return False

    asunto = f"Tu Presupuesto N° {presupuesto.id}"
    cuerpo = f"Adjuntamos el PDF de tu presupuesto. Total: ${presupuesto.total:,.2f}"

    email = EmailMessage(
        subject=asunto,
        body=cuerpo,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[presupuesto.comprador.email],
    )
    nombre_archivo = f"Presupuesto_{presupuesto.id}.pdf"
    email.attach(nombre_archivo, pdf_data, 'application/pdf')
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


# --- Función para generar PDF ---
def generar_presupuesto_pdf(presupuesto, items):
    # Buscar plantilla de manera dinámica
    plantilla_path = finders.find("pdf/Plantilla_presupuesto.pdf")
    if not plantilla_path:
        raise FileNotFoundError(
            "No se encontró 'pdf/Plantilla_presupuesto.pdf' dentro de STATICFILES"
        )

    pdf = fitz.open(plantilla_path)
    page = pdf[0]

    # === INFO PRINCIPAL ===
    page.insert_text((80, 135), f"{presupuesto.id}", fontsize=15, color=(0, 0, 0))
    page.insert_text((110, 160), f"{presupuesto.fecha.strftime('%d/%m/%Y')}", fontsize=15, color=(0, 0, 0))
    page.insert_text((220, 210), f"{presupuesto.comprador}", fontsize=15, color=(0, 0, 0))

    # === TABLA DE ITEMS ===
    y = 395

    for item in items:
        nombre = (item.producto.title[:32] + "...") if len(item.producto.title) > 32 else item.producto.title
        subtotal = item.precio_unitario * item.cantidad
        page.insert_text((70, y), nombre, fontsize=10, color=(0, 0, 0))
        page.insert_text((280, y), f"{item.cantidad}", fontsize=10, color=(0, 0, 0))
        page.insert_text((400, y), f"${item.precio_unitario:,.2f}", fontsize=10, color=(0, 0, 0))
        page.insert_text((500, y), f"${subtotal:,.2f}", fontsize=10, color=(0, 0, 0))
        y += 30

    # === TOTAL GENERAL ===
    y = 620
    page.insert_text((390, y), f"${presupuesto.total:,.2f}", fontsize=20, color=(0, 0, 0))

    # Guardar en memoria
    buffer = BytesIO()
    pdf.save(buffer)
    pdf.close()
    buffer.seek(0)
    return buffer.getvalue()


# --- Vista principal ---
def generar_presupuesto(request):
    """
    Crea el presupuesto, genera el PDF, envía email y devuelve el PDF como descarga.
    """
    if not request.user.is_authenticated:
        return HttpResponse("Debes iniciar sesión para generar un presupuesto.", status=403)

    carrito = request.session.get('carrito', {})
    if not carrito:
        return HttpResponse("Tu carrito está vacío.", status=400)

    # 1️⃣ Crear Presupuesto
    presupuesto = Presupuesto.objects.create(comprador=request.user)
    total_presupuesto = Decimal('0.00')

    for product_id, cantidad in carrito.items():
        try:
            product = get_object_or_404(Product, id=int(product_id))
            cantidad = int(cantidad)
            precio_unitario = Decimal(str(product.price))
            subtotal = precio_unitario * cantidad

            PresupuestoItem.objects.create(
                presupuesto=presupuesto,
                producto=product,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
            )
            total_presupuesto += subtotal
        except (Product.DoesNotExist, ValueError):
            continue  # Ignorar errores individuales

    # 2️⃣ Guardar total final
    presupuesto.total = total_presupuesto
    presupuesto.save()

    # 3️⃣ Generar PDF
    pdf_data = generar_presupuesto_pdf(presupuesto, presupuesto.items.all())

    # 4️⃣ Enviar email
    enviar_presupuesto_por_email(presupuesto, pdf_data)

    # 5️⃣ Devolver PDF como descarga
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{presupuesto.id}.pdf"'

    # Opcional: limpiar carrito
    if 'carrito' in request.session:
        del request.session['carrito']

    return response
