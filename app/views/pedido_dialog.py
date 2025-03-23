import sys
import os
import uuid
import traceback
import pandas as pd
from datetime import datetime

# Agregar el directorio principal al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import tkinter as tk
from tkinter import ttk, messagebox

from app.controllers.cliente_controller import ClienteController
from app.controllers.pedido_controller import PedidoController
from app.controllers.producto_controller import ProductoController
from app.models.pedido import Pedido, ItemPedido
from app.views.cliente_dialog import abrir_dialogo_cliente

class PedidoDialog:
    """Diálogo para crear o editar pedidos"""
    
    def __init__(self, parent, editar_pedido=None, callback=None):
        """
        Inicializa el diálogo para pedidos
        
        Args:
            parent: Ventana padre
            editar_pedido: Pedido a editar (None si es nuevo)
            callback: Función a llamar después de guardar
        """
        self.root = tk.Toplevel(parent)
        self.root.title("Nuevo Pedido" if editar_pedido is None else "Editar Pedido")
        self.root.geometry("800x650")  # Reducimos un poco la altura
        self.root.resizable(True, True)
        self.root.grab_set()  # Hacer la ventana modal
        
        # Inicializar controladores
        self.cliente_controller = ClienteController()
        self.pedido_controller = PedidoController()
        self.producto_controller = ProductoController()
        
        # Inicializar variables
        self.callback = callback
        self.editar_pedido = editar_pedido
        self.pedido_id = self.editar_pedido.id if self.editar_pedido else str(uuid.uuid4())
        self.items = self.editar_pedido.items if self.editar_pedido else []
        
        # Inicializar listas de clientes
        self.clientes = None
        self.cliente_nombres = []
        self.cliente_ids = []
        self.inicializar_clientes()
        
        # Inicializar listas de productos
        self.productos_nombres = []
        self.productos_ids = []
        self.productos_df = None
        self.inicializar_productos()
        
        # Variable para guardar el cliente seleccionado
        self.cliente_seleccionado = None
        
        if self.editar_pedido:
            self.cliente_seleccionado = self.editar_pedido.cliente
        
        # Crear la interfaz
        self.crear_interfaz()
    
    def inicializar_clientes(self):
        """Inicializa la lista de clientes desde el controlador"""
        print("[PedidoDialog] Inicializando clientes...")
        try:
            df_clientes = self.cliente_controller.obtener_clientes()
            print(f"[PedidoDialog] Clientes obtenidos: {len(df_clientes)}")
            
            if df_clientes.empty:
                print("[PedidoDialog] ERROR: No se encontraron clientes")
                messagebox.showwarning("Sin clientes", "No hay clientes disponibles en el sistema. Por favor, agregue clientes primero.")
                self.cliente_nombres = ["No hay clientes disponibles"]
                self.cliente_ids = []
                return
            
            # Verificar si tenemos las columnas necesarias
            print(f"[PedidoDialog] Columnas disponibles: {df_clientes.columns.tolist()}")
            
            # Limpiar listas existentes
            self.cliente_nombres = []
            self.cliente_ids = []
            
            # Iterar sobre clientes y agregar a las listas
            for index, row in df_clientes.iterrows():
                if 'id' not in row:
                    print(f"[PedidoDialog] Cliente sin ID: {row}")
                    continue
                
                cliente_id = row['id']
                
                # Obtener nombre para mostrar
                nombre_mostrar = None
                if 'nombre' in row and 'apellido' in row and not pd.isna(row['nombre']) and not pd.isna(row['apellido']):
                    nombre_mostrar = f"{row['nombre']} {row['apellido']}"
                elif 'nombre' in row and not pd.isna(row['nombre']):
                    nombre_mostrar = row['nombre']
                else:
                    nombre_mostrar = f"Cliente {index+1}"
                
                # Crear nombre formateado para mostrar en combobox
                nombre_formateado = f"{nombre_mostrar} - {cliente_id}"
                
                self.cliente_nombres.append(nombre_formateado)
                self.cliente_ids.append(cliente_id)
                
            print(f"[PedidoDialog] Clientes cargados: {len(self.cliente_nombres)}")
            print(f"[PedidoDialog] Nombres: {self.cliente_nombres}")
            print(f"[PedidoDialog] IDs: {self.cliente_ids}")
            
        except Exception as e:
            print(f"[PedidoDialog] Error al inicializar clientes: {str(e)}")
            traceback.print_exc()
            self.cliente_nombres = ["Error al cargar clientes"]
            self.cliente_ids = []
    
    def crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear interfaz
        self.crear_formulario_cliente()
        self.crear_tabla_items()
        self.crear_formulario_producto()
        self.crear_botones()
        
        # Si estamos editando, cargar datos del pedido
        if self.editar_pedido:
            self.cargar_datos_pedido()
    
    def crear_formulario_cliente(self):
        """Crea el formulario para seleccionar el cliente"""
        cliente_frame = tk.LabelFrame(self.root, text="Información del Cliente", padx=10, pady=5, bg="#f0f0f0")
        cliente_frame.pack(fill="x", padx=20, pady=5)
        
        # Primera fila - Selección de cliente
        tk.Label(cliente_frame, text="Cliente *:", bg="#f0f0f0").grid(row=0, column=0, sticky="w")
        
        # Verificar si hay clientes disponibles
        print(f"[PedidoDialog] Creando combobox de clientes con {len(self.cliente_nombres)} clientes")
        
        # Si no hay clientes, mostrar mensaje de advertencia
        if not self.cliente_nombres:
            print("[PedidoDialog] No hay clientes disponibles para mostrar en el combobox")
            messagebox.showwarning("Sin clientes", "No hay clientes disponibles. Por favor, agregue un cliente primero.")
        
        # Usar la lista de clientes ya inicializada
        values = self.cliente_nombres if self.cliente_nombres else ["No hay clientes disponibles"]
        
        self.cliente_combo = ttk.Combobox(
            cliente_frame, 
            values=values,
            width=40
        )
        self.cliente_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Botón para agregar cliente
        tk.Button(
            cliente_frame, 
            text="Nuevo Cliente", 
            command=self.crear_cliente,
            bg="#4CAF50",
            fg="white",
            width=15
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Segunda fila - Fecha y Estado (en una sola línea para ahorrar espacio)
        tk.Label(cliente_frame, text="Fecha:", bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        
        # Obtener fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        self.fecha_entry = tk.Entry(cliente_frame, width=15)
        self.fecha_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.fecha_entry.insert(0, fecha_actual)
        
        tk.Label(cliente_frame, text="Estado:", bg="#f0f0f0").grid(row=1, column=1, padx=(130, 0), sticky="e")
        self.estado_combo = ttk.Combobox(
            cliente_frame, 
            values=["Pendiente", "En proceso", "Completado", "Cancelado"],
            width=15
        )
        self.estado_combo.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.estado_combo.current(0)  # Seleccionar "Pendiente" por defecto
        
        # Tercera fila - Notas (reducida)
        tk.Label(cliente_frame, text="Notas:", bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        self.notas_text = tk.Text(cliente_frame, height=2, width=52)
        self.notas_text.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
    
    def crear_tabla_items(self):
        """Crea la tabla para mostrar los items del pedido"""
        items_frame = ttk.LabelFrame(self.main_frame, text="Productos del Pedido", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tabla de items
        columns = ("producto", "cantidad", "precio", "descuento", "subtotal")
        self.items_tabla = ttk.Treeview(items_frame, columns=columns, show="headings", selectmode="browse", height=10)
        
        # Configurar columnas
        self.items_tabla.heading("producto", text="Producto")
        self.items_tabla.heading("cantidad", text="Cantidad")
        self.items_tabla.heading("precio", text="Precio Unit.")
        self.items_tabla.heading("descuento", text="Descuento %")
        self.items_tabla.heading("subtotal", text="Subtotal")
        
        self.items_tabla.column("producto", width=300)
        self.items_tabla.column("cantidad", width=80)
        self.items_tabla.column("precio", width=100)
        self.items_tabla.column("descuento", width=100)
        self.items_tabla.column("subtotal", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tabla.yview)
        self.items_tabla.configure(yscroll=scrollbar.set)
        
        # Botones de acción
        botones_frame = ttk.Frame(items_frame)
        botones_frame.pack(fill=tk.X, pady=5)
        
        # Estilo para botones
        style = ttk.Style()
        style.configure("Tabla.TButton", padding=(5, 3), font=("Helvetica", 9))
        
        # Botones con estilo mejorado
        btn_eliminar = ttk.Button(botones_frame, text="Eliminar Seleccionado", 
                                 style="Tabla.TButton", command=self.eliminar_item)
        btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        btn_editar = ttk.Button(botones_frame, text="Editar Seleccionado", 
                               style="Tabla.TButton", command=self.editar_item)
        btn_editar.pack(side=tk.LEFT, padx=5)
        
        # Label para el total
        self.total_label = ttk.Label(botones_frame, text="Total: $0.00", font=("Helvetica", 12, "bold"))
        self.total_label.pack(side=tk.RIGHT, padx=10)
        
        # Empaquetar tabla y scrollbar
        self.items_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def crear_formulario_producto(self):
        """Crea el formulario para seleccionar y agregar productos"""
        producto_frame = tk.LabelFrame(self.main_frame, text="Agregar Producto (Obligatorio)", padx=10, pady=5, bg="#f0f0f0")
        producto_frame.pack(fill="x", padx=20, pady=5)
        
        # Borde rojo para indicar que es obligatorio
        producto_frame.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        
        # Mensaje de advertencia sobre productos obligatorios
        self.contador_productos = tk.Label(
            producto_frame, 
            text="Productos agregados: 0 (Debe agregar al menos 1 producto)", 
            bg="#f0f0f0", 
            fg="red", 
            font=("Arial", 10, "bold")
        )
        self.contador_productos.grid(row=0, column=0, columnspan=3, pady=(0, 5), sticky="w")

        # Layout más compacto: 3 columnas para ahorrar espacio
        # Primera columna: etiquetas
        # Segunda columna: campos de entrada
        # Tercera columna: botones
        
        # Primera fila - Selección de producto
        tk.Label(producto_frame, text="Producto *:", bg="#f0f0f0").grid(row=1, column=0, sticky="w")
        
        # Verificar si hay productos disponibles
        print(f"[PedidoDialog] Creando combobox con {len(self.productos_nombres)} productos")
        
        # Preparar valores para el combobox
        values = self.productos_nombres if self.productos_nombres else ["No hay productos disponibles"]
        
        # Crear combobox con búsqueda
        self.producto_combobox = ttk.Combobox(
            producto_frame, 
            values=values,
            width=40
        )
        self.producto_combobox.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        
        # Segunda fila - Cantidad y Descuento (en una línea) y botón Agregar
        tk.Label(producto_frame, text="Cantidad *:", bg="#f0f0f0").grid(row=2, column=0, sticky="w")
        
        # Frame para contener cantidad y descuento en una línea
        entradas_frame = tk.Frame(producto_frame, bg="#f0f0f0")
        entradas_frame.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        
        self.cantidad_entry = tk.Entry(entradas_frame, width=8)
        self.cantidad_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.cantidad_entry.insert(0, "1")  # Valor por defecto
        
        tk.Label(entradas_frame, text="Descuento (%):", bg="#f0f0f0").pack(side=tk.LEFT, padx=(10, 5))
        self.descuento_entry = tk.Entry(entradas_frame, width=8)
        self.descuento_entry.pack(side=tk.LEFT)
        self.descuento_entry.insert(0, "0")  # Valor por defecto
        
        # Botón de agregar producto (ahora a la derecha del descuento)
        self.agregar_btn = tk.Button(
            entradas_frame,
            text="Agregar",
            command=self.agregar_producto,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            width=12,
            height=1
        )
        self.agregar_btn.pack(side=tk.LEFT, padx=(15, 0))
    
    def crear_botones(self):
        """Crea los botones de acción"""
        botones_frame = ttk.Frame(self.main_frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        # Estilo personalizado para botones más pequeños
        style = ttk.Style()
        style.configure("Pequeno.TButton", padding=(5, 3), font=("Helvetica", 9))
        
        # Crear botones más pequeños y sin descripciones
        btn_cancelar = ttk.Button(
            botones_frame, 
            text="Cancelar", 
            style="Pequeno.TButton", 
            width=12, 
            command=self.root.destroy
        )
        btn_cancelar.pack(side=tk.RIGHT, padx=5)
        
        btn_guardar = ttk.Button(
            botones_frame, 
            text="Confirmar y Guardar", 
            style="Pequeno.TButton", 
            width=16, 
            command=self.guardar_pedido
        )
        btn_guardar.pack(side=tk.RIGHT, padx=5)
        
        btn_vista_previa = ttk.Button(
            botones_frame, 
            text="Vista Previa", 
            style="Pequeno.TButton", 
            width=12, 
            command=self.vista_previa_pedido
        )
        btn_vista_previa.pack(side=tk.RIGHT, padx=5)
    
    def inicializar_productos(self):
        """Inicializa la lista de productos desde el controlador"""
        print("[PedidoDialog] Inicializando productos...")
        try:
            self.productos_df = self.producto_controller.obtener_productos()
            print(f"[PedidoDialog] Productos obtenidos: {len(self.productos_df)}")
            
            if self.productos_df.empty:
                print("[PedidoDialog] ERROR: No se encontraron productos")
                messagebox.showwarning("Sin productos", "No hay productos disponibles en el sistema. Por favor, agregue productos primero.")
                self.productos_nombres = ["No hay productos disponibles"]
                self.productos_ids = []
                return
            
            # Verificar si tenemos las columnas necesarias
            print(f"[PedidoDialog] Columnas disponibles: {self.productos_df.columns.tolist()}")
            
            # Limpiar listas existentes
            self.productos_nombres = []
            self.productos_ids = []
            
            # Iterar sobre productos y agregar a las listas
            for index, row in self.productos_df.iterrows():
                # Verificar si tenemos id y nombre o descripción
                if 'id' not in row:
                    print(f"[PedidoDialog] Producto sin ID: {row}")
                    continue
                
                producto_id = row['id']
                
                # Obtener nombre/descripción para mostrar
                nombre_mostrar = None
                if 'descripcion' in row and not pd.isna(row['descripcion']):
                    nombre_mostrar = row['descripcion']
                elif 'nombre' in row and not pd.isna(row['nombre']):
                    nombre_mostrar = row['nombre']
                else:
                    nombre_mostrar = f"Producto {index+1}"
                    
                # Obtener precio para mostrar
                precio = None
                if 'precio_venta' in row and not pd.isna(row['precio_venta']):
                    precio = row['precio_venta']
                elif 'precio' in row and not pd.isna(row['precio']):
                    precio = row['precio']
                elif 'precio_compra' in row and not pd.isna(row['precio_compra']):
                    precio = row['precio_compra']
                else:
                    precio = 0
                
                # Crear nombre formateado para mostrar en combobox
                nombre_formateado = f"{nombre_mostrar} - ${float(precio):.2f}" if precio is not None else nombre_mostrar
                
                self.productos_nombres.append(nombre_formateado)
                self.productos_ids.append(producto_id)
                
            print(f"[PedidoDialog] Productos cargados: {len(self.productos_nombres)}")
            print(f"[PedidoDialog] Nombres: {self.productos_nombres}")
            print(f"[PedidoDialog] IDs: {self.productos_ids}")
            
        except Exception as e:
            print(f"[PedidoDialog] Error al inicializar productos: {str(e)}")
            traceback.print_exc()
            self.productos_nombres = ["Error al cargar productos"]
            self.productos_ids = []
    
    def agregar_producto(self):
        """Agrega un producto a la lista de items"""
        try:
            print("[PedidoDialog] Intentando agregar producto...")
            
            # Verificar si hay productos disponibles
            if not self.productos_nombres or self.productos_nombres[0] == "No hay productos disponibles":
                messagebox.showwarning("Sin productos", "No hay productos disponibles para agregar.")
                return
            
            # Obtener el índice del producto seleccionado
            seleccion = self.producto_combobox.current()
            print(f"[PedidoDialog] Índice seleccionado: {seleccion}")
            
            # Si no hay selección, mostrar error
            if seleccion == -1:
                # Intentar buscar por texto
                texto_seleccionado = self.producto_combobox.get()
                print(f"[PedidoDialog] Texto seleccionado: {texto_seleccionado}")
                
                # Buscar en la lista de productos
                encontrado = False
                for i, nombre in enumerate(self.productos_nombres):
                    if texto_seleccionado in nombre:
                        seleccion = i
                        encontrado = True
                        break
                
                if not encontrado:
                    messagebox.showwarning("Producto no seleccionado", "Por favor, seleccione un producto de la lista.")
                    return
            
            # Verificar que el índice sea válido
            if seleccion < 0 or seleccion >= len(self.productos_ids):
                messagebox.showwarning("Selección inválida", "Por favor, seleccione un producto válido.")
                return
            
            # Obtener detalles del producto seleccionado
            producto_id = self.productos_ids[seleccion]
            producto_nombre = self.productos_nombres[seleccion]
            print(f"[PedidoDialog] Producto seleccionado - ID: {producto_id}, Nombre: {producto_nombre}")
            
            # Obtener información completa del producto del DataFrame
            producto_df_filtrado = self.productos_df[self.productos_df['id'] == producto_id]
            if producto_df_filtrado.empty:
                messagebox.showwarning("Error", f"No se encontró información del producto con ID {producto_id}")
                return
                
            producto_info = producto_df_filtrado.iloc[0]
            print(f"[PedidoDialog] Información del producto: {dict(producto_info)}")
            
            # Obtener precio (precio_venta o precio)
            precio = 0
            if 'precio_venta' in producto_info and not pd.isna(producto_info['precio_venta']):
                precio = float(producto_info['precio_venta'])
            elif 'precio' in producto_info and not pd.isna(producto_info['precio']):
                precio = float(producto_info['precio'])
            elif 'precio_compra' in producto_info and not pd.isna(producto_info['precio_compra']):
                # Si no hay precio de venta, usar el precio de compra como fallback
                precio = float(producto_info['precio_compra'])
            
            # Obtener descripción o nombre como fallback
            descripcion = ""
            if 'descripcion' in producto_info and not pd.isna(producto_info['descripcion']):
                descripcion = producto_info['descripcion']
            elif 'nombre' in producto_info:
                descripcion = producto_info['nombre']
            
            print(f"[PedidoDialog] Usando descripción: {descripcion}, precio: {precio}")
            
            # Obtener cantidad
            cantidad_texto = self.cantidad_entry.get()
            try:
                cantidad = int(cantidad_texto)
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0")
            except ValueError:
                messagebox.showwarning("Cantidad inválida", "Por favor, ingrese una cantidad válida mayor a 0.")
                return
            
            # Obtener descuento
            descuento_texto = self.descuento_entry.get()
            try:
                descuento = float(descuento_texto)
                if descuento < 0 or descuento > 100:
                    raise ValueError("El descuento debe estar entre 0 y 100")
            except ValueError:
                messagebox.showwarning("Descuento inválido", "Por favor, ingrese un descuento válido entre 0 y 100.")
                return
            
            # Calcular el subtotal manualmente para asegurar que esté correcto
            subtotal = cantidad * precio * (1 - descuento / 100)
            
            # Crear objeto ItemPedido y añadir a la lista
            nuevo_id = len(self.items) + 1
            item = ItemPedido(
                id=nuevo_id,
                producto_id=producto_id,
                descripcion=descripcion,
                cantidad=cantidad,
                precio_unitario=precio,
                descuento=descuento
            )
            
            # Verificar que el subtotal se ha calculado correctamente
            if hasattr(item, 'subtotal'):
                print(f"[PedidoDialog] Subtotal calculado en ItemPedido: {item.subtotal}")
            else:
                # Asignar manualmente si no se ha calculado
                item.subtotal = subtotal
                print(f"[PedidoDialog] Asignando subtotal manualmente: {subtotal}")
            
            # Añadir a la lista de items
            self.items.append(item)
            
            # Actualizar tabla y total
            self.actualizar_tabla_items()
            self.calcular_total()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Producto agregado", f"Se ha agregado {cantidad} unidad(es) de {descripcion} al pedido.")
            
            # Limpiar campos
            self.producto_combobox.set("")  # Limpiar selección
            self.cantidad_entry.delete(0, tk.END)
            self.cantidad_entry.insert(0, "1")  # Valor por defecto
            self.descuento_entry.delete(0, tk.END)
            self.descuento_entry.insert(0, "0")  # Valor por defecto
            
        except Exception as e:
            print(f"[PedidoDialog] Error al agregar producto: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
    
    def actualizar_tabla_items(self):
        """Actualiza la tabla de items del pedido"""
        # Limpiar tabla existente
        for item in self.items_tabla.get_children():
            self.items_tabla.delete(item)
        
        # Insertar filas con los nuevos datos
        print(f"[PedidoDialog] Actualizando tabla con {len(self.items)} ítems")
        
        for item in self.items:
            # Asegurar que el subtotal está calculado
            if not hasattr(item, 'subtotal') or item.subtotal is None:
                item.subtotal = item.calcular_subtotal()
                
            print(f"[PedidoDialog] Agregando a tabla: {item.descripcion}, {item.cantidad} x ${item.precio_unitario:.2f}")
            
            # Insertar ítem en la tabla
            self.items_tabla.insert("", "end", values=(
                item.descripcion,
                item.cantidad,
                f"${item.precio_unitario:.2f}",
                f"{item.descuento}%",
                f"${item.subtotal:.2f}"
            ))
        
        # Actualizar el contador de productos
        if hasattr(self, 'contador_productos'):
            texto = f"Productos agregados: {len(self.items)}"
            if len(self.items) == 0:
                texto += " (Debe agregar al menos 1 producto)"
                self.contador_productos.config(fg="red", font=("Arial", 10, "bold"))
            else:
                texto += " ✓"
                self.contador_productos.config(fg="green", font=("Arial", 10, "bold"))
            
            self.contador_productos.config(text=texto)
    
    def ver_detalle_item(self, item_id):
        """Muestra los detalles de un item"""
        # Buscar item
        item = next((item for item in self.items if item.id == item_id), None)
        if not item:
            messagebox.showerror("Error", "No se encontró el item seleccionado")
            return
        
        # Crear ventana de detalles
        detalle = tk.Toplevel(self.root)
        detalle.title("Detalle del Item")
        detalle.geometry("400x250")
        detalle.transient(self.root)
        detalle.grab_set()
        
        # Frame principal
        frame = ttk.Frame(detalle, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Descripción
        ttk.Label(frame, text="Producto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=item.descripcion).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Cantidad
        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=str(item.cantidad)).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Precio unitario
        ttk.Label(frame, text="Precio unitario:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=f"${item.precio_unitario:.2f}").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Descuento
        ttk.Label(frame, text="Descuento:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=f"{item.descuento}%").grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Subtotal
        ttk.Label(frame, text="Subtotal:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=f"${item.subtotal:.2f}").grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Botones
        botones_frame = ttk.Frame(frame)
        botones_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(botones_frame, text="Cerrar", command=detalle.destroy).pack(side=tk.RIGHT, padx=5)
    
    def eliminar_item(self):
        """Elimina el item seleccionado"""
        seleccion = self.items_tabla.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar Item", "Por favor, seleccione un item para eliminar")
            return
        
        # Obtener el índice del item seleccionado
        indice_seleccionado = self.items_tabla.index(seleccion[0])
        print(f"[PedidoDialog] Índice seleccionado para eliminar: {indice_seleccionado}")
        
        # Verificar que el índice sea válido
        if indice_seleccionado < 0 or indice_seleccionado >= len(self.items):
            messagebox.showerror("Error", "No se pudo identificar el item seleccionado")
            return
        
        # Obtener el item a eliminar
        item_a_eliminar = self.items[indice_seleccionado]
        print(f"[PedidoDialog] Eliminando item: {item_a_eliminar.descripcion}")
        
        # Confirmar eliminación
        confirmar = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro que desea eliminar '{item_a_eliminar.descripcion}'?"
        )
        
        if not confirmar:
            return
        
        # Eliminar el item de la lista
        self.items.pop(indice_seleccionado)
        
        # Actualizar la tabla y recalcular el total
        self.actualizar_tabla_items()
        self.calcular_total()
        
        messagebox.showinfo("Éxito", "Producto eliminado correctamente")
    
    def editar_item(self):
        """Edita el item seleccionado"""
        seleccion = self.items_tabla.selection()
        if not seleccion:
            messagebox.showwarning("Editar Item", "Por favor, seleccione un item para editar")
            return
        
        # Obtener el índice del item seleccionado
        indice_seleccionado = self.items_tabla.index(seleccion[0])
        print(f"[PedidoDialog] Índice seleccionado para editar: {indice_seleccionado}")
        
        # Verificar que el índice sea válido
        if indice_seleccionado < 0 or indice_seleccionado >= len(self.items):
            messagebox.showerror("Error", "No se pudo identificar el item seleccionado")
            return
        
        # Obtener el item a editar
        item = self.items[indice_seleccionado]
        print(f"[PedidoDialog] Editando item: {item.descripcion}")
        
        # Crear ventana de edición
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Editar Item")
        edit_dialog.geometry("400x200")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Centrar ventana
        edit_dialog.update_idletasks()
        width = edit_dialog.winfo_width()
        height = edit_dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        edit_dialog.geometry(f"+{x}+{y}")
        
        # Formulario
        frame = ttk.Frame(edit_dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Descripción
        ttk.Label(frame, text="Producto:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=item.descripcion).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Cantidad
        ttk.Label(frame, text="Cantidad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        cantidad_spinbox = ttk.Spinbox(frame, from_=1, to=1000, width=5)
        cantidad_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        cantidad_spinbox.set(item.cantidad)
        
        # Precio
        ttk.Label(frame, text="Precio Unit.:").grid(row=2, column=0, sticky=tk.W, pady=5)
        precio_spinbox = ttk.Spinbox(frame, from_=0, to=100000, width=10, increment=0.01)
        precio_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5)
        precio_spinbox.set(f"{item.precio_unitario:.2f}")
        
        # Descuento
        ttk.Label(frame, text="Descuento %:").grid(row=3, column=0, sticky=tk.W, pady=5)
        descuento_spinbox = ttk.Spinbox(frame, from_=0, to=100, width=5)
        descuento_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5)
        descuento_spinbox.set(item.descuento)
        
        # Botones
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Función para guardar cambios
        def guardar_cambios():
            try:
                cantidad = int(cantidad_spinbox.get())
                precio = float(precio_spinbox.get())
                descuento = float(descuento_spinbox.get())
                
                if cantidad <= 0:
                    messagebox.showwarning("Editar Item", "La cantidad debe ser mayor a 0")
                    return
                
                if precio < 0:
                    messagebox.showwarning("Editar Item", "El precio debe ser mayor o igual a 0")
                    return
                
                if descuento < 0 or descuento > 100:
                    messagebox.showwarning("Editar Item", "El descuento debe estar entre 0 y 100")
                    return
                
                # Actualizar item
                item.cantidad = cantidad
                item.precio_unitario = precio
                item.descuento = descuento
                item.subtotal = item.calcular_subtotal()
                
                print(f"[PedidoDialog] Item actualizado: {item.descripcion}, {cantidad} x ${precio:.2f} ({descuento}% desc.) = ${item.subtotal:.2f}")
                
                # Cerrar diálogo y actualizar tabla
                edit_dialog.destroy()
                self.actualizar_tabla_items()
                self.calcular_total()
                
                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                
            except ValueError:
                messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos")
        
        ttk.Button(buttons_frame, text="Guardar", command=guardar_cambios).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=edit_dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def crear_cliente(self):
        """Abre el diálogo para crear un nuevo cliente"""
        def actualizar_lista_clientes(cliente):
            """Callback cuando se crea un cliente nuevo"""
            print(f"Cliente creado: {cliente.nombre} {cliente.apellido}")
            
            # Reinicializar la lista de clientes
            self.inicializar_clientes()
            
            # Actualizar el combobox
            self.cliente_combo['values'] = self.cliente_nombres
            
            # Seleccionar el cliente recién creado
            for i, nombre in enumerate(self.cliente_nombres):
                if cliente.id in nombre:
                    self.cliente_combo.current(i)
                    break
        
        abrir_dialogo_cliente(self.root, actualizar_lista_clientes)
    
    def cargar_datos_pedido(self):
        """Carga los datos de un pedido existente"""
        if not self.editar_pedido:
            return
        
        # Seleccionar cliente
        for i, cliente_id in enumerate(self.cliente_ids):
            if cliente_id == self.editar_pedido.cliente_id:
                self.cliente_combo.current(i)
                break
        
        # Fecha
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, self.editar_pedido.fecha)
        
        # Estado
        estados = ["Pendiente", "En proceso", "Completado", "Cancelado"]
        for i, estado in enumerate(estados):
            if estado == self.editar_pedido.estado:
                self.estado_combo.current(i)
                break
        
        # Notas
        if self.editar_pedido.notas:
            self.notas_text.delete(1.0, tk.END)
            self.notas_text.insert(tk.END, self.editar_pedido.notas)
        
        # Items
        self.items = self.editar_pedido.items.copy()
        self.actualizar_tabla_items()
    
    def vista_previa_pedido(self):
        """Muestra una vista previa del pedido antes de guardar"""
        if not self.items:
            messagebox.showwarning("Vista Previa", "No se han agregado productos al pedido")
            return
        
        # Crear ventana de vista previa
        preview = tk.Toplevel(self.root)
        preview.title("Vista Previa del Pedido")
        preview.geometry("800x650")  # Mismas dimensiones que el formulario principal
        preview.transient(self.root)
        preview.grab_set()
        preview.resizable(True, True)  # Permitir redimensionar
        
        # Frame principal
        main_frame = ttk.Frame(preview, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Vista Previa del Pedido", font=("Helvetica", 14, "bold")).pack(side=tk.LEFT)
        
        # Panel superior con datos del cliente y pedido
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Datos del cliente (izquierda)
        cliente_frame = ttk.LabelFrame(top_frame, text="Datos del Cliente", padding=10)
        cliente_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Información del pedido (derecha)
        info_frame = ttk.LabelFrame(top_frame, text="Información del Pedido", padding=10)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Obtener selección de cliente
        cliente_seleccionado = self.cliente_combo.get()
        print(f"[PedidoDialog] Cliente seleccionado para vista previa: {cliente_seleccionado}")
        
        # Extraer el ID del cliente
        cliente_id = None
        nombre_cliente = cliente_seleccionado
        if " - " in cliente_seleccionado:
            partes = cliente_seleccionado.split(" - ")
            nombre_cliente = partes[0]
            cliente_id = partes[1] if len(partes) > 1 else None
            
        # Mostrar información del cliente
        ttk.Label(cliente_frame, text="Cliente:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(cliente_frame, text=nombre_cliente).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Obtener datos adicionales del cliente usando el cliente_controller
        row_cliente = 1
        if cliente_id:
            try:
                df_clientes = self.cliente_controller.obtener_clientes()
                cliente_filtrado = df_clientes[df_clientes['id'] == cliente_id]
                
                if not cliente_filtrado.empty:
                    cliente_data = cliente_filtrado.iloc[0]
                    
                    # Teléfono
                    if 'telefono' in cliente_data and not pd.isna(cliente_data['telefono']):
                        ttk.Label(cliente_frame, text="Teléfono:").grid(row=row_cliente, column=0, sticky=tk.W, pady=5)
                        ttk.Label(cliente_frame, text=str(cliente_data['telefono'])).grid(row=row_cliente, column=1, sticky=tk.W, pady=5)
                        row_cliente += 1
                    
                    # Dirección
                    if 'direccion' in cliente_data and not pd.isna(cliente_data['direccion']):
                        ttk.Label(cliente_frame, text="Dirección:").grid(row=row_cliente, column=0, sticky=tk.W, pady=5)
                        ttk.Label(cliente_frame, text=str(cliente_data['direccion'])).grid(row=row_cliente, column=1, sticky=tk.W, pady=5)
                        row_cliente += 1
                        
                    # Email
                    if 'email' in cliente_data and not pd.isna(cliente_data['email']):
                        ttk.Label(cliente_frame, text="Email:").grid(row=row_cliente, column=0, sticky=tk.W, pady=5)
                        ttk.Label(cliente_frame, text=str(cliente_data['email'])).grid(row=row_cliente, column=1, sticky=tk.W, pady=5)
                        row_cliente += 1
            except Exception as e:
                print(f"[PedidoDialog] Error al obtener datos del cliente: {str(e)}")
        
        # Mostrar información del pedido
        ttk.Label(info_frame, text="Fecha:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=self.fecha_entry.get()).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="Estado:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=self.estado_combo.get()).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Notas
        notas = self.notas_text.get(1.0, tk.END).strip()
        if notas:
            ttk.Label(info_frame, text="Notas:").grid(row=2, column=0, sticky=tk.NW, pady=5)
            
            # Crear un frame con text widget de solo lectura para mostrar las notas
            notas_frame = ttk.Frame(info_frame)
            notas_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
            
            notas_text = tk.Text(notas_frame, height=3, width=30, wrap=tk.WORD)
            notas_text.insert(tk.END, notas)
            notas_text.config(state=tk.DISABLED)  # Solo lectura
            notas_text.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbar para notas
            notas_scroll = ttk.Scrollbar(notas_frame, orient=tk.VERTICAL, command=notas_text.yview)
            notas_text.configure(yscrollcommand=notas_scroll.set)
            notas_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tabla de items (ocupa el espacio principal)
        items_frame = ttk.LabelFrame(main_frame, text="Productos", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear tabla
        items_tabla = ttk.Treeview(items_frame, columns=("producto", "cantidad", "precio", "descuento", "subtotal"), show="headings", height=12)
        items_tabla.heading("producto", text="Producto")
        items_tabla.heading("cantidad", text="Cantidad")
        items_tabla.heading("precio", text="Precio")
        items_tabla.heading("descuento", text="Descuento")
        items_tabla.heading("subtotal", text="Subtotal")
        
        items_tabla.column("producto", width=300)
        items_tabla.column("cantidad", width=80)
        items_tabla.column("precio", width=100)
        items_tabla.column("descuento", width=100)
        items_tabla.column("subtotal", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=items_tabla.yview)
        items_tabla.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        items_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Llenar tabla
        for item in self.items:
            items_tabla.insert("", "end", values=(
                item.descripcion,
                item.cantidad,
                f"${item.precio_unitario:.2f}",
                f"{item.descuento}%",
                f"${item.subtotal:.2f}"
            ))
        
        # Panel inferior con total y botones
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        # Total
        total = self.calcular_total()
        total_frame = ttk.Frame(bottom_frame)
        total_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(total_frame, text="Total:", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(total_frame, text=f"${total:.2f}", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones
        botones_frame = ttk.Frame(bottom_frame)
        botones_frame.pack(side=tk.RIGHT)
        
        ttk.Button(botones_frame, text="Volver", width=12, command=preview.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(botones_frame, text="Confirmar y Guardar", width=16, command=lambda: self.confirmar_desde_vista_previa(preview)).pack(side=tk.RIGHT, padx=5)
    
    def confirmar_desde_vista_previa(self, ventana):
        """Confirma la creación/edición del pedido desde la vista previa"""
        ventana.destroy()
        
        try:
            # Obtener ID del cliente
            cliente_seleccionado = self.cliente_combo.get()
            cliente_id = None
            
            if " - " in cliente_seleccionado:
                # Extraer el ID que está después del último guion
                partes = cliente_seleccionado.split(" - ")
                if len(partes) > 1:
                    cliente_id = partes[-1]  # Tomar el último elemento (ID)
                    
            print(f"[PedidoDialog] Guardando pedido para cliente ID: {cliente_id}")
            
            if not cliente_id:
                messagebox.showwarning("Guardar Pedido", "No se pudo determinar el ID del cliente. Por favor, seleccione un cliente válido.")
                return
            
            # Crear o actualizar pedido
            if self.editar_pedido:
                # Actualizar pedido existente
                self.editar_pedido.cliente_id = cliente_id
                self.editar_pedido.fecha = self.fecha_entry.get()
                self.editar_pedido.estado = self.estado_combo.get()
                self.editar_pedido.notas = self.notas_text.get(1.0, tk.END).strip()
                self.editar_pedido.items = self.items
                
                # Recalcular total
                self.editar_pedido.calcular_total()
                
                # Guardar (ahora devuelve el objeto pedido o None)
                print(f"[PedidoDialog] Actualizando pedido con ID: {self.editar_pedido.id}")
                resultado = self.pedido_controller.actualizar_pedido(self.editar_pedido)
                
                if resultado:
                    # El resultado ahora debería ser un objeto pedido
                    messagebox.showinfo("Éxito", "Pedido actualizado correctamente")
                    self.editar_pedido = resultado
                else:
                    messagebox.showwarning("Atención", "El pedido se actualizó pero no se pudo recuperar el objeto actualizado")
                    # Mantener el pedido original
            else:
                # Crear nuevo pedido
                pedido = Pedido(
                    id=None,  # Se asigna automáticamente
                    cliente_id=cliente_id,
                    fecha=self.fecha_entry.get(),
                    estado=self.estado_combo.get(),
                    items=self.items,
                    notas=self.notas_text.get(1.0, tk.END).strip()
                )
                
                # Guardar (ahora devuelve el objeto pedido o None)
                print(f"[PedidoDialog] Creando nuevo pedido")
                resultado = self.pedido_controller.crear_pedido(pedido)
                
                if resultado:
                    # El resultado ahora debería ser un objeto pedido con ID
                    messagebox.showinfo("Éxito", "Pedido creado correctamente con ID: " + resultado.id)
                    self.editar_pedido = resultado
                else:
                    messagebox.showwarning("Atención", "El pedido no pudo crearse correctamente")
                    self.editar_pedido = pedido  # Usar el pedido local como respaldo
            
            # Cerrar diálogo principal
            self.root.destroy()
            
            # Imprimir información sobre lo que vamos a enviar al callback
            print(f"[PedidoDialog] Pedido a enviar al callback: {self.editar_pedido}")
            if hasattr(self.editar_pedido, 'id'):
                print(f"[PedidoDialog] ID del pedido: {self.editar_pedido.id}")
            else:
                print(f"[PedidoDialog] El pedido no tiene atributo ID. Tipo: {type(self.editar_pedido)}")
            
            # Llamar al callback si existe
            if self.callback and self.editar_pedido and hasattr(self.editar_pedido, 'id'):
                self.callback(self.editar_pedido)
            else:
                print("[PedidoDialog] No se llamó al callback (no existe o el pedido no tiene ID)")
                
        except Exception as e:
            print(f"[PedidoDialog] Error al guardar el pedido: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al guardar el pedido: {str(e)}")
            
    def guardar_pedido(self):
        """Guarda el pedido con confirmación previa"""
        # Validar cliente
        if not self.cliente_combo.get():
            messagebox.showwarning("Guardar Pedido", "Por favor, seleccione un cliente")
            return
        
        # Validar items
        if not self.items:
            messagebox.showwarning("Guardar Pedido", "Por favor, agregue al menos un producto al pedido")
            return
            
        # Mostrar vista previa automáticamente
        self.vista_previa_pedido()

    def calcular_total(self):
        """Calcula el total del pedido y actualiza el campo correspondiente"""
        total = 0
        
        print(f"[PedidoDialog] Calculando total para {len(self.items)} items")
        
        for item in self.items:
            # Calcular el subtotal si no existe
            if not hasattr(item, 'subtotal') or item.subtotal is None:
                item.subtotal = item.cantidad * item.precio_unitario * (1 - item.descuento / 100)
                
            print(f"[PedidoDialog] Item: {item.descripcion}, Cantidad: {item.cantidad}, Precio: {item.precio_unitario}, Subtotal: {item.subtotal}")
            total += item.subtotal
        
        # Actualizar label de total
        if hasattr(self, 'total_label'):
            nuevo_texto = f"Total: ${total:.2f}"
            print(f"[PedidoDialog] Actualizando etiqueta de total a: {nuevo_texto}")
            self.total_label.config(text=nuevo_texto)
        
        # Actualizar contador de productos
        if hasattr(self, 'contador_productos'):
            texto = f"Productos agregados: {len(self.items)}"
            if len(self.items) == 0:
                texto += " (Debe agregar al menos 1 producto)"
                self.contador_productos.config(fg="red", font=("Arial", 10, "bold"))
            else:
                texto += " ✓"
                self.contador_productos.config(fg="green", font=("Arial", 10, "bold"))
            
            self.contador_productos.config(text=texto)
                
        # Guardar el total para usar en otros métodos
        self.total = total
        
        print(f"[PedidoDialog] Total calculado: {total:.2f}")
        return total


def abrir_dialogo_pedido(parent, callback=None):
    """Abre el diálogo para crear un nuevo pedido"""
    PedidoDialog(parent, callback=callback)


def abrir_dialogo_editar_pedido(parent, pedido, callback=None):
    """Abre el diálogo para editar un pedido existente"""
    PedidoDialog(parent, pedido, callback)
