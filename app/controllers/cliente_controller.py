import sys
import os
import datetime

# Agregar directorio principal al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.cliente import Cliente
from app.utils.excel_manager import ExcelManager

class ClienteController:
    def __init__(self):
        self.excel_manager = ExcelManager()
    
    def crear_cliente(self, nombre, apellido, email=None, telefono=None, direccion=None):
        """Crea un nuevo cliente y lo guarda en Excel"""
        # Generar un ID único para el cliente (usando timestamp como ejemplo)
        id_cliente = int(datetime.datetime.now().timestamp())
        
        # Crear el cliente
        nuevo_cliente = Cliente(id_cliente, nombre, apellido, email, telefono, direccion)
        
        # Guardar en Excel
        self.excel_manager.guardar_cliente(nuevo_cliente)
        
        return nuevo_cliente
    
    def obtener_clientes(self, filtros=None):
        """Obtiene todos los clientes con filtros opcionales"""
        return self.excel_manager.obtener_clientes(filtros)
    
    def obtener_cliente_por_id(self, cliente_id):
        """Obtiene un cliente por su ID"""
        df_clientes = self.excel_manager.obtener_clientes()
        
        # Buscar el cliente específico
        cliente_filtrado = df_clientes[df_clientes['id'] == cliente_id]
        
        if cliente_filtrado.empty:
            return None
        
        # Crear objeto Cliente
        row = cliente_filtrado.iloc[0]
        cliente = Cliente(
            row['id'],
            row['nombre'],
            row['apellido'],
            row.get('email'),
            row.get('telefono'),
            row.get('direccion')
        )
        
        return cliente
    
    def actualizar_cliente(self, cliente_id, nombre=None, apellido=None, email=None, telefono=None, direccion=None):
        """Actualiza los datos de un cliente existente"""
        cliente = self.obtener_cliente_por_id(cliente_id)
        
        if not cliente:
            return False, "Cliente no encontrado"
        
        # Actualizar solo los campos proporcionados
        if nombre:
            cliente.nombre = nombre
        if apellido:
            cliente.apellido = apellido
            
        # Actualizar datos adicionales
        cliente.actualizar_datos(email, telefono, direccion)
        
        # Guardar cambios
        self.excel_manager.guardar_cliente(cliente)
        
        return True, "Cliente actualizado correctamente"
    
    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente (en realidad, podríamos marcarlo como inactivo)"""
        cliente = self.obtener_cliente_por_id(cliente_id)
        
        if not cliente:
            return False, "Cliente no encontrado"
        
        # Aquí podríamos agregar lógica para marcar como inactivo en lugar de eliminar
        # Por ahora, lo eliminamos del DataFrame
        
        df_clientes = self.excel_manager.obtener_clientes()
        df_clientes = df_clientes[df_clientes['id'] != cliente_id]
        
        # Guardar el DataFrame actualizado
        df_clientes.to_excel(self.excel_manager.clientes_file, index=False)
        
        return True, "Cliente eliminado correctamente" 