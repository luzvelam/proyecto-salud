import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
import os
import mercadopago


from .models import Inventario, Envio, EnvioProducto, Orders, Payments
from .models import Envio  # O el modelo que corresponda

def listar_envios(request):
    envios = Envio.objects.all()  # Obtén los envíos desde la base de datos
    return render(request, 'listar_envios.html', {'envios': envios})

def mercado_pago(request):
    return render(request, 'mercado_pago.html')


def index(request):
    return render(request, 'index.html')

# Vistas relacionadas con el pago
def crear_preferencia(request):
    if request.method == "POST":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        preference_data = {
            "items": [
                {
                    "title": "Consulta Médica",  # Cambia según el servicio/producto
                    "quantity": 1,
                    "currency_id": "MXN",
                    "unit_price": 500.00  # Cambia al precio que manejes
                }
            ],
            "back_urls": {
                "success": "http://tusitio.com/pago-exitoso/",
                "failure": "http://tusitio.com/pago-fallido/",
                "pending": "http://tusitio.com/pago-pendiente/"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        return JsonResponse({"preference_id": preference["id"]})

    return JsonResponse({"error": "Método no permitido"}, status=405)


def validar_pago(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Datos del pago
        token = data.get('token')
        amount = data.get('transaction_amount')
        description = data.get('description')
        installments = data.get('installments')
        payer_email = data['payer']['email']

        # Inicializar MercadoPago
        mp = mercado_pago.MercadoPago()
        payment = mp.payment.create({
            "transaction_amount": amount,
            "token": token,
            "description": description,
            "installments": installments,
            "payer": {
                "email": payer_email
            }
        })

        # Verificar si el pago fue aprobado
        if payment['status'] == 'approved':
            # Crear el registro de pago en la base de datos
            order = Orders.objects.get(id=data['order_id'])
            new_payment = Payments.objects.create(
                order=order,
                monto=amount,
                metodo_pago="MercadoPago",
                estado_pago="Aprobado",
                referencia_pago=payment['id']
            )
            return JsonResponse({"status": "approved", "message": "Pago exitoso", "payment_id": new_payment.id})
        else:
            return JsonResponse({"status": "failed", "message": payment['message']})

    return JsonResponse({"status": "error", "message": "Método no permitido"})

def notificacion_pago(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get("data.id")
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

            payment = sdk.payment().get(payment_id)

            if payment["response"]["status"] == "approved":
                return JsonResponse({"success": True, "message": "Pago aprobado."})

            return JsonResponse({"success": False, "message": "El pago no está aprobado."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"error": "Método no permitido"}, status=405)

# Vistas relacionadas con la autenticación y gestión de usuarios
User = get_user_model()

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('index')  # Redirige correctamente
        else:
            messages.error(request, 'Credenciales incorrectas.')
    
    return render(request, "login.html")


def registrar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        password = request.POST['password']
        
        user = User.objects.create_user(
            username=email,
            email=email, 
            first_name=nombre, 
            password=password
        )
        
        messages.success(request, 'Usuario registrado exitosamente.')
        return redirect('login')  

    return render(request, 'registrar.html')    


def cerrar_sesion(request):
    logout(request)
    return redirect('login') 

@login_required
def reporte_view(request):
    return render(request, 'reporte.html') 

@login_required
def agregar_inventario(request):
    return render(request, 'agregar_inventario.html') 

@login_required
def actualizar_inventario(request):
    return render(request, 'actualizar_inventario.html') 

@login_required
def eliminar_inventario(request):
    return render(request, 'eliminar_inventario.html') 

@login_required
def listar_inventario(request):
    return render(request, 'listar_inventario.html') 

@login_required
def agregar_envio(request):
    if request.method == 'POST':
        id_orden = request.POST.get('id_orden')
        fecha_envio = request.POST.get('fecha_envio')
        fecha_estimada_llegada = request.POST.get('fecha_estimada_llegada')
        direccion_entrega = request.POST.get('direccion_entrega')
        nombre_destinatario = request.POST.get('nombre_destinatario')
        costo_envio = request.POST.get('costo_envio')
        transportista = request.POST.get('transportista')

        productos_ids = request.POST.getlist('productos')
        cantidades = request.POST.getlist('cantidades')

        precio_total = 0
        productos = []

        for i, producto_id in enumerate(productos_ids):
            cantidad = int(cantidades[i])

            if cantidad > 0:
                producto = get_object_or_404(Inventario, id=producto_id)

                if producto.stock >= cantidad:
                    productos.append((producto, cantidad))
                    precio_total += producto.precio * cantidad
                else:
                    messages.error(request, f"No hay suficiente stock para {producto.nombre}. Stock actual: {producto.stock}")
                    return redirect('agregar_envio')

        if productos:
            nuevo_envio = Envio(
                id_orden=id_orden,
                fecha_envio=fecha_envio,
                fecha_estimada_llegada=fecha_estimada_llegada,
                precio_total=precio_total,
                estado_entrega='Pendiente',
                direccion_entrega=direccion_entrega,
                nombre_destinatario=nombre_destinatario,
                costo_envio=costo_envio,
                transportista=transportista
            )
            nuevo_envio.save()

            for producto, cantidad in productos:
                EnvioProducto.objects.create(envio=nuevo_envio, producto=producto, cantidad=cantidad)
                producto.stock -= cantidad
                producto.save()

            messages.success(request, "Envío registrado exitosamente.")
            return redirect('listar_envios')
        else:
            messages.error(request, "No se han seleccionado productos válidos.")
            return redirect('agregar_envio')

    productos = Inventario.objects.all()
    return render(request, 'agregar_envio.html', {'productos': productos})

@login_required
def actualizar_envio(request):
    if request.method == 'POST':
        id_orden = request.POST.get('id_orden')
        fecha_estimada_llegada = request.POST.get('fecha_estimada_llegada')
        direccion_entrega = request.POST.get('direccion_entrega')
        nombre_destinatario = request.POST.get('nombre_destinatario')
        costo_envio = request.POST.get('costo_envio')
        transportista = request.POST.get('transportista')
        estado_entrega = request.POST.get('estado_entrega')

        envio = get_object_or_404(Envio, id_orden=id_orden)
        envio.fecha_estimada_llegada = fecha_estimada_llegada
        envio.direccion_entrega = direccion_entrega
        envio.nombre_destinatario = nombre_destinatario
        envio.costo_envio = costo_envio
        envio.transportista = transportista
        envio.estado_entrega = estado_entrega
        envio.save()

        messages.success(request, "Envío actualizado exitosamente.")
        return redirect('listar_envios')

    elif request.method == 'GET' and 'id_orden' in request.GET:
        id_orden = request.GET['id_orden']
        envio = get_object_or_404(Envio, id_orden=id_orden)
        return render(request, 'actualizar_envio.html', {'envio': envio})

    return render(request, 'actualizar_envio.html')

# Funciones adicionales de gestión de inventarios
def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
  
        producto = Inventario(
            nombre=nombre,
            descripcion=descripcion,
            categoria=categoria,
            precio=precio,
            stock=stock
        )
        producto.save()

        messages.success(request, "Producto registrado exitosamente.")
        return redirect('Agregar_Producto')

    return render(request, 'agregar_inventario.html')

def listar_inventario(request):
    productos = Inventario.objects.all().order_by('id')
    return render(request, 'listar_inventario.html', {'productos': productos})

def buscar_producto(request, id):
    producto = get_object_or_404(Inventario, id=id)
    data = {
        'nombre': producto.nombre,
        'descripcion': producto.descripcion,
        'categoria': producto.categoria,
        'precio': str(producto.precio),
        'stock': producto.stock,
    }
    return JsonResponse(data)

def actualizar_inventario(request):
    if request.method == 'POST':
        buscar_id = request.POST.get('buscar_id')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        categoria = request.POST.get('categoria')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')

        producto = get_object_or_404(Inventario, id=buscar_id)
        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.categoria = categoria
        producto.precio = precio
        producto.stock = stock
        producto.save()

        messages.success(request, "Producto actualizado exitosamente.")
        return redirect('actualizar_inventario')

    return render(request, 'actualizar_inventario.html')

def eliminar_producto(request):
    if request.method == 'POST':
        buscar_id = request.POST.get('buscar_id')
        producto = get_object_or_404(Inventario, id=buscar_id)
        producto.delete()

        messages.success(request, "Producto eliminado exitosamente.")
        return redirect('eliminar_inventario')

    return render(request, 'eliminar_inventario.html')

def reportar_error(request):
    # Lógica para manejar los errores
    return render(request, 'error.html')  # Modifica según tu lógica

@login_required
def eliminar_envio(request, id_orden):
    envio = get_object_or_404(Envio, id_orden=id_orden)
    
    if request.method == 'POST':
        envio.delete()
        messages.success(request, "Envío eliminado exitosamente.")
        return redirect('listar_envios')

    return render(request, 'confirmar_eliminacion.html', {'envio': envio})

def crear_preferencia(request):
    if request.method == "POST":
        # Inicializar MercadoPago SDK con tu access token
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        sdk.set_config('sandbox', True)  # Asegúrate de que esté en modo sandbox para pruebas


        # Datos de la preferencia (productos, precios, URLs de retorno)
        preference_data = {
            "items": [
                {
                    "title": "Producto Médico",  # Cambia esto por el nombre del producto
                    "quantity": 1,
                    "currency_id": "MXN",  # O la moneda correspondiente
                    "unit_price": 500.00  # Precio del producto
                }
            ],
            "back_urls": {
                "success": "https://tusitio.com/pago-exitoso/",  # Cambia estas URLs según tus necesidades
                "failure": "https://tusitio.com/pago-fallido/",
                "pending": "https://tusitio.com/pago-pendiente/"
            },
            "auto_return": "approved",  # Define la acción que tomará el sistema cuando el pago sea aprobado
            "payment_methods": {
                "excluded_payment_types": [
                    {
                        "id": "ticket"
                    }
                ]
            }
        }

        # Crear la preferencia
        preference_response = sdk.preference().create(preference_data)
        
        # Verifica que la preferencia se haya creado exitosamente
        if preference_response["status"] != 201:
            return JsonResponse({"error": "Error al crear la preferencia", "details": preference_response}, status=400)

        preference = preference_response["response"]
        
        # Retornar el ID de la preferencia al frontend para redirigir al usuario
        return JsonResponse({"preference_id": preference["id"]})

    return JsonResponse({"error": "Método no permitido"}, status=405)



