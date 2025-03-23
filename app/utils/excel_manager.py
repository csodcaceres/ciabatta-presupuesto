import pandas as pd
import os
from datetime import datetime

class ExcelManager:
    def __init__(self, data_directory="data"):
        self.data_directory = data_directory
        self.pedidos_file = os.path.join(data_directory, "pedidos.xlsx")
        self.clientes_file = os.path.join(data_directory, "clientes.xlsx")
        self.productos_file = os.path.join(data_directory, "productos.xlsx")
        self.presupuestos_file = os.path.join(data_directory, "presupuestos.xlsx")
        
        # Asegurar que el directorio de datos exista
        if not os.path.exists(data_directory):
            os.makedirs(data_directory)
        
        # Inicializar los archivos de Excel si no existen
        self._inicializar_archivos()
    
    def _inicializar_archivos(self):
        # Inicializar archivo de pedidos
        if not os.path.exists(self.pedidos_file):
            df_pedidos = pd.DataFrame(columns=['id', 'cliente_id', 'fecha', 'estado', 'total'])
            df_pedidos.to_excel(self.pedidos_file, index=False)
            
            # Crear una hoja adicional para los detalles de productos por pedido
            with pd.ExcelWriter(self.pedidos_file, engine='openpyxl', mode='a') as writer:
                df_detalles = pd.DataFrame(columns=['pedido_id', 'producto_id', 'cantidad', 'precio_unitario', 'subtotal'])
                df_detalles.to_excel(writer, sheet_name='detalles', index=False)
        
        # Inicializar archivo de clientes
        if not os.path.exists(self.clientes_file):
            df_clientes = pd.DataFrame(columns=['id', 'nombre', 'apellido', 'email', 'telefono', 'direccion'])
            df_clientes.to_excel(self.clientes_file, index=False)
        
        # Inicializar archivo de productos
        if not os.path.exists(self.productos_file):
            df_productos = pd.DataFrame(columns=['id', 'nombre', 'descripcion', 'precio_compra', 'precio_venta'])
            df_productos.to_excel(self.productos_file, index=False)
            
        # Inicializar archivo de presupuestos
        if not os.path.exists(self.presupuestos_file):
            df_presupuestos = pd.DataFrame(columns=['id', 'cliente_id', 'fecha', 'validez', 'total', 'notas', 'estado'])
            df_presupuestos.to_excel(self.presupuestos_file, index=False)
            
            # Crear una hoja adicional para los ítems de presupuesto
            with pd.ExcelWriter(self.presupuestos_file, engine='openpyxl', mode='a') as writer:
                df_items = pd.DataFrame(columns=['presupuesto_id', 'id', 'descripcion', 'cantidad', 'precio_unitario', 'descuento', 'subtotal'])
                df_items.to_excel(writer, sheet_name='items', index=False)
    
    def guardar_pedido(self, pedido):
        """
        Guarda un pedido en el archivo Excel
        
        Args:
            pedido (Pedido): Objeto pedido a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            print(f"[ExcelManager] Guardando pedido ID: {pedido.id}")
            print(f"[ExcelManager] Cliente ID: {pedido.cliente_id}")
            print(f"[ExcelManager] Items: {len(pedido.items) if hasattr(pedido, 'items') else 'No tiene atributo items'}")
            
            # Leer datos actuales
            df_pedidos = pd.read_excel(self.pedidos_file)
            df_detalles = pd.read_excel(self.pedidos_file, sheet_name='detalles')
            
            # Preparar información del pedido
            datos_pedido = {
                'id': pedido.id,
                'cliente_id': pedido.cliente_id,  # Usamos directamente el cliente_id del pedido
                'fecha': pedido.fecha if hasattr(pedido, 'fecha') else datetime.now().strftime('%Y-%m-%d'),
                'estado': pedido.estado if hasattr(pedido, 'estado') else 'Nuevo',
                'total': pedido.total,
                'notas': pedido.notas if hasattr(pedido, 'notas') else ''
            }
            
            # Verificar si el pedido ya existe
            if pedido.id in df_pedidos['id'].values:
                print(f"[ExcelManager] Actualizando pedido existente ID: {pedido.id}")
                # Actualizar pedido existente
                idx = df_pedidos[df_pedidos['id'] == pedido.id].index[0]
                
                for campo, valor in datos_pedido.items():
                    if campo in df_pedidos.columns:
                        df_pedidos.at[idx, campo] = valor
                
                # Eliminar detalles antiguos
                print(f"[ExcelManager] Eliminando {len(df_detalles[df_detalles['pedido_id'] == pedido.id])} detalles antiguos para el pedido ID: {pedido.id}")
                df_detalles = df_detalles[df_detalles['pedido_id'] != pedido.id]
            else:
                print(f"[ExcelManager] Creando nuevo pedido ID: {pedido.id}")
                # Verificar que el DataFrame tiene todas las columnas necesarias
                for campo in datos_pedido.keys():
                    if campo not in df_pedidos.columns:
                        df_pedidos[campo] = ''
                
                # Crear nuevo pedido
                df_pedidos = pd.concat([df_pedidos, pd.DataFrame([datos_pedido])], ignore_index=True)
            
            # Agregar detalles de items
            if hasattr(pedido, 'items') and pedido.items:
                print(f"[ExcelManager] Agregando {len(pedido.items)} items al pedido {pedido.id}")
                for i, item in enumerate(pedido.items):
                    # Asegurarnos de que todos los atributos necesarios existen
                    detalle = {
                        'pedido_id': pedido.id,  # Asegurarse de que el pedido_id sea consistente
                        'id': getattr(item, 'id', i+1),  # Usar el id del item o índice+1
                        'producto_id': getattr(item, 'producto_id', None),
                        'descripcion': getattr(item, 'descripcion', 'Sin descripción'),
                        'cantidad': getattr(item, 'cantidad', 0),
                        'precio_unitario': getattr(item, 'precio_unitario', 0),
                        'descuento': getattr(item, 'descuento', 0),
                        'subtotal': getattr(item, 'subtotal', 0)
                    }
                    
                    print(f"[ExcelManager] Item {i+1}: {detalle['descripcion']}, Cantidad: {detalle['cantidad']}, Precio: {detalle['precio_unitario']}, pedido_id: {detalle['pedido_id']}")
                    
                    # Verificar que el DataFrame tiene todas las columnas necesarias
                    for campo in detalle.keys():
                        if campo not in df_detalles.columns:
                            df_detalles[campo] = ''
                            
                    # Añadir el detalle al DataFrame
                    df_detalles = pd.concat([df_detalles, pd.DataFrame([detalle])], ignore_index=True)
            else:
                print(f"[ExcelManager] El pedido {pedido.id} no tiene items o no tiene el atributo 'items'")
                if hasattr(pedido, 'items'):
                    print(f"[ExcelManager] Tipo de pedido.items: {type(pedido.items)}")
                    print(f"[ExcelManager] ¿pedido.items es None? {pedido.items is None}")
                    print(f"[ExcelManager] Longitud de pedido.items: {len(pedido.items) if pedido.items is not None else 'None'}")
                else:
                    print(f"[ExcelManager] El pedido no tiene el atributo 'items'")
            
            # Verificar detalles antes de guardar
            print(f"[ExcelManager] DataFrame de pedidos antes de guardar: {len(df_pedidos)} filas")
            print(f"[ExcelManager] DataFrame de detalles antes de guardar: {len(df_detalles)} filas")
            pedidos_ids = df_pedidos['id'].unique()
            print(f"[ExcelManager] IDs de pedidos en df_pedidos: {pedidos_ids}")
            if 'pedido_id' in df_detalles.columns:
                detalles_pedido_ids = df_detalles['pedido_id'].unique()
                print(f"[ExcelManager] IDs de pedidos en df_detalles: {detalles_pedido_ids}")
            
            # Guardar cambios
            with pd.ExcelWriter(self.pedidos_file, engine='openpyxl') as writer:
                df_pedidos.to_excel(writer, index=False, sheet_name='Sheet1')
                df_detalles.to_excel(writer, index=False, sheet_name='detalles')
            
            print(f"[ExcelManager] Pedido guardado correctamente con {len(pedido.items) if hasattr(pedido, 'items') and pedido.items else 0} items")
            
            # Verificar que los detalles se guardaron correctamente
            try:
                df_check = pd.read_excel(self.pedidos_file, sheet_name='detalles')
                if 'pedido_id' in df_check.columns:
                    items_count = len(df_check[df_check['pedido_id'] == pedido.id])
                    print(f"[ExcelManager] Verificación: Se encontraron {items_count} items para el pedido {pedido.id} después de guardar")
                else:
                    print(f"[ExcelManager] Verificación: No existe columna 'pedido_id' en la hoja de detalles")
            except Exception as check_err:
                print(f"[ExcelManager] Error al verificar detalles guardados: {str(check_err)}")
            
            return True
            
        except Exception as e:
            import traceback
            print(f"[ExcelManager] Error al guardar pedido: {str(e)}")
            traceback.print_exc()
            return False
    
    def obtener_pedidos(self, filtro=None):
        """Obtiene todos los pedidos, opcionalmente filtrados"""
        df_pedidos = pd.read_excel(self.pedidos_file)
        df_detalles = pd.read_excel(self.pedidos_file, sheet_name='detalles')
        
        if filtro:
            # Aplicar filtros si se especifican
            if 'estado' in filtro:
                df_pedidos = df_pedidos[df_pedidos['estado'] == filtro['estado']]
            if 'cliente_id' in filtro:
                df_pedidos = df_pedidos[df_pedidos['cliente_id'] == filtro['cliente_id']]
            if 'fecha_desde' in filtro and 'fecha_hasta' in filtro:
                df_pedidos = df_pedidos[(df_pedidos['fecha'] >= filtro['fecha_desde']) & 
                                        (df_pedidos['fecha'] <= filtro['fecha_hasta'])]
        
        return df_pedidos
    
    def guardar_cliente(self, cliente):
        """Guarda un cliente en el archivo Excel"""
        df_clientes = pd.read_excel(self.clientes_file)
        
        if cliente.id in df_clientes['id'].values:
            idx = df_clientes[df_clientes['id'] == cliente.id].index[0]
            df_clientes.at[idx, 'nombre'] = cliente.nombre
            df_clientes.at[idx, 'apellido'] = cliente.apellido
            df_clientes.at[idx, 'email'] = cliente.email
            df_clientes.at[idx, 'telefono'] = cliente.telefono
            df_clientes.at[idx, 'direccion'] = cliente.direccion
        else:
            nuevo_cliente = cliente.to_dict()
            df_clientes = pd.concat([df_clientes, pd.DataFrame([nuevo_cliente])], ignore_index=True)
        
        df_clientes.to_excel(self.clientes_file, index=False)
    
    def obtener_clientes(self, filtro=None):
        """Obtiene todos los clientes, opcionalmente filtrados"""
        df_clientes = pd.read_excel(self.clientes_file)
        
        if filtro:
            if 'nombre' in filtro:
                df_clientes = df_clientes[df_clientes['nombre'].str.contains(filtro['nombre'], case=False)]
            if 'apellido' in filtro:
                df_clientes = df_clientes[df_clientes['apellido'].str.contains(filtro['apellido'], case=False)]
        
        return df_clientes
    
    def guardar_producto(self, producto):
        """Guarda un producto en el archivo Excel"""
        df_productos = pd.read_excel(self.productos_file)
        
        if producto.id in df_productos['id'].values:
            idx = df_productos[df_productos['id'] == producto.id].index[0]
            df_productos.at[idx, 'nombre'] = producto.nombre
            df_productos.at[idx, 'descripcion'] = producto.descripcion
            df_productos.at[idx, 'precio_compra'] = producto.precio_compra
            df_productos.at[idx, 'precio_venta'] = producto.precio_venta
        else:
            nuevo_producto = {
                'id': producto.id,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio_compra': producto.precio_compra,
                'precio_venta': producto.precio_venta
            }
            df_productos = pd.concat([df_productos, pd.DataFrame([nuevo_producto])], ignore_index=True)
        
        df_productos.to_excel(self.productos_file, index=False)
    
    def eliminar_producto(self, producto_id):
        """Elimina un producto del archivo Excel"""
        try:
            df_productos = pd.read_excel(self.productos_file)
            
            # Verificar si el producto existe
            if producto_id not in df_productos['id'].values:
                return False
            
            # Eliminar el producto
            df_productos = df_productos[df_productos['id'] != producto_id]
            df_productos.to_excel(self.productos_file, index=False)
            
            return True
        except Exception as e:
            print(f"Error al eliminar producto: {str(e)}")
            return False
    
    def obtener_productos(self, filtro=None):
        """Obtiene todos los productos, opcionalmente filtrados"""
        df_productos = pd.read_excel(self.productos_file)
        
        if filtro:
            if 'nombre' in filtro:
                df_productos = df_productos[df_productos['nombre'].str.contains(filtro['nombre'], case=False)]
            if 'precio_min' in filtro and 'precio_max' in filtro:
                df_productos = df_productos[(df_productos['precio_venta'] >= filtro['precio_min']) & 
                                           (df_productos['precio_venta'] <= filtro['precio_max'])]
        
        return df_productos
    
    def generar_reporte_ventas(self, fecha_inicio, fecha_fin, formato='excel'):
        """Genera un reporte de ventas entre las fechas especificadas"""
        df_pedidos = pd.read_excel(self.pedidos_file)
        df_detalles = pd.read_excel(self.pedidos_file, sheet_name='detalles')
        df_clientes = pd.read_excel(self.clientes_file)
        df_productos = pd.read_excel(self.productos_file)
        
        # Filtrar pedidos por fecha y estado completado
        df_filtrado = df_pedidos[
            (df_pedidos['fecha'] >= fecha_inicio) & 
            (df_pedidos['fecha'] <= fecha_fin) & 
            (df_pedidos['estado'] == 'completado')
        ]
        
        if df_filtrado.empty:
            return "No hay ventas en el período especificado"
        
        # Unir con detalles y productos
        df_reporte = pd.merge(df_filtrado, df_detalles, left_on='id', right_on='pedido_id')
        df_reporte = pd.merge(df_reporte, df_productos[['id', 'nombre', 'categoria']], 
                             left_on='producto_id', right_on='id', suffixes=('', '_producto'))
        df_reporte = pd.merge(df_reporte, df_clientes[['id', 'nombre', 'apellido']], 
                             left_on='cliente_id', right_on='id', suffixes=('', '_cliente'))
        
        # Crear nombre para el archivo del reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_file = os.path.join(self.data_directory, f"reporte_ventas_{timestamp}.xlsx")
        
        # Guardar reporte
        with pd.ExcelWriter(reporte_file, engine='openpyxl') as writer:
            # Reporte resumido
            resumen = df_filtrado.groupby('fecha').agg({'total': 'sum'}).reset_index()
            resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Reporte detallado
            detalle = df_reporte[['fecha', 'nombre_cliente', 'apellido', 'nombre', 'cantidad', 
                                'precio_unitario', 'subtotal', 'total']]
            detalle.columns = ['Fecha', 'Nombre Cliente', 'Apellido Cliente', 'Producto', 
                             'Cantidad', 'Precio Unitario', 'Subtotal', 'Total Pedido']
            detalle.to_excel(writer, sheet_name='Detalle', index=False)
            
            # Reporte por producto
            por_producto = df_reporte.groupby(['nombre', 'categoria']).agg(
                {'cantidad': 'sum', 'subtotal': 'sum'}).reset_index()
            por_producto.columns = ['Producto', 'Categoría', 'Unidades Vendidas', 'Total Ventas']
            por_producto.to_excel(writer, sheet_name='Por Producto', index=False)
            
            # Reporte por cliente
            por_cliente = df_reporte.groupby(['nombre_cliente', 'apellido']).agg(
                {'id': 'count', 'total': 'sum'}).reset_index()
            por_cliente.columns = ['Nombre', 'Apellido', 'Cantidad Pedidos', 'Total Gastado']
            por_cliente.to_excel(writer, sheet_name='Por Cliente', index=False)
        
        return reporte_file
    
    def guardar_presupuesto(self, presupuesto):
        """Guarda un presupuesto en el archivo Excel"""
        # Leer datos actuales
        df_presupuestos = pd.read_excel(self.presupuestos_file)
        df_items = pd.read_excel(self.presupuestos_file, sheet_name='items')
        
        # Verificar si el presupuesto ya existe
        if presupuesto.id in df_presupuestos['id'].values:
            # Actualizar presupuesto existente
            idx = df_presupuestos[df_presupuestos['id'] == presupuesto.id].index[0]
            df_presupuestos.at[idx, 'estado'] = presupuesto.estado
            df_presupuestos.at[idx, 'total'] = presupuesto.total
            df_presupuestos.at[idx, 'notas'] = presupuesto.notas
            
            # Eliminar ítems antiguos
            df_items = df_items[df_items['presupuesto_id'] != presupuesto.id]
        else:
            # Crear nuevo presupuesto
            cliente_id = presupuesto.cliente.id if hasattr(presupuesto.cliente, 'id') else presupuesto.cliente
            nuevo_presupuesto = {
                'id': presupuesto.id,
                'cliente_id': cliente_id,
                'fecha': presupuesto.fecha,
                'validez': presupuesto.validez,
                'total': presupuesto.total,
                'notas': presupuesto.notas,
                'estado': presupuesto.estado
            }
            df_presupuestos = pd.concat([df_presupuestos, pd.DataFrame([nuevo_presupuesto])], ignore_index=True)
        
        # Agregar ítems de presupuesto
        for item in presupuesto.items:
            item_dict = {
                'presupuesto_id': presupuesto.id,
                'id': item.id,
                'descripcion': item.descripcion,
                'cantidad': item.cantidad,
                'precio_unitario': item.precio_unitario,
                'descuento': item.descuento,
                'subtotal': item.subtotal
            }
            df_items = pd.concat([df_items, pd.DataFrame([item_dict])], ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(self.presupuestos_file, engine='openpyxl') as writer:
            df_presupuestos.to_excel(writer, index=False, sheet_name='Sheet1')
            df_items.to_excel(writer, index=False, sheet_name='items')
    
    def obtener_presupuestos(self, filtro=None):
        """Obtiene todos los presupuestos, opcionalmente filtrados"""
        df_presupuestos = pd.read_excel(self.presupuestos_file)
        
        if filtro:
            # Aplicar filtros si se especifican
            if 'estado' in filtro:
                df_presupuestos = df_presupuestos[df_presupuestos['estado'] == filtro['estado']]
            if 'cliente_id' in filtro:
                df_presupuestos = df_presupuestos[df_presupuestos['cliente_id'] == filtro['cliente_id']]
            if 'fecha_desde' in filtro and 'fecha_hasta' in filtro:
                df_presupuestos = df_presupuestos[(df_presupuestos['fecha'] >= filtro['fecha_desde']) & 
                                                (df_presupuestos['fecha'] <= filtro['fecha_hasta'])]
        
        return df_presupuestos
    
    def obtener_items_presupuesto(self, presupuesto_id):
        """Obtiene los ítems de un presupuesto específico"""
        df_items = pd.read_excel(self.presupuestos_file, sheet_name='items')
        return df_items[df_items['presupuesto_id'] == presupuesto_id]
    
    def convertir_presupuesto_a_pedido(self, presupuesto_id):
        """Convierte un presupuesto aceptado en un pedido"""
        # Obtener presupuesto
        df_presupuestos = pd.read_excel(self.presupuestos_file)
        presupuesto_row = df_presupuestos[df_presupuestos['id'] == presupuesto_id]
        
        if presupuesto_row.empty or presupuesto_row.iloc[0]['estado'] != 'aceptado':
            return False, "Presupuesto no encontrado o no está aceptado"
        
        # Crear nuevo pedido
        presupuesto_data = presupuesto_row.iloc[0]
        pedido_id = int(datetime.now().timestamp())
        nuevo_pedido = {
            'id': pedido_id,
            'cliente_id': presupuesto_data['cliente_id'],
            'fecha': datetime.now().strftime("%d/%m/%Y"),
            'estado': 'pendiente',
            'total': presupuesto_data['total']
        }
        
        # Guardar pedido
        df_pedidos = pd.read_excel(self.pedidos_file)
        df_pedidos = pd.concat([df_pedidos, pd.DataFrame([nuevo_pedido])], ignore_index=True)
        
        # Obtener ítems del presupuesto
        df_items_presupuesto = pd.read_excel(self.presupuestos_file, sheet_name='items')
        items_presupuesto = df_items_presupuesto[df_items_presupuesto['presupuesto_id'] == presupuesto_id]
        
        # Crear ítems para el pedido
        df_detalles_pedido = pd.read_excel(self.pedidos_file, sheet_name='detalles')
        detalles_pedido = []
        
        for _, item in items_presupuesto.iterrows():
            detalle = {
                'pedido_id': pedido_id,
                'producto_id': item['id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'subtotal': item['subtotal']
            }
            detalles_pedido.append(detalle)
        
        df_detalles_pedido = pd.concat([df_detalles_pedido, pd.DataFrame(detalles_pedido)], ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(self.pedidos_file, engine='openpyxl') as writer:
            df_pedidos.to_excel(writer, index=False, sheet_name='Sheet1')
            df_detalles_pedido.to_excel(writer, index=False, sheet_name='detalles')
        
        return True, pedido_id 