import datetime

class Presupuesto:
    def __init__(self, id, cliente, fecha=None, validez=15, items=None, total=None, notas=None):
        self.id = id
        self.cliente = cliente
        self.fecha = fecha if fecha else datetime.datetime.now().strftime("%d/%m/%Y")
        self.validez = validez  # Días de validez del presupuesto
        self.items = items if items else []
        self.total = total if total else self.calcular_total()
        self.notas = notas
        self.estado = 'pendiente'  # pendiente, aceptado, rechazado, vencido
    
    def calcular_total(self):
        """Calcula el total del presupuesto sumando todos los ítems"""
        if not self.items:
            return 0
        return sum(item.subtotal for item in self.items)
    
    def agregar_item(self, item):
        """Agrega un ítem al presupuesto y recalcula el total"""
        self.items.append(item)
        self.total = self.calcular_total()
    
    def eliminar_item(self, item_id):
        """Elimina un ítem del presupuesto por su ID y recalcula el total"""
        self.items = [item for item in self.items if item.id != item_id]
        self.total = self.calcular_total()
    
    def cambiar_estado(self, nuevo_estado):
        """Cambia el estado del presupuesto"""
        estados_validos = ['pendiente', 'aceptado', 'rechazado', 'vencido']
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            return True
        return False
    
    def esta_vigente(self):
        """Verifica si el presupuesto aún está vigente"""
        if self.estado != 'pendiente':
            return False
            
        # Convertir fecha de presupuesto a objeto datetime
        try:
            partes = self.fecha.split('/')
            fecha_presupuesto = datetime.datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            fecha_vencimiento = fecha_presupuesto + datetime.timedelta(days=self.validez)
            return datetime.datetime.now() <= fecha_vencimiento
        except:
            return False
    
    def to_dict(self):
        """Convierte el presupuesto a un diccionario para almacenamiento"""
        return {
            'id': self.id,
            'cliente_id': self.cliente.id if hasattr(self.cliente, 'id') else self.cliente,
            'fecha': self.fecha,
            'validez': self.validez,
            'total': self.total,
            'notas': self.notas,
            'estado': self.estado
        }


class ItemPresupuesto:
    def __init__(self, id, descripcion, cantidad, precio_unitario, descuento=0):
        self.id = id
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.descuento = descuento  # Porcentaje de descuento
        self.subtotal = self.calcular_subtotal()
    
    def calcular_subtotal(self):
        """Calcula el subtotal del ítem considerando cantidad, precio y descuento"""
        subtotal = self.cantidad * self.precio_unitario
        if self.descuento > 0:
            subtotal -= subtotal * (self.descuento / 100)
        return subtotal
    
    def actualizar_cantidad(self, nueva_cantidad):
        """Actualiza la cantidad del ítem y recalcula el subtotal"""
        if nueva_cantidad > 0:
            self.cantidad = nueva_cantidad
            self.subtotal = self.calcular_subtotal()
            return True
        return False
    
    def actualizar_precio(self, nuevo_precio):
        """Actualiza el precio unitario del ítem y recalcula el subtotal"""
        if nuevo_precio > 0:
            self.precio_unitario = nuevo_precio
            self.subtotal = self.calcular_subtotal()
            return True
        return False
    
    def actualizar_descuento(self, nuevo_descuento):
        """Actualiza el descuento del ítem y recalcula el subtotal"""
        if 0 <= nuevo_descuento <= 100:
            self.descuento = nuevo_descuento
            self.subtotal = self.calcular_subtotal()
            return True
        return False
    
    def to_dict(self):
        """Convierte el ítem a un diccionario para almacenamiento"""
        return {
            'id': self.id,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'descuento': self.descuento,
            'subtotal': self.subtotal
        } 