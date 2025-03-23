import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import uuid
from datetime import datetime, timedelta

# Agregar el directorio principal al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.controllers.cliente_controller import ClienteController
from app.controllers.producto_controller import ProductoController
from app.controllers.presupuesto_controller import PresupuestoController
from app.models.presupuesto import Presupuesto, ItemPresupuesto

def abrir_dialogo_presupuesto(parent, callback_guardado=None):
    """
    Abre un diálogo para crear un nuevo presupuesto
    
    Args:
        parent: Ventana padre
        callback_guardado: Función a ejecutar cuando se guarde el presupuesto
    """
    PresupuestoDialog(parent, callback_guardado=callback_guardado)
    
def abrir_dialogo_editar_presupuesto(parent, presupuesto_id, callback_guardado=None):
    """
    Abre un diálogo para editar un presupuesto existente
    
    Args:
        parent: Ventana padre
        presupuesto_id: ID del presupuesto a editar
        callback_guardado: Función a ejecutar cuando se guarde el presupuesto
    """
    PresupuestoDialog(parent, presupuesto_id=presupuesto_id, callback_guardado=callback_guardado)

class PresupuestoDialog:
    """Diálogo para crear o editar un presupuesto"""
    
    def __init__(self, parent, presupuesto_id=None, callback_guardado=None):
        """
        Inicializa el diálogo
        
        Args:
            parent: Ventana padre
            presupuesto_id: ID del presupuesto a editar (None para nuevo presupuesto)
            callback_guardado: Función a ejecutar cuando se guarde el presupuesto
        """
        self.parent = parent
        self.presupuesto_id = presupuesto_id
        self.callback_guardado = callback_guardado
        
        # Controladores
        self.cliente_controller = ClienteController()
        self.producto_controller = ProductoController()
        self.presupuesto_controller = PresupuestoController()
        
        # Listas de clientes y productos
        self.clientes = self.cliente_controller.obtener_clientes()
        self.productos = self.producto_controller.obtener_productos()
        
        # Presupuesto
        self.presupuesto = None
        if presupuesto_id:
            self.presupuesto = self.presupuesto_controller.obtener_presupuesto_completo(presupuesto_id)
            if not self.presupuesto:
                messagebox.showerror("Error", f"No se encontró el presupuesto con ID {presupuesto_id}")
                return
        
        # Items del presupuesto
        self.items_presupuesto = []
        if self.presupuesto:
            self.items_presupuesto = self.presupuesto.items.copy()
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Presupuesto" if not presupuesto_id else "Editar Presupuesto")
        self.dialog.geometry("800x600")
        self.dialog.minsize(800, 600)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        self.main_frame = ttk.Frame(self.dialog, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear diálogo básico con un mensaje
        ttk.Label(self.main_frame, 
                 text="Diálogo para Presupuestos - En desarrollo", 
                 font=("Helvetica", 14, "bold")).pack(pady=20)
        
        ttk.Label(self.main_frame, 
                 text="Este módulo está actualmente en desarrollo.\nPronto estará disponible la funcionalidad completa.", 
                 font=("Helvetica", 12)).pack(pady=20)
        
        # Botón para cerrar
        ttk.Button(self.main_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(pady=20)


# Para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba PresupuestoDialog")
    root.geometry("800x600")
    
    def on_presupuesto_saved(presupuesto):
        print(f"Presupuesto guardado: ID={presupuesto.id}, Total=${presupuesto.total:.2f}")
    
    ttk.Button(root, text="Nuevo Presupuesto", 
              command=lambda: abrir_dialogo_presupuesto(root, on_presupuesto_saved)).pack(pady=20)
    
    root.mainloop() 