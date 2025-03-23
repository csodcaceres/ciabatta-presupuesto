import os
import sys
import pandas as pd
import uuid

# Agregar el directorio principal al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.excel_manager import ExcelManager 
from app.controllers.producto_controller import ProductoController

def main():
    print("Agregando ítems a pedidos existentes que no tienen detalles...")
    
    # Inicializar managers y controladores
    excel_manager = ExcelManager()
    producto_controller = ProductoController()
    
    # Leer el archivo Excel de pedidos
    df_pedidos = pd.read_excel(excel_manager.pedidos_file)
    df_detalles = pd.read_excel(excel_manager.pedidos_file, sheet_name='detalles')
    
    # Obtener productos disponibles
    df_productos = producto_controller.obtener_productos()
    if df_productos.empty:
        print("❌ No hay productos disponibles para agregar a los pedidos")
        return
        
    print(f"✅ Se encontraron {len(df_productos)} productos disponibles")
    
    # Obtener IDs únicos de pedidos en la hoja de detalles
    pedidos_con_items = set(df_detalles['pedido_id'].unique())
    
    # Identificar pedidos que no tienen ítems
    pedidos_sin_items = []
    for _, pedido in df_pedidos.iterrows():
        if pedido['id'] not in pedidos_con_items:
            pedidos_sin_items.append(pedido['id'])
    
    if not pedidos_sin_items:
        print("✅ Todos los pedidos ya tienen ítems asociados")
        return
        
    print(f"🔍 Se encontraron {len(pedidos_sin_items)} pedidos sin ítems: {pedidos_sin_items}")
    
    # Agregar ítems a pedidos sin detalles
    nuevos_detalles = []
    for pedido_id in pedidos_sin_items:
        print(f"📝 Agregando ítems al pedido {pedido_id}")
        
        # Obtener el pedido
        pedido_row = df_pedidos[df_pedidos['id'] == pedido_id].iloc[0]
        total_pedido = pedido_row['total']
        
        # Seleccionar productos aleatorios para asignar al pedido
        productos_seleccionados = df_productos.sample(min(2, len(df_productos))).to_dict('records')
        
        # Si solo hay un producto, asignar todo el total a ese producto
        if len(productos_seleccionados) == 1:
            producto = productos_seleccionados[0]
            cantidad = max(1, int(total_pedido / producto['precio_venta']))
            subtotal = cantidad * producto['precio_venta']
            
            detalle = {
                'pedido_id': pedido_id,
                'producto_id': producto['id'],
                'cantidad': cantidad,
                'precio_unitario': producto['precio_venta'],
                'subtotal': subtotal,
                'descripcion': producto['nombre'],
                'descuento': 0,
                'id': 1
            }
            nuevos_detalles.append(detalle)
            print(f"  ➕ Agregado: {detalle['descripcion']}, Cantidad: {detalle['cantidad']}")
            
        # Si hay múltiples productos, distribuir el total entre ellos
        else:
            # Distribuir el total entre los productos
            total_restante = total_pedido
            for i, producto in enumerate(productos_seleccionados):
                # El último producto recibe todo el resto
                if i == len(productos_seleccionados) - 1:
                    precio = producto['precio_venta']
                    cantidad = max(1, int(total_restante / precio))
                    subtotal = min(total_restante, cantidad * precio)
                else:
                    # Para productos anteriores, asignar un porcentaje del total
                    porcentaje = 0.6 if i == 0 else 0.4
                    subtotal = total_restante * porcentaje
                    precio = producto['precio_venta']
                    cantidad = max(1, int(subtotal / precio))
                    subtotal = cantidad * precio
                    total_restante -= subtotal
                
                detalle = {
                    'pedido_id': pedido_id,
                    'producto_id': producto['id'],
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'subtotal': subtotal,
                    'descripcion': producto['nombre'],
                    'descuento': 0,
                    'id': i + 1
                }
                nuevos_detalles.append(detalle)
                print(f"  ➕ Agregado: {detalle['descripcion']}, Cantidad: {detalle['cantidad']}")
    
    # Añadir los nuevos detalles al DataFrame
    df_detalles_actualizado = pd.concat([df_detalles, pd.DataFrame(nuevos_detalles)], ignore_index=True)
    
    # Guardar cambios en el archivo Excel
    with pd.ExcelWriter(excel_manager.pedidos_file, engine='openpyxl') as writer:
        df_pedidos.to_excel(writer, index=False, sheet_name='Sheet1')
        df_detalles_actualizado.to_excel(writer, index=False, sheet_name='detalles')
    
    print(f"✅ Se agregaron ítems a {len(pedidos_sin_items)} pedidos correctamente")
    print(f"📊 Total de ítems en la hoja de detalles ahora: {len(df_detalles_actualizado)}")
    print("=== Fin del proceso ===")

if __name__ == "__main__":
    main() 