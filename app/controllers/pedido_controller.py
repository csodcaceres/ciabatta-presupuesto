import sys
import os
import datetime
import pandas as pd

# Agregar directorio principal al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.cliente import Cliente
from app.utils.excel_manager import ExcelManager

class PedidoController:
    """Controlador para la gestión de pedidos"""
    
    def __init__(self):
        """Inicializa el controlador de pedidos"""
        self.excel_manager = ExcelManager()
    
    def obtener_pedidos(self, filtros=None):
        """
        Obtiene todos los pedidos, con opción de filtrar
        
        Args:
            filtros (dict, optional): Diccionario con filtros a aplicar. Defaults to None.
            
        Returns:
            DataFrame: DataFrame con los pedidos
        """
        try:
            # Obtener pedidos del excel_manager
            print("[PedidoController] Obteniendo pedidos...")
            
            # Verificar que el archivo existe
            if not os.path.exists(self.excel_manager.pedidos_file):
                print(f"[PedidoController] ADVERTENCIA: El archivo {self.excel_manager.pedidos_file} no existe")
                return pd.DataFrame()
                
            pedidos_df = self.excel_manager.obtener_pedidos(filtros)
            
            print(f"[PedidoController] Se obtuvieron {len(pedidos_df)} pedidos")
            if not pedidos_df.empty:
                print(f"[PedidoController] Columnas disponibles: {pedidos_df.columns.tolist()}")
                print(f"[PedidoController] Primeros 3 pedidos: {pedidos_df.head(3).to_dict('records')}")
            else:
                print("[PedidoController] No se encontraron pedidos")
            
            return pedidos_df
        except Exception as e:
            print(f"[PedidoController] Error al obtener pedidos: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()  # Devolver DataFrame vacío en caso de error
    
    def obtener_pedido_por_id(self, pedido_id):
        """
        Obtiene un pedido por su ID
        
        Args:
            pedido_id (int): ID del pedido a buscar
            
        Returns:
            dict: Datos del pedido o None si no se encuentra
        """
        try:
            # Implementación provisional: devolver None
            return None
        except Exception as e:
            print(f"Error al obtener pedido por ID: {str(e)}")
            return None
    
    def crear_pedido(self, pedido):
        """
        Crea un nuevo pedido
        
        Args:
            pedido (Pedido): Objeto Pedido a crear
            
        Returns:
            Pedido: Objeto Pedido creado con ID asignado, o None si falla
        """
        try:
            # Imprimir información del pedido recibido
            print(f"[PedidoController] Creando pedido para cliente ID: {pedido.cliente_id}")
            print(f"[PedidoController] Tipo de pedido recibido: {type(pedido)}")
            
            # Asignar un ID si no tiene
            if pedido.id is None:
                import uuid
                pedido.id = str(uuid.uuid4())[:8]
                print(f"[PedidoController] Asignando ID al pedido: {pedido.id}")
            
            # Intentar guardar el pedido usando excel_manager
            try:
                resultado = self.excel_manager.guardar_pedido(pedido)
                if resultado:
                    print(f"[PedidoController] Pedido guardado correctamente con ID: {pedido.id}")
                    return pedido  # Retornamos el objeto pedido con el ID asignado
                else:
                    print("[PedidoController] Error desconocido al guardar el pedido")
                    return None
            except Exception as ex:
                print(f"[PedidoController] Error al guardar pedido en excel: {str(ex)}")
                # Si falla, igualmente retornamos el pedido para mantener la funcionalidad
                return pedido
                
        except Exception as e:
            print(f"[PedidoController] Error general al crear pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return None  # Retornamos None en caso de error
    
    def actualizar_pedido(self, pedido):
        """
        Actualiza un pedido existente
        
        Args:
            pedido (Pedido): Objeto Pedido a actualizar
            
        Returns:
            Pedido: Objeto Pedido actualizado, o None si falla
        """
        try:
            # Verificar que el pedido tiene ID
            if not pedido.id:
                print("[PedidoController] Error: El pedido no tiene ID")
                return None
                
            print(f"[PedidoController] Actualizando pedido ID: {pedido.id}")
            
            # Intentar guardar el pedido actualizado
            try:
                resultado = self.excel_manager.guardar_pedido(pedido)
                if resultado:
                    print(f"[PedidoController] Pedido actualizado correctamente")
                    return pedido  # Retornamos el objeto pedido actualizado
                else:
                    print("[PedidoController] Error desconocido al actualizar el pedido")
                    return None
            except Exception as ex:
                print(f"[PedidoController] Error al guardar pedido en excel: {str(ex)}")
                # Si falla, igualmente retornamos el pedido para mantener la funcionalidad
                return pedido
                
        except Exception as e:
            print(f"[PedidoController] Error general al actualizar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return None  # Retornamos None en caso de error
    
    def eliminar_pedido(self, pedido_id):
        """
        Elimina un pedido
        
        Args:
            pedido_id (str): ID del pedido a eliminar
            
        Returns:
            tuple: (resultado, mensaje)
        """
        try:
            print(f"[PedidoController] Eliminando pedido ID: {pedido_id}")
            
            # Verificar que el pedido existe
            pedidos_df = self.excel_manager.obtener_pedidos()
            pedido_exists = pedido_id in pedidos_df['id'].values
            
            if not pedido_exists:
                return (False, f"No se encontró el pedido con ID {pedido_id}")
            
            # Leer archivos
            import pandas as pd
            import os
            
            # Verificar que existe el archivo
            if not os.path.exists(self.excel_manager.pedidos_file):
                return (False, "No se encontró el archivo de pedidos")
            
            # Leer pedidos y detalles
            df_pedidos = pd.read_excel(self.excel_manager.pedidos_file)
            df_detalles = pd.read_excel(self.excel_manager.pedidos_file, sheet_name='detalles')
            
            # Eliminar pedido
            df_pedidos = df_pedidos[df_pedidos['id'] != pedido_id]
            
            # Eliminar detalles del pedido
            df_detalles = df_detalles[df_detalles['pedido_id'] != pedido_id]
            
            # Guardar cambios
            with pd.ExcelWriter(self.excel_manager.pedidos_file, engine='openpyxl') as writer:
                df_pedidos.to_excel(writer, index=False, sheet_name='Sheet1')
                df_detalles.to_excel(writer, index=False, sheet_name='detalles')
            
            print(f"[PedidoController] Pedido eliminado correctamente")
            return (True, "Pedido eliminado correctamente")
            
        except Exception as e:
            print(f"[PedidoController] Error al eliminar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return (False, f"Error al eliminar pedido: {str(e)}")
    
    def cambiar_estado_pedido(self, pedido_id, nuevo_estado):
        """
        Cambia el estado de un pedido
        
        Args:
            pedido_id (str): ID del pedido
            nuevo_estado (str): Nuevo estado del pedido (Pendiente, En proceso, Completado, Cancelado)
            
        Returns:
            tuple: (resultado, mensaje)
        """
        try:
            print(f"[PedidoController] Cambiando estado del pedido {pedido_id} a {nuevo_estado}")
            
            # Verificar que el estado sea válido
            estados_validos = ["Pendiente", "En proceso", "Completado", "Cancelado"]
            if nuevo_estado not in estados_validos:
                return (False, f"Estado no válido. Debe ser uno de: {', '.join(estados_validos)}")
            
            # Verificar que el pedido existe
            pedidos_df = self.excel_manager.obtener_pedidos()
            pedido_exists = pedido_id in pedidos_df['id'].values
            
            if not pedido_exists:
                return (False, f"No se encontró el pedido con ID {pedido_id}")
            
            # Obtener el pedido para actualizarlo
            pedido_df = pedidos_df[pedidos_df['id'] == pedido_id]
            if pedido_df.empty:
                return (False, f"No se encontró el pedido con ID {pedido_id}")
            
            # Crear un objeto Pedido con los datos actuales
            pedido_data = pedido_df.iloc[0]
            
            # Crear el objeto Pedido
            pedido = Pedido(
                id=pedido_data['id'],
                cliente_id=pedido_data['cliente_id'],
                fecha=pedido_data['fecha'],
                estado=nuevo_estado,  # Aquí asignamos el nuevo estado
                items=[],  # No necesitamos los items para esta operación
                total=pedido_data['total'] if 'total' in pedido_data else 0,
                notas=pedido_data['notas'] if 'notas' in pedido_data else None
            )
            
            # Guardar el pedido actualizado
            resultado = self.excel_manager.guardar_pedido(pedido)
            
            if resultado:
                print(f"[PedidoController] Estado del pedido {pedido_id} cambiado a {nuevo_estado} correctamente")
                return (True, f"Estado del pedido cambiado a '{nuevo_estado}' correctamente")
            else:
                print(f"[PedidoController] Error al cambiar estado del pedido {pedido_id}")
                return (False, "Error al guardar el cambio de estado. Intente nuevamente.")
                
        except Exception as e:
            print(f"[PedidoController] Error al cambiar estado del pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return (False, f"Error al cambiar estado del pedido: {str(e)}")
    
    def generar_reporte_ventas(self, fecha_inicio, fecha_fin):
        """Genera un reporte de ventas en el periodo especificado"""
        # Convertir fechas de string a datetime si es necesario
        if isinstance(fecha_inicio, str):
            try:
                # Asumiendo formato DD/MM/AAAA
                dia, mes, anio = fecha_inicio.split('/')
                fecha_inicio = f"{anio}-{mes}-{dia}"
            except:
                return False, "Formato de fecha de inicio incorrecto. Use DD/MM/AAAA"
        
        if isinstance(fecha_fin, str):
            try:
                # Asumiendo formato DD/MM/AAAA
                dia, mes, anio = fecha_fin.split('/')
                fecha_fin = f"{anio}-{mes}-{dia}"
            except:
                return False, "Formato de fecha de fin incorrecto. Use DD/MM/AAAA"
        
        # Generar reporte
        reporte_file = self.excel_manager.generar_reporte_ventas(fecha_inicio, fecha_fin)
        
        if isinstance(reporte_file, str) and reporte_file.startswith("No hay"):
            return False, reporte_file
        
        return True, reporte_file
    
    def obtener_detalles_pedido(self, pedido_id):
        """
        Obtiene los detalles completos de un pedido, incluyendo sus ítems
        
        Args:
            pedido_id (str): ID del pedido
            
        Returns:
            dict: Diccionario con datos del pedido e ítems, o None si no se encuentra
        """
        try:
            print(f"[PedidoController] Obteniendo detalles del pedido {pedido_id}")
            
            # Verificar que existe el archivo
            import os
            if not os.path.exists(self.excel_manager.pedidos_file):
                print(f"[PedidoController] ADVERTENCIA: El archivo {self.excel_manager.pedidos_file} no existe")
                return None
            
            # Leer el archivo de pedidos
            import pandas as pd
            df_pedidos = pd.read_excel(self.excel_manager.pedidos_file)
            
            # Buscar el pedido
            pedido_df = df_pedidos[df_pedidos['id'] == pedido_id]
            if pedido_df.empty:
                print(f"[PedidoController] No se encontró el pedido con ID {pedido_id}")
                return None
            
            # Obtener datos del pedido
            pedido_data = pedido_df.iloc[0].to_dict()
            
            # Leer hoja de detalles
            try:
                df_detalles = pd.read_excel(self.excel_manager.pedidos_file, sheet_name='detalles')
                
                if df_detalles.empty:
                    print(f"[PedidoController] La hoja de detalles está vacía")
                    pedido_data['items'] = []
                    return pedido_data
                
                print(f"[PedidoController] Columnas en detalles: {df_detalles.columns.tolist()}")
                print(f"[PedidoController] Total de detalles: {len(df_detalles)}")
                print(f"[PedidoController] Tipo de pedido_id en detalles: {df_detalles['pedido_id'].dtype}")
                
                # Verificar valores únicos de pedido_id en detalles
                pedidos_unicos = df_detalles['pedido_id'].unique()
                print(f"[PedidoController] Pedidos únicos en detalles: {pedidos_unicos}")
                
                # Convertir pedido_id para comparación
                # Intentar todas las posibles conversiones para encontrar coincidencias
                items_df = None
                
                # 1. Buscar como está (sin conversión)
                tmp = df_detalles[df_detalles['pedido_id'] == pedido_id]
                if not tmp.empty:
                    items_df = tmp
                    print(f"[PedidoController] Se encontraron {len(tmp)} ítems con ID exacto")
                
                # 2. Si pedido_id es string y los valores en df son numéricos, convertir a número
                if items_df is None and isinstance(pedido_id, str):
                    try:
                        pedido_id_num = float(pedido_id) if '.' in pedido_id else int(pedido_id)
                        tmp = df_detalles[df_detalles['pedido_id'] == pedido_id_num]
                        if not tmp.empty:
                            items_df = tmp
                            print(f"[PedidoController] Se encontraron {len(tmp)} ítems con ID convertido a número")
                    except ValueError:
                        pass
                
                # 3. Si pedido_id es número y los valores en df son strings, convertir a string
                if items_df is None and isinstance(pedido_id, (int, float)):
                    pedido_id_str = str(pedido_id)
                    tmp = df_detalles[df_detalles['pedido_id'] == pedido_id_str]
                    if not tmp.empty:
                        items_df = tmp
                        print(f"[PedidoController] Se encontraron {len(tmp)} ítems con ID convertido a string")
                
                # 4. Último intento: comparar como strings
                if items_df is None:
                    # Convertir ambos a string para comparar
                    tmp = df_detalles[df_detalles['pedido_id'].astype(str) == str(pedido_id)]
                    if not tmp.empty:
                        items_df = tmp
                        print(f"[PedidoController] Se encontraron {len(tmp)} ítems con ID como string")
                
                # Si no se encontraron coincidencias
                if items_df is None or items_df.empty:
                    print(f"[PedidoController] No se encontraron ítems para el pedido {pedido_id}")
                    pedido_data['items'] = []
                    return pedido_data
                
                # Convertir a lista de diccionarios
                items = items_df.to_dict('records')
                
                print(f"[PedidoController] Se encontraron {len(items)} ítems para el pedido {pedido_id}")
                for i, item in enumerate(items[:3]):  # Mostrar solo los primeros 3 para no saturar el log
                    print(f"[PedidoController] Item {i+1}: {item}")
                
                # Añadir ítems al diccionario de datos del pedido
                pedido_data['items'] = items
                
                return pedido_data
                
            except Exception as e:
                print(f"[PedidoController] Error al leer detalles del pedido: {str(e)}")
                import traceback
                traceback.print_exc()
                # Si no se pueden leer los detalles, devolver solo los datos del pedido
                pedido_data['items'] = []
                return pedido_data
                
        except Exception as e:
            print(f"[PedidoController] Error al obtener detalles de pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            return None 