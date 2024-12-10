from django.db import models
from django.contrib.auth.models import AbstractUser

class Inventario(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.nombre
    
class Envio(models.Model):
    id_orden = models.CharField(max_length=50, unique=True)
    fecha_envio = models.DateField()
    fecha_estimada_llegada = models.DateField()
    productos = models.ManyToManyField(Inventario, through='EnvioProducto')
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_entrega = models.CharField(max_length=50)
    direccion_entrega = models.TextField()
    nombre_destinatario = models.CharField(max_length=100)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2)
    transportista = models.CharField(max_length=100)

    def __str__(self):
        return f"Envio {self.id_orden}"

class EnvioProducto(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    producto = models.ForeignKey(Inventario, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} de {self.producto.nombre} en Envío {self.envio.id_orden}"
    

class Usuarios(AbstractUser):
    # Campos adicionales que quieras agregar
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Añade related_name para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_usuarios_groups',
        blank=True,
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_usuarios_permissions',
        blank=True,
        verbose_name='user permissions'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
        
class Hospitales(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100, null=True, blank=True)
    pais = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Categorias(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class Medications(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    categoria = models.CharField(max_length=50, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    tiempo_produccion = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class Orders(models.Model):
    hospital = models.ForeignKey(Hospitales, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20)
    tiempo_estimado_entrega = models.IntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    prioridad = models.CharField(max_length=20, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id}"

class OrderItems(models.Model):
    order = models.ForeignKey(Orders, related_name='items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medications, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.medication.nombre}"

class Payments(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50)
    estado_pago = models.CharField(max_length=20)
    referencia_pago = models.CharField(max_length=100, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order_id}"

class Shipments(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_estimada_llegada = models.DateTimeField(null=True, blank=True)
    proveedor_envio = models.CharField(max_length=50, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=20, null=True, blank=True)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment for Order {self.order_id}"

class StockHistory(models.Model):
    medication = models.ForeignKey(Medications, on_delete=models.CASCADE)
    cambio_stock = models.IntegerField()
    razon = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stock change for {self.medication.nombre}"

class Discounts(models.Model):
    medication = models.ForeignKey(Medications, on_delete=models.CASCADE)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Discount for {self.medication.nombre}"

class PurchaseHistory(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20)

    def __str__(self):
        return f"Purchase for User {self.usuario_id}"

class Roles(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

class AuditLogs(models.Model):
    tabla = models.CharField(max_length=50)
    operacion = models.CharField(max_length=50)
    usuario = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    datos_anteriores = models.JSONField(null=True, blank=True)
    datos_nuevos = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.operacion} on {self.tabla}"


class Notifications(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for User {self.usuario_id}"