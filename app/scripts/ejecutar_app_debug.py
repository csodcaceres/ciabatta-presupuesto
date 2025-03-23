import os
import sys
import traceback
import logging
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Agregar el directorio raíz al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir))

print("Iniciando aplicación en modo debug...")
print(f"Python path: {sys.path}")
print(f"Directorio actual: {os.getcwd()}")
print(f"Directorio app: {os.path.join(root_dir, 'app')} (existe: {os.path.exists(os.path.join(root_dir, 'app'))})")
print(f"Directorio data: {os.path.join(root_dir, 'data')} (existe: {os.path.exists(os.path.join(root_dir, 'data'))})")

def crear_pedido_prueba():
    """
    Crea un pedido de prueba con varios ítems para verificar que la funcionalidad de detalle de pedidos funcione.
    """
    from app.controllers.pedido_controller import PedidoController
    from app.controllers.producto_controller import ProductoController
    from app.controllers.cliente_controller import ClienteController
    from app.models.pedido import Pedido, ItemPedido
    import datetime
    import uuid
    
    pedido_controller = PedidoController()
    producto_controller = ProductoController()
    cliente_controller = ClienteController()
    
    # Verificar que existen productos
    productos_df = producto_controller.obtener_productos()
    if productos_df.empty:
        print("No hay productos para crear un pedido de prueba.")
        return False
    
    # Verificar que existen clientes
    clientes_df = cliente_controller.obtener_clientes()
    if clientes_df.empty:
        print("No hay clientes para crear un pedido de prueba.")
        return False
    
    # Obtener el primer cliente
    cliente_id = clientes_df.iloc[0]['id']
    
    # Crear ítems para el pedido
    items = []
    for i, row in productos_df.iterrows():
        if i >= 2:  # Limitar a 2 productos para evitar el pedido sea muy grande
            break
            
        producto_id = row['id']
        descripcion = row['nombre'] if 'nombre' in row else f"Producto {i+1}"
        precio = row['precio_venta'] if 'precio_venta' in row else 1000
        
        item = ItemPedido(
            id=i+1,
            producto_id=producto_id,
            descripcion=descripcion,
            cantidad=i+1,  # Cantidad incremental
            precio_unitario=float(precio),
            descuento=i*5  # Descuento incremental (0%, 5%, 10%, etc.)
        )
        items.append(item)
    
    # Crear el pedido
    pedido_id = str(uuid.uuid4())[:8]
    pedido = Pedido(
        id=pedido_id,
        cliente_id=cliente_id,
        fecha=datetime.datetime.now().strftime('%Y-%m-%d'),
        estado='Pendiente',
        items=items,
        notas='Pedido de prueba creado automáticamente'
    )
    
    # Guardar el pedido
    resultado = pedido_controller.crear_pedido(pedido)
    
    if resultado:
        print(f"Pedido de prueba creado correctamente con ID: {pedido_id} y {len(items)} ítems")
        return True
    else:
        print("Error al crear el pedido de prueba")
        return False

def verificar_pedidos_de_prueba():
    """
    Verifica si existen pedidos con ítems en la base de datos.
    Si no existen, crea un pedido de prueba con varios ítems.
    """
    from app.controllers.pedido_controller import PedidoController
    from app.controllers.producto_controller import ProductoController
    from app.controllers.cliente_controller import ClienteController
    from app.models.pedido import Pedido, ItemPedido
    import pandas as pd
    import os
    
    pedido_controller = PedidoController()
    producto_controller = ProductoController()
    cliente_controller = ClienteController()
    
    # Verificar si existen pedidos
    pedidos_df = pedido_controller.obtener_pedidos()
    
    if pedidos_df.empty:
        print("No hay pedidos en la base de datos. Creando un pedido de prueba...")
        return crear_pedido_prueba()
    
    # Verificar si hay ítems en los pedidos
    excel_path = os.path.join(root_dir, 'data', 'pedidos.xlsx')
    if os.path.exists(excel_path):
        try:
            df_detalles = pd.read_excel(excel_path, sheet_name='detalles')
            if df_detalles.empty:
                print("La hoja de detalles está vacía. Creando un pedido de prueba con ítems...")
                return crear_pedido_prueba()
        except Exception as e:
            print(f"Error al leer detalles: {str(e)}")
            return crear_pedido_prueba()
    
    return False

try:
    print("Intentando importar main.py desde la raíz...")
    # Verificar si hay pedidos de prueba
    verificar_pedidos_de_prueba()
    
    print("Ejecutando aplicación...")
    # Ejecutar la aplicación principal
    import sys
    sys.path.insert(0, root_dir)
    from main import main
    main()
    
except ImportError:
    print("No se pudo importar main.py desde la raíz, intentando desde app...")
    try:
        # Intentar importar directamente desde el archivo
        import os.path
        import importlib.util
        
        main_path = os.path.join(root_dir, 'main.py')
        if os.path.exists(main_path):
            spec = importlib.util.spec_from_file_location("main", main_path)
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            main_module.main()
        else:
            raise ImportError(f"No se encontró el archivo main.py en {main_path}")
    except Exception as e:
        print(f"Error al iniciar la aplicación: {str(e)}")
        traceback.print_exc()
except Exception as e:
    print(f"Error al iniciar la aplicación: {str(e)}")
    traceback.print_exc() 