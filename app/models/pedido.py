class ItemPedido:
    """Representa un ítem o línea en un pedido"""
    
    def __init__(self, id, producto_id, descripcion, cantidad, precio_unitario, descuento=0):
        self.id = id
        self.producto_id = producto_id
        self.descripcion = descripcion
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario
        self.descuento = descuento
        self.subtotal = self.calcular_subtotal()
    
    def calcular_subtotal(self):
        """Calcula el subtotal del ítem aplicando el descuento"""
        precio_con_descuento = self.precio_unitario * (1 - self.descuento / 100)
        return self.cantidad * precio_con_descuento
    
    def actualizar_cantidad(self, cantidad):
        """Actualiza la cantidad del ítem y recalcula el subtotal"""
        self.cantidad = cantidad
        self.subtotal = self.calcular_subtotal()
    
    def actualizar_precio(self, precio):
        """Actualiza el precio unitario y recalcula el subtotal"""
        self.precio_unitario = precio
        self.subtotal = self.calcular_subtotal()
    
    def actualizar_descuento(self, descuento):
        """Actualiza el descuento y recalcula el subtotal"""
        self.descuento = descuento
        self.subtotal = self.calcular_subtotal()
    
    def to_dict(self):
        """Convierte el ítem a un diccionario"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'descuento': self.descuento,
            'subtotal': self.subtotal
        }


class Pedido:
    def __init__(self, id, cliente_id=None, fecha=None, estado='Pendiente', items=None, notas=None, total=None):
        self.id = id
        self.cliente_id = cliente_id
        self.fecha = fecha
        self.estado = estado
        self.items = items if items else []
        self.notas = notas
        self.total = total if total is not None else self.calcular_total()

    def calcular_total(self):
        """Calcula el total del pedido sumando los subtotales de los items"""
        if not self.items:
            return 0
        return sum(item.subtotal for item in self.items)

    def agregar_item(self, item):
        """Agrega un item al pedido y recalcula el total"""
        self.items.append(item)
        self.total = self.calcular_total()

    def eliminar_item(self, item_id):
        """Elimina un item del pedido y recalcula el total"""
        self.items = [item for item in self.items if item.id != item_id]
        # Reindexar IDs
        for i, item in enumerate(self.items):
            item.id = i + 1
        self.total = self.calcular_total()

    def actualizar_estado(self, nuevo_estado):
        """Actualiza el estado del pedido"""
        estados_validos = ['Pendiente', 'En proceso', 'Completado', 'Cancelado']
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            return True
        return False

    def to_dict(self):
        """Convierte el pedido a un diccionario"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'fecha': self.fecha,
            'estado': self.estado,
            'items': [item.to_dict() for item in self.items],
            'notas': self.notas,
            'total': self.total
        } 