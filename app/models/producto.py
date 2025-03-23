class Producto:
    def __init__(self, id, nombre, descripcion, precio_compra=0, precio_venta=0, cantidad=1):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_compra = float(precio_compra)
        self.precio_venta = float(precio_venta)
        self.cantidad = cantidad
        
    @property
    def margen(self):
        """Calcula el margen de ganancia en porcentaje"""
        if self.precio_compra <= 0:
            return 0
        return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100

    def actualizar_cantidad(self, nueva_cantidad):
        if nueva_cantidad > 0:
            self.cantidad = nueva_cantidad
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio_compra': self.precio_compra,
            'precio_venta': self.precio_venta,
            'cantidad': self.cantidad
        } 