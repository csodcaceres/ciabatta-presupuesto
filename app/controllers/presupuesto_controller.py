import pandas as pd
import os
import sys
import datetime

# Agregar el directorio principal al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.excel_manager import ExcelManager
from app.models.presupuesto import Presupuesto, ItemPresupuesto

class PresupuestoController:
    """Controlador para la gestión de presupuestos"""
    
    def __init__(self):
        """Inicializa el controlador de presupuestos"""
        self.excel_manager = ExcelManager()
    
    def crear_presupuesto(self, cliente, items=None, validez=15, notas=""):
        """
        Crea un nuevo presupuesto
        
        Args:
            cliente: Cliente para el presupuesto
            items (list, optional): Lista de items para el presupuesto. Defaults to None.
            validez (int, optional): Días de validez. Defaults to 15.
            notas (str, optional): Notas adicionales. Defaults to "".
            
        Returns:
            Presupuesto: Objeto presupuesto creado
        """
        try:
            # Generar ID único para el presupuesto
            id_presupuesto = int(datetime.datetime.now().timestamp())
            
            # Fecha actual en formato DD/MM/AAAA
            fecha = datetime.datetime.now().strftime("%d/%m/%Y")
            
            # Crear el presupuesto
            nuevo_presupuesto = Presupuesto(
                id=id_presupuesto,
                cliente=cliente,
                fecha=fecha,
                validez=validez,
                items=items if items is not None else [],
                notas=notas
            )
            
            # Guardar en Excel
            self.excel_manager.guardar_presupuesto(nuevo_presupuesto)
            
            return nuevo_presupuesto
        except Exception as e:
            print(f"Error al crear presupuesto: {str(e)}")
            return None
    
    def obtener_presupuestos(self, filtros=None):
        """
        Obtiene todos los presupuestos, con opción de filtrar
        
        Args:
            filtros (dict, optional): Diccionario con filtros a aplicar. Defaults to None.
            
        Returns:
            DataFrame: DataFrame con los presupuestos
        """
        try:
            # Implementación provisional: devolver DataFrame vacío
            return pd.DataFrame(columns=['id', 'cliente_id', 'fecha', 'validez', 'total', 'notas', 'estado'])
        except Exception as e:
            print(f"Error al obtener presupuestos: {str(e)}")
            return pd.DataFrame()  # Devolver DataFrame vacío en caso de error
    
    def obtener_presupuesto_completo(self, presupuesto_id):
        """
        Obtiene un presupuesto completo por su ID, incluyendo items
        
        Args:
            presupuesto_id: ID del presupuesto
            
        Returns:
            Presupuesto: Objeto presupuesto o None si no se encuentra
        """
        try:
            # Implementación provisional: devolver None
            return None
        except Exception as e:
            print(f"Error al obtener presupuesto completo: {str(e)}")
            return None
    
    def actualizar_estado_presupuesto(self, presupuesto_id, nuevo_estado):
        """
        Actualiza el estado de un presupuesto
        
        Args:
            presupuesto_id: ID del presupuesto
            nuevo_estado (str): Nuevo estado ("Pendiente", "Aceptado" o "Rechazado")
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Implementación provisional
            return True
        except Exception as e:
            print(f"Error al actualizar estado del presupuesto: {str(e)}")
            return False
    
    def agregar_item(self, presupuesto_id, descripcion, cantidad, precio_unitario, descuento=0):
        """Agrega un nuevo ítem a un presupuesto existente"""
        presupuesto = self.obtener_presupuesto_completo(presupuesto_id)
        
        if not presupuesto:
            return False, "Presupuesto no encontrado"
        
        # Generar ID para el ítem
        item_id = int(datetime.datetime.now().timestamp())
        
        # Crear el ítem
        nuevo_item = ItemPresupuesto(item_id, descripcion, cantidad, precio_unitario, descuento)
        
        # Agregar al presupuesto
        presupuesto.agregar_item(nuevo_item)
        
        # Guardar cambios
        self.excel_manager.guardar_presupuesto(presupuesto)
        
        return True, nuevo_item
    
    def eliminar_item(self, presupuesto_id, item_id):
        """Elimina un ítem de un presupuesto"""
        presupuesto = self.obtener_presupuesto_completo(presupuesto_id)
        
        if not presupuesto:
            return False, "Presupuesto no encontrado"
        
        # Eliminar el ítem
        presupuesto.eliminar_item(item_id)
        
        # Guardar cambios
        self.excel_manager.guardar_presupuesto(presupuesto)
        
        return True, "Ítem eliminado correctamente"
    
    def actualizar_notas(self, presupuesto_id, nuevas_notas):
        """Actualiza las notas de un presupuesto"""
        presupuesto = self.obtener_presupuesto_completo(presupuesto_id)
        
        if not presupuesto:
            return False, "Presupuesto no encontrado"
        
        # Actualizar notas
        presupuesto.notas = nuevas_notas
        
        # Guardar cambios
        self.excel_manager.guardar_presupuesto(presupuesto)
        
        return True, "Notas actualizadas correctamente"
    
    def generar_presupuesto_pdf(self, presupuesto_id, ruta_salida=None):
        """Genera un PDF con el presupuesto (esta función requeriría una biblioteca como reportlab)"""
        presupuesto = self.obtener_presupuesto_completo(presupuesto_id)
        
        if not presupuesto:
            return False, "Presupuesto no encontrado"
        
        # Aquí iría la lógica para generar un PDF con reportlab u otra biblioteca
        # Por ahora, retornamos un mensaje indicando que no está implementado
        return False, "Generación de PDF no implementada" 