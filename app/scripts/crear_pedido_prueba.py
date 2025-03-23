import sys
import os
import uuid
import pandas as pd
from datetime import datetime

# Añadir el directorio raíz al path para poder importar los módulos
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from app.models.pedido import Pedido, ItemPedido
from app.controllers.pedido_controller import PedidoController
from app.controllers.producto_controller import ProductoController
from app.utils.excel_manager import ExcelManager

def main():
    print("=== Creando pedido de prueba ===")
    
    # Inicializar los controladores
    pedido_controller = PedidoController()  # No recibe parámetros
    producto_controller = ProductoController()  # Asumimos constructor similar
    
    # Obtener productos para añadir al pedido
    productos = producto_controller.obtener_productos()
    if productos.empty:
        print("No hay productos disponibles. Creando productos de ejemplo...")
        # Aquí podrías crear productos de ejemplo si fuera necesario
    
    print(f"Se encontraron {len(productos)} productos")
    
    # Generar ID único para el pedido
    pedido_id = str(uuid.uuid4())[:8]
    
    # Crear items para el pedido
    items = []
    for i, producto in productos.iterrows():
        if i >= 2:  # Limitar a los primeros 2 productos
            break
            
        precio = producto['precio_venta'] if not pd.isna(producto['precio_venta']) else 0
        cantidad = i + 1  # Cantidad progresiva: 1, 2, ...
        descuento = i * 5  # Descuento progresivo: 0%, 5%, ...
        
        item = ItemPedido(
            id=i+1,
            producto_id=producto['id'],
            descripcion=producto['nombre'],
            cantidad=cantidad,
            precio_unitario=precio,
            descuento=descuento
        )
        
        items.append(item)
        print(f"Item {i+1}: {producto['nombre']}, Cantidad: {cantidad}, Precio: {precio}, Descuento: {descuento}%")
    
    # Crear el pedido
    pedido = Pedido(
        id=pedido_id,
        cliente_id=1742743163,  # ID de cliente existente
        fecha=datetime.now().strftime('%Y-%m-%d'),
        estado="Pendiente",
        items=items,
        notas="Pedido de prueba creado desde script"
    )
    
    # Calcular total
    pedido.calcular_total()
    print(f"Total del pedido: ${pedido.total}")
    
    # Guardar pedido
    resultado = pedido_controller.crear_pedido(pedido)
    
    if resultado:
        print(f"Pedido creado correctamente con ID: {resultado.id}")
        print(f"Número de items guardados: {len(resultado.items)}")
    else:
        print("Error al crear el pedido")
    
    # Verificar que el pedido se guardó correctamente
    try:
        # Referencia al excel_manager a través del controlador
        excel_manager = pedido_controller.excel_manager
        
        # Leer el archivo Excel para verificar
        df_pedidos = pd.read_excel(excel_manager.pedidos_file)
        df_detalles = pd.read_excel(excel_manager.pedidos_file, sheet_name='detalles')
        
        # Verificar pedido
        pedido_df = df_pedidos[df_pedidos['id'] == pedido_id]
        if not pedido_df.empty:
            print(f"✅ Pedido encontrado en Excel con ID: {pedido_id}")
        else:
            print(f"❌ Pedido NO encontrado en Excel")
            
        # Verificar items
        items_df = df_detalles[df_detalles['pedido_id'] == pedido_id]
        if not items_df.empty:
            print(f"✅ Se encontraron {len(items_df)} items para el pedido en Excel")
            print("Primeros items:")
            print(items_df.head())
        else:
            print(f"❌ NO se encontraron items para el pedido en Excel")
            
        # Mostrar todos los IDs de pedido en la hoja de detalles
        pedido_ids_detalles = df_detalles['pedido_id'].unique()
        print(f"IDs de pedido en la hoja de detalles: {pedido_ids_detalles}")
            
    except Exception as e:
        print(f"Error al verificar datos en Excel: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=== Fin del proceso ===")

if __name__ == "__main__":
    main() 