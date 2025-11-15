from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO
from decimal import Decimal # Importar Decimal para cálculos precisos
import fitz # PyMuPDF
from .models import Presupuesto, PresupuestoItem
from productos.models import Product
from django.shortcuts import get_object_or_404 # Para manejo seguro de Product.objects.get


# --- Función auxiliar (debes tenerla definida si quieres usarla) ---
def enviar_presupuesto_por_email(presupuesto, pdf_data):
    # Lógica para enviar el email... (función provista en respuestas anteriores)
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


# --- Tu función de generación de PDF (sin cambios, asumiendo que funciona) ---
def generar_presupuesto_pdf(presupuesto, items):
    plantilla_path = settings.BASE_DIR / "core/static/pdf/plantilla_presupuesto.pdf"
    pdf = fitz.open(plantilla_path)
    page = pdf[0]

    # === INFO PRINCIPAL ===
    page.insert_text((80, 135), f" {presupuesto.id}", fontsize=15, color=(0,0,0))
    page.insert_text((110, 160), f" {presupuesto.fecha.strftime('%d/%m/%Y')}", fontsize=15, color=(0,0,0))
    page.insert_text((220,210), f" {presupuesto.comprador}", fontsize=15 , color=(0,0,0))

    # === TABLA ===
    y = 395
    
    for item in items:
        nombre = (item.producto.title[:32] + "...") if len(item.producto.title) > 32 else item.producto.title

        page.insert_text((70, y), nombre, fontsize=10, color=(0,0,0))
        page.insert_text((280, y), f"{item.cantidad}", fontsize=10, color=(0,0,0))
        page.insert_text((400, y), f"${item.precio_unitario:,.2f}", fontsize=10, color=(0,0,0))
        page.insert_text((500, y), f"${item.subtotal:,.2f}", fontsize=10, color=(0,0,0))

        y += 30  # bajar a la siguiente fila

    # === TOTAL GENERAL ===
    y = 620  # un poco de espacio antes del total
    page.insert_text(
        (390, y),
        f"${presupuesto.total:,.2f}",
        fontsize=20,
        color=(0,0,0)
    )

    buffer = BytesIO()
    pdf.save(buffer)
    pdf.close()
    buffer.seek(0)
    return buffer.getvalue()



# --- Vista Principal (Modificada) ---
def generar_presupuesto(request):
    """
    Crea el Presupuesto, genera el PDF, lo envía por email (si aplica) y lo descarga.
    """
    if not request.user.is_authenticated:
        # Los presupuestos deben ser de usuarios identificados para tener un email de destino.
        return HttpResponse("Debes iniciar sesión para generar un presupuesto.", status=403)
        
    carrito = request.session.get('carrito', {})
    if not carrito:
        return HttpResponse("Tu carrito está vacío.", status=400)

    # 1. CREAR EL PRESUPUESTO
    presupuesto = Presupuesto.objects.create(
        comprador=request.user,
    )

    total_presupuesto = Decimal('0.00')
    
    for product_id, cantidad in carrito.items():
        try:
            # Uso de get_object_or_404 (aunque solo fallaría si el ID es incorrecto)
            product = get_object_or_404(Product, id=int(product_id))
            cantidad = int(cantidad)

            # 🛠️ CÁLCULO SEGURO: Convertir el precio a Decimal antes de calcular
            precio_unitario = Decimal(str(product.price)) 
            subtotal = precio_unitario * cantidad
            
            PresupuestoItem.objects.create(
                presupuesto=presupuesto,
                producto=product,
                cantidad=cantidad,
                precio_unitario=precio_unitario, # Ya es Decimal
            )
            total_presupuesto += subtotal
            
        except Product.DoesNotExist:
            # Opcional: Loggear o manejar productos que ya no existen.
            continue 
        except ValueError:
            # Opcional: Manejar si la cantidad no es un número válido.
            continue
            
    # 2. GUARDAR EL TOTAL FINAL
    presupuesto.total = total_presupuesto
    presupuesto.save()

    # 3. GENERAR PDF
    pdf_data = generar_presupuesto_pdf(presupuesto, presupuesto.items.all())

    # 4. ENVIAR EMAIL
    # Se recomienda enviar el email ANTES de la descarga
    email_enviado = enviar_presupuesto_por_email(presupuesto, pdf_data)
    
    # 5. DEVOLVER PDF COMO DESCARGA
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{presupuesto.id}.pdf"'
    
    # Opcional: Puedes borrar el carrito de la sesión después de generar el presupuesto
    del request.session['carrito']
    
    return response
