import pandas as pd
import os
import sys
import uuid

# Agregar el directorio principal al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.excel_manager import ExcelManager
from app.models.producto import Producto

class ProductoController:
    """Controlador para la gestión de productos"""
    
    def __init__(self):
        """Inicializa el controlador de productos"""
        self.excel_manager = ExcelManager()
    
    def obtener_productos(self, filtros=None):
        """
        Obtiene todos los productos, con opción de filtrar
        
        Args:
            filtros (dict, optional): Diccionario con filtros a aplicar. Defaults to None.
            
        Returns:
            DataFrame: DataFrame con los productos
        """
        try:
            df_productos = self.excel_manager.obtener_productos(filtros)
            
            # Verificar si el DataFrame está vacío
            if df_productos.empty:
                print("El DataFrame de productos está vacío")
                return df_productos
            
            # Verificar columnas y asegurar compatibilidad
            print(f"[ProductoController] Columnas en DataFrame productos: {df_productos.columns.tolist()}")
            print(f"[ProductoController] Número de productos: {len(df_productos)}")
            print(f"[ProductoController] Primeros productos: {df_productos.head().to_dict('records')}")
            
            # Si no existe precio_venta pero sí precio, crear columna precio_venta
            if 'precio' in df_productos.columns and 'precio_venta' not in df_productos.columns:
                print("[ProductoController] Creando columna precio_venta a partir de precio")
                df_productos['precio_venta'] = df_productos['precio']
                
            # Si no existe precio pero sí precio_venta, crear columna precio
            if 'precio_venta' in df_productos.columns and 'precio' not in df_productos.columns:
                print("[ProductoController] Creando columna precio a partir de precio_venta")
                df_productos['precio'] = df_productos['precio_venta']
            
            # Si no existe ninguna, crear ambas con valor 0
            if 'precio' not in df_productos.columns and 'precio_venta' not in df_productos.columns:
                print("[ProductoController] Creando columnas de precio con valores predeterminados")
                df_productos['precio'] = 0.0
                df_productos['precio_venta'] = 0.0
                
            return df_productos
        except Exception as e:
            print(f"[ProductoController] Error al obtener productos: {str(e)}")
            return pd.DataFrame()  # Devolver DataFrame vacío en caso de error
    
    def obtener_producto_por_id(self, producto_id):
        """
        Obtiene un producto por su ID
        
        Args:
            producto_id (int): ID del producto a buscar
            
        Returns:
            Producto: Instancia del producto o None si no se encuentra
        """
        try:
            df_productos = self.excel_manager.obtener_productos()
            if producto_id in df_productos['id'].values:
                producto_data = df_productos[df_productos['id'] == producto_id].iloc[0]
                return Producto(
                    id=producto_data['id'],
                    nombre=producto_data['nombre'],
                    descripcion=producto_data['descripcion'],
                    precio_compra=float(producto_data.get('precio_compra', 0)),
                    precio_venta=float(producto_data.get('precio_venta', 0))
                )
            return None
        except Exception as e:
            print(f"Error al obtener producto por ID: {str(e)}")
            return None
    
    def crear_producto(self, producto):
        """
        Crea un nuevo producto
        
        Args:
            producto (Producto): Producto a crear
            
        Returns:
            tuple: (resultado, mensaje)
        """
        try:
            # Generar ID si es None
            if producto.id is None:
                producto.id = str(uuid.uuid4())[:8]
            
            # Guardar producto
            self.excel_manager.guardar_producto(producto)
            return (True, "Producto creado correctamente")
        except Exception as e:
            return (False, f"Error al crear producto: {str(e)}")
    
    def actualizar_producto(self, producto_id, producto):
        """
        Actualiza un producto existente
        
        Args:
            producto_id (str): ID del producto a actualizar
            producto (Producto): Producto con los nuevos datos
            
        Returns:
            tuple: (resultado, mensaje)
        """
        try:
            # Verificar que el producto existe
            producto_existente = self.obtener_producto_por_id(producto_id)
            if not producto_existente:
                return (False, f"No se encontró un producto con ID {producto_id}")
            
            # Guardar producto actualizado
            self.excel_manager.guardar_producto(producto)
            return (True, "Producto actualizado correctamente")
        except Exception as e:
            return (False, f"Error al actualizar producto: {str(e)}")
    
    def eliminar_producto(self, producto_id):
        """
        Elimina un producto
        
        Args:
            producto_id (str): ID del producto a eliminar
            
        Returns:
            tuple: (resultado, mensaje)
        """
        try:
            # Verificar que el producto existe
            producto_existente = self.obtener_producto_por_id(producto_id)
            if not producto_existente:
                return (False, f"No se encontró un producto con ID {producto_id}")
            
            # Eliminar producto
            result = self.excel_manager.eliminar_producto(producto_id)
            if result:
                return (True, "Producto eliminado correctamente")
            else:
                return (False, "No se pudo eliminar el producto")
        except Exception as e:
            return (False, f"Error al eliminar producto: {str(e)}") 