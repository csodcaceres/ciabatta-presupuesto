import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Agregar el directorio principal al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.controllers.cliente_controller import ClienteController

class ClienteDialog:
    def __init__(self, parent, cliente=None, callback=None):
        """
        Inicializa la ventana de diálogo para añadir o editar clientes
        
        Args:
            parent: Ventana padre
            cliente: Cliente a editar (None si es un nuevo cliente)
            callback: Función a llamar cuando se guarde el cliente
        """
        self.parent = parent
        self.cliente = cliente
        self.callback = callback
        self.controller = ClienteController()
        
        # Crear una nueva ventana top-level
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Cliente" if not cliente else "Editar Cliente")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # Hace que la ventana sea hija de la principal
        self.dialog.grab_set()  # Hace que la ventana sea modal
        
        # Centrar la ventana con respecto a la principal
        self.centrar_ventana()
        
        # Crear el formulario
        self.crear_formulario()
        
        # Si se está editando un cliente existente, rellenar el formulario
        if cliente:
            self.rellenar_formulario()
    
    def centrar_ventana(self):
        """Centra la ventana de diálogo con respecto a la ventana principal"""
        # Actualizar la ventana para obtener su tamaño real
        self.dialog.update_idletasks()
        
        # Obtener dimensiones
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        
        # Calcular posición
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Posicionar ventana
        self.dialog.geometry(f"+{x}+{y}")
    
    def crear_formulario(self):
        """Crea el formulario para añadir/editar clientes"""
        # Contenedor principal
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = "Datos del Cliente"
        ttk.Label(main_frame, text=titulo, font=('Helvetica', 12, 'bold')).pack(pady=(0, 15))
        
        # Frame para los campos del formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos del formulario
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.nombre_entry = ttk.Entry(form_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Apellido:").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.apellido_entry = ttk.Entry(form_frame, width=30)
        self.apellido_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, pady=5, sticky=tk.W)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Teléfono:").grid(row=3, column=0, pady=5, sticky=tk.W)
        self.telefono_entry = ttk.Entry(form_frame, width=30)
        self.telefono_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        ttk.Label(form_frame, text="Dirección:").grid(row=4, column=0, pady=5, sticky=tk.W)
        self.direccion_entry = ttk.Entry(form_frame, width=30)
        self.direccion_entry.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)
        
        # Frame para los botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Botones
        ttk.Button(buttons_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Guardar", command=self.guardar_cliente).pack(side=tk.RIGHT, padx=5)
    
    def rellenar_formulario(self):
        """Rellena el formulario con los datos del cliente a editar"""
        self.nombre_entry.insert(0, self.cliente.nombre)
        self.apellido_entry.insert(0, self.cliente.apellido)
        
        if self.cliente.email:
            self.email_entry.insert(0, self.cliente.email)
        
        if self.cliente.telefono:
            self.telefono_entry.insert(0, self.cliente.telefono)
        
        if self.cliente.direccion:
            self.direccion_entry.insert(0, self.cliente.direccion)
    
    def validar_formulario(self):
        """Valida que los campos obligatorios estén rellenos"""
        if not self.nombre_entry.get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        if not self.apellido_entry.get().strip():
            messagebox.showerror("Error", "El apellido es obligatorio")
            return False
        
        return True
    
    def guardar_cliente(self):
        """Guarda el cliente en la base de datos"""
        if not self.validar_formulario():
            return
        
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        email = self.email_entry.get().strip() or None
        telefono = self.telefono_entry.get().strip() or None
        direccion = self.direccion_entry.get().strip() or None
        
        try:
            if self.cliente:  # Editar cliente existente
                resultado, mensaje = self.controller.actualizar_cliente(
                    self.cliente.id, nombre, apellido, email, telefono, direccion
                )
                if resultado:
                    messagebox.showinfo("Éxito", mensaje)
                    self.cliente = self.controller.obtener_cliente_por_id(self.cliente.id)
                    if self.callback:
                        self.callback(self.cliente)
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Error", mensaje)
            else:  # Nuevo cliente
                nuevo_cliente = self.controller.crear_cliente(
                    nombre, apellido, email, telefono, direccion
                )
                messagebox.showinfo("Éxito", "Cliente creado correctamente")
                if self.callback:
                    self.callback(nuevo_cliente)
                self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")


# Función de prueba para crear un cliente desde la ventana principal
def abrir_dialogo_cliente(parent, callback=None):
    """Abre el diálogo para crear un nuevo cliente"""
    ClienteDialog(parent, callback=callback)


# Función de prueba para editar un cliente desde la ventana principal
def abrir_dialogo_editar_cliente(parent, cliente, callback=None):
    """Abre el diálogo para editar un cliente existente"""
    ClienteDialog(parent, cliente, callback)


# Para pruebas
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Prueba ClienteDialog")
    root.geometry("600x400")
    
    def on_cliente_saved(cliente):
        print(f"Cliente guardado: {cliente.nombre} {cliente.apellido}")
    
    ttk.Button(root, text="Nuevo Cliente", 
              command=lambda: abrir_dialogo_cliente(root, on_cliente_saved)).pack(pady=20)
    
    root.mainloop() 