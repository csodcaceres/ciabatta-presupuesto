import sys
import os
import uuid
import traceback

# Añadir la ruta del directorio padre para importar los módulos correctamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from controllers.producto_controller import ProductoController
    from models.producto import Producto
    
    def crear_productos_prueba():
        """Crea productos de prueba en la base de datos"""
        print("Iniciando creación de productos de prueba...")
        
        controller = ProductoController()
        productos_actuales = controller.obtener_productos()
        
        if not productos_actuales.empty:
            print(f"Ya existen {len(productos_actuales)} productos en el sistema.")
            print("Columnas disponibles:", productos_actuales.columns.tolist())
            print("Primeros productos:", productos_actuales.head().to_dict('records'))
            return
        
        print("No se encontraron productos. Creando productos de prueba...")
        
        # Lista de productos a crear
        productos = [
            Producto(
                id=str(uuid.uuid4()),
                nombre="Pan Ciabatta",
                descripcion="Pan Ciabatta tradicional",
                precio_compra=1.5,
                precio_venta=3.0
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Pan Francés",
                descripcion="Pan Francés clásico",
                precio_compra=0.8,
                precio_venta=2.0
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Pan Integral",
                descripcion="Pan Integral de semillas",
                precio_compra=1.2,
                precio_venta=2.5
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Facturas",
                descripcion="Facturas de manteca (docena)",
                precio_compra=3.0,
                precio_venta=6.0
            ),
            Producto(
                id=str(uuid.uuid4()),
                nombre="Medialuna",
                descripcion="Medialunas de manteca (unidad)",
                precio_compra=0.25,
                precio_venta=0.5
            )
        ]
        
        # Guardar cada producto
        for producto in productos:
            print(f"Guardando producto: {producto.nombre}")
            controller.guardar_producto(producto)
        
        # Verificar que se hayan guardado
        productos_nuevos = controller.obtener_productos()
        print(f"Se crearon {len(productos_nuevos)} productos exitosamente")
        print("Columnas disponibles:", productos_nuevos.columns.tolist())
        print("Productos creados:", productos_nuevos.to_dict('records'))
    
    if __name__ == "__main__":
        crear_productos_prueba()
        
except Exception as e:
    print(f"Error: {str(e)}")
    traceback.print_exc() 