import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import sys
import os

# Agregar el directorio principal al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.controllers.producto_controller import ProductoController
from app.models.producto import Producto

def abrir_dialogo_producto(parent, callback_guardado=None):
    """
    Abre un diálogo para crear un nuevo producto
    
    Args:
        parent: Ventana padre
        callback_guardado: Función a ejecutar cuando se guarde el producto
    """
    ProductoDialog(parent, callback_guardado=callback_guardado)
    
def abrir_dialogo_editar_producto(parent, producto_id, callback_guardado=None):
    """
    Abre un diálogo para editar un producto existente
    
    Args:
        parent: Ventana padre
        producto_id: ID del producto a editar
        callback_guardado: Función a ejecutar cuando se guarde el producto
    """
    ProductoDialog(parent, producto_id=producto_id, callback_guardado=callback_guardado)

class ProductoDialog:
    """Diálogo para crear o editar un producto"""
    
    def __init__(self, parent, producto_id=None, callback_guardado=None):
        """
        Inicializa el diálogo
        
        Args:
            parent: Ventana padre
            producto_id: ID del producto a editar (None para nuevo producto)
            callback_guardado: Función a ejecutar cuando se guarde el producto
        """
        self.parent = parent
        self.producto_id = producto_id
        self.callback_guardado = callback_guardado
        self.producto_controller = ProductoController()
        self.producto = None
        
        # Si tenemos ID, cargar el producto
        if producto_id:
            self.producto = self.producto_controller.obtener_producto_por_id(producto_id)
            if not self.producto:
                messagebox.showerror("Error", f"No se encontró el producto con ID {producto_id}")
                return
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Producto" if not producto_id else "Editar Producto")
        self.dialog.geometry("500x400")
        self.dialog.minsize(500, 400)
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
        
        # Crear interfaz
        self.crear_formulario()
        self.crear_botones()
        
        # Si estamos editando, cargar datos del producto
        if self.producto:
            self.cargar_datos_producto()
    
    def crear_formulario(self):
        """Crea el formulario de producto"""
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Campos obligatorios
        ttk.Label(form_frame, text="* Campos obligatorios", 
                 font=("Helvetica", 9, "italic")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=(0, 10))
        
        # Nombre
        ttk.Label(form_frame, text="Nombre: *").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.nombre_entry = ttk.Entry(form_frame, width=40)
        self.nombre_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.descripcion_text = tk.Text(form_frame, width=40, height=5)
        self.descripcion_text.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Precio de compra
        ttk.Label(form_frame, text="Precio de Compra: *").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.precio_compra_entry = ttk.Entry(form_frame, width=15)
        self.precio_compra_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Precio de venta
        ttk.Label(form_frame, text="Precio de Venta: *").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.precio_venta_entry = ttk.Entry(form_frame, width=15)
        self.precio_venta_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Margen de ganancia (calculado)
        ttk.Label(form_frame, text="Margen de Ganancia:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.margen_label = ttk.Label(form_frame, text="0%")
        self.margen_label.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Conectar eventos para calcular el margen
        self.precio_compra_entry.bind("<KeyRelease>", self.calcular_margen)
        self.precio_venta_entry.bind("<KeyRelease>", self.calcular_margen)
    
    def calcular_margen(self, event=None):
        """Calcula el margen de ganancia basado en los precios ingresados"""
        try:
            precio_compra = float(self.precio_compra_entry.get() or 0)
            precio_venta = float(self.precio_venta_entry.get() or 0)
            
            if precio_compra <= 0:
                self.margen_label.config(text="0%")
                return
            
            margen = ((precio_venta - precio_compra) / precio_compra) * 100
            self.margen_label.config(text=f"{margen:.2f}%")
        except ValueError:
            self.margen_label.config(text="0%")
    
    def crear_botones(self):
        """Crea los botones de acción"""
        botones_frame = ttk.Frame(self.main_frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        # Estilo personalizado para botones más grandes
        style = ttk.Style()
        style.configure("Grande.TButton", padding=(10, 5), font=("Helvetica", 10))
        
        cancelar_btn = ttk.Button(botones_frame, text="Cancelar", style="Grande.TButton", 
                                command=self.dialog.destroy)
        cancelar_btn.pack(side=tk.RIGHT, padx=5)
        
        guardar_btn = ttk.Button(botones_frame, text="Guardar", style="Grande.TButton", 
                               command=self.guardar_producto)
        guardar_btn.pack(side=tk.RIGHT, padx=5)
    
    def cargar_datos_producto(self):
        """Carga los datos del producto en el formulario"""
        if not self.producto:
            return
        
        self.nombre_entry.insert(0, self.producto.nombre)
        self.descripcion_text.insert("1.0", self.producto.descripcion)
        self.precio_compra_entry.insert(0, str(self.producto.precio_compra))
        self.precio_venta_entry.insert(0, str(self.producto.precio_venta))
        
        # Calcular margen inicial
        self.calcular_margen()
    
    def guardar_producto(self):
        """Guarda el producto en la base de datos"""
        # Validar campos obligatorios
        if not self.nombre_entry.get().strip():
            messagebox.showwarning("Guardar Producto", "El nombre es obligatorio")
            return
        
        try:
            precio_compra = float(self.precio_compra_entry.get() or 0)
        except ValueError:
            messagebox.showwarning("Guardar Producto", "El precio de compra debe ser un número")
            return
        
        try:
            precio_venta = float(self.precio_venta_entry.get() or 0)
        except ValueError:
            messagebox.showwarning("Guardar Producto", "El precio de venta debe ser un número")
            return
        
        # Crear producto
        nuevo_producto = Producto(
            id=self.producto.id if self.producto else str(uuid.uuid4())[:8],
            nombre=self.nombre_entry.get().strip(),
            descripcion=self.descripcion_text.get("1.0", tk.END).strip(),
            precio_compra=precio_compra,
            precio_venta=precio_venta
        )
        
        # Guardar producto
        if self.producto:
            resultado, mensaje = self.producto_controller.actualizar_producto(self.producto.id, nuevo_producto)
        else:
            resultado, mensaje = self.producto_controller.crear_producto(nuevo_producto)
        
        if resultado:
            messagebox.showinfo("Guardar Producto", mensaje)
            
            # Si hay callback, ejecutarlo
            if self.callback_guardado:
                self.callback_guardado(nuevo_producto)
            
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje) 