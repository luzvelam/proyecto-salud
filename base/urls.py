from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# Importación de vistas adicionales
from .views import cerrar_sesion, buscar_producto, actualizar_inventario, eliminar_producto, reportar_error

urlpatterns = [
    path('index', views.index, name="index"),  # Página principal
    path('index', views.index, name='index'),
    path('', views.login, name="login"),  # Ruta para login
    path('reporte/', views.reporte_view, name='reporte'),  # Ruta para la vista de reporte
    path('registrar/', views.registrar_usuario, name='registrar'),  # Ruta para registro de usuario
    path('AgregarInventario/', views.agregar_inventario, name='agregar_inventario'),  # Ruta para agregar inventario
    path('ActualizarInventario/', views.actualizar_inventario, name='actualizar_inventario'),  # Ruta para actualizar inventario
    path('EliminarInventario/', views.eliminar_inventario, name='eliminar_inventario'),  # Ruta para eliminar inventario
    path('ListarInventario/', views.listar_inventario, name='listar_inventario'),  # Ruta para listar inventarios
    path('AgregarEnvio/', views.agregar_envio, name='agregar_envio'),  # Ruta para agregar un envío
    path('ActualizarEnvio/', views.actualizar_envio, name='actualizar_envio'),  # Ruta para actualizar un envío
    path('mercado_pago/', views.mercado_pago, name='mercado_pago'),  # Ruta para MercadoPago
    # path('ListarEnvios/', views.listar_envios, name='listar_envios'),  # Ruta comentada (comentada o eliminada porque ya se ha agregado más abajo)
    path('crear-preferencia/', views.crear_preferencia, name='crear_preferencia'),
    
    # Ruta para cerrar sesión
    path('logout/', cerrar_sesion, name='logout'),
    
    # Ruta para eliminar un envío
    path('EliminarEnvio/<str:id_orden>/', views.eliminar_envio, name='eliminar_envio'),

    # Ruta para listar todos los envíos
    path('listar_envios/', views.listar_envios, name='listar_envios'),  

    # Funcionalidad de Base de Datos (productos)
    path('Agregar_Producto/', views.agregar_producto, name='Agregar_Producto'),  # Ruta para agregar productos
    path('buscar_producto/<int:id>/', buscar_producto, name='buscar_producto'),  # Ruta para buscar productos por ID
    path('actualizar_inventario/', actualizar_inventario, name='actualizar_inventario'),  # Ruta para actualizar inventario
    path('eliminar_producto/', eliminar_producto, name='eliminar_producto'),  # Ruta para eliminar un producto
    # path('EliminarEnvio/<str:id_orden>/', views.eliminar_envio, name='eliminar_envio'),  # Eliminada porque ya está incluida arriba

    # Logs de Errores (ruta para reportar errores)
    path('reportar-error/', reportar_error, name='reportar_error'),

    # Validación de pagos (MercadoPago)
    path('validar_pago/', views.validar_pago, name='validar_pago'),  # Ruta para validar el pago

    # Nuevas rutas agregadas para MercadoPago
    path('crear-preferencia/', views.crear_preferencia, name='crear_preferencia'),  # Ruta para crear preferencia en MercadoPago
    path('notificacion-pago/', views.notificacion_pago, name='notificacion_pago'),  # Ruta para recibir notificaciones de pago
]
