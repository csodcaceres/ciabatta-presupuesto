import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import pandas as pd

# Agregar el directorio principal al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.views.cliente_dialog import abrir_dialogo_cliente, abrir_dialogo_editar_cliente
from app.controllers.cliente_controller import ClienteController
from app.controllers.pedido_controller import PedidoController
from app.controllers.producto_controller import ProductoController
from app.controllers.presupuesto_controller import PresupuestoController
from app.views.pedido_dialog import abrir_dialogo_pedido, abrir_dialogo_editar_pedido
from app.views.presupuesto_dialog import abrir_dialogo_presupuesto, abrir_dialogo_editar_presupuesto
from app.views.producto_dialog import abrir_dialogo_producto, abrir_dialogo_editar_producto

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Pedidos - Ciabatta")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Inicializar controladores
        self.cliente_controller = ClienteController()
        self.pedido_controller = PedidoController()
        self.producto_controller = ProductoController()
        self.presupuesto_controller = PresupuestoController()
        
        # Variables
        self.filtro_pedido_var = tk.StringVar()
        self.filtro_cliente_var = tk.StringVar()
        self.filtro_producto_var = tk.StringVar()
        self.filtro_presupuesto_var = tk.StringVar()
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50")
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TNotebook.Tab", padding=[12, 6], font=('Helvetica', 10))
        
        # Barra de estado
        self.barra_estado = ttk.Label(self.root, text="Sistema listo", relief=tk.SUNKEN, anchor=tk.W)
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Crear interfaz
        self.crear_menu()
        self.crear_notebook()
        
        # Cargar datos iniciales
        self.cargar_datos_pedidos()
        self.cargar_datos_clientes()
        self.cargar_datos_productos()
        self.cargar_datos_presupuestos()
    
    def crear_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Pedidos
        pedidos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pedidos", menu=pedidos_menu)
        pedidos_menu.add_command(label="Nuevo Pedido", command=self.nuevo_pedido)
        pedidos_menu.add_command(label="Buscar Pedido", command=self.buscar_pedido)
        
        # Menú Clientes
        clientes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Clientes", menu=clientes_menu)
        clientes_menu.add_command(label="Nuevo Cliente", command=self.nuevo_cliente)
        clientes_menu.add_command(label="Buscar Cliente", command=self.buscar_clientes)
        
        # Menú Productos
        productos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Productos", menu=productos_menu)
        productos_menu.add_command(label="Nuevo Producto", command=self.nuevo_producto)
        productos_menu.add_command(label="Buscar Producto", command=self.filtrar_productos)
        
        # Menú Presupuestos
        presupuestos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Presupuestos", menu=presupuestos_menu)
        presupuestos_menu.add_command(label="Nuevo Presupuesto", command=self.nuevo_presupuesto)
        presupuestos_menu.add_command(label="Buscar Presupuesto", command=self.buscar_presupuesto)
    
    def crear_notebook(self):
        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.tab_pedidos = ttk.Frame(self.notebook)
        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_productos = ttk.Frame(self.notebook)
        self.tab_presupuestos = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_pedidos, text='Pedidos')
        self.notebook.add(self.tab_clientes, text='Clientes')
        self.notebook.add(self.tab_productos, text='Productos')
        self.notebook.add(self.tab_presupuestos, text='Presupuestos')
        
        # Crear interfaz de cada pestaña
        self.configurar_pedidos()
        self.configurar_clientes()
        self.configurar_productos()
        self.crear_tab_presupuestos()
    
    def crear_tab_presupuestos(self):
        """Crea la interfaz de la pestaña de presupuestos"""
        # Frame principal
        frame = ttk.Frame(self.tab_presupuestos, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Frame superior (filtros y botones)
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # Filtro
        ttk.Label(top_frame, text="Buscar:").pack(side='left', padx=(0, 5))
        ttk.Entry(top_frame, textvariable=self.filtro_presupuesto_var, width=30).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Buscar", command=lambda: self.cargar_datos_presupuestos(self.filtro_presupuesto_var.get())).pack(side='left', padx=(0, 5))
        ttk.Button(top_frame, text="Mostrar Todos", command=self.mostrar_todos_presupuestos).pack(side='left')
        
        # Botones de acción
        ttk.Button(top_frame, text="Nuevo Presupuesto", command=self.nuevo_presupuesto).pack(side='right', padx=5)
        ttk.Button(top_frame, text="Ver Detalles", command=self.ver_detalles_presupuesto).pack(side='right', padx=5)
        ttk.Button(top_frame, text="Editar", command=self.editar_presupuesto).pack(side='right', padx=5)
        ttk.Button(top_frame, text="Eliminar", command=self.eliminar_presupuesto).pack(side='right', padx=5)
        ttk.Button(top_frame, text="Convertir a Pedido", command=self.convertir_a_pedido).pack(side='right', padx=5)
        
        # Tabla de presupuestos
        columns = ('id', 'cliente', 'fecha', 'validez', 'total', 'estado')
        self.tabla_presupuestos = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Configurar columnas
        self.tabla_presupuestos.heading('id', text='ID')
        self.tabla_presupuestos.heading('cliente', text='Cliente')
        self.tabla_presupuestos.heading('fecha', text='Fecha')
        self.tabla_presupuestos.heading('validez', text='Validez')
        self.tabla_presupuestos.heading('total', text='Total')
        self.tabla_presupuestos.heading('estado', text='Estado')
        
        self.tabla_presupuestos.column('id', width=80)
        self.tabla_presupuestos.column('cliente', width=200)
        self.tabla_presupuestos.column('fecha', width=100)
        self.tabla_presupuestos.column('validez', width=100)
        self.tabla_presupuestos.column('total', width=100)
        self.tabla_presupuestos.column('estado', width=100)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.tabla_presupuestos.yview)
        self.tabla_presupuestos.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla_presupuestos.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Evento de doble clic en la tabla
        self.tabla_presupuestos.bind('<Double-1>', lambda e: self.ver_detalles_presupuesto())
    
    def configurar_pedidos(self):
        """Configurar la pestaña de pedidos"""
        # Frame superior con botones de acción
        frame_acciones = ttk.Frame(self.tab_pedidos)
        frame_acciones.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame_acciones, text="Nuevo Pedido", command=self.nuevo_pedido).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Editar Pedido", command=self.editar_pedido).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Eliminar Pedido", command=self.eliminar_pedido).pack(side=tk.LEFT, padx=5)
        
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(self.tab_pedidos, text="Filtros")
        frame_filtros.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Estado:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.estado_combo = ttk.Combobox(frame_filtros, values=["Todos", "Pendiente", "En proceso", "Completado", "Cancelado"])
        self.estado_combo.grid(row=0, column=1, padx=5, pady=5)
        self.estado_combo.current(0)
        
        ttk.Label(frame_filtros, text="Cliente:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.cliente_entry = ttk.Entry(frame_filtros)
        self.cliente_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(frame_filtros, text="Filtrar", command=self.filtrar_pedidos).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(frame_filtros, text="Limpiar Filtros", command=self.limpiar_filtros_pedidos).grid(row=0, column=5, padx=5, pady=5)
        
        # Tabla de pedidos
        frame_tabla = ttk.Frame(self.tab_pedidos)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columnas = ('id', 'cliente', 'fecha', 'estado', 'total')
        self.tabla_pedidos = ttk.Treeview(frame_tabla, columns=columnas, show='headings')
        
        # Configurar columnas
        self.tabla_pedidos.heading('id', text='ID')
        self.tabla_pedidos.heading('cliente', text='Cliente')
        self.tabla_pedidos.heading('fecha', text='Fecha')
        self.tabla_pedidos.heading('estado', text='Estado')
        self.tabla_pedidos.heading('total', text='Total')
        
        self.tabla_pedidos.column('id', width=50)
        self.tabla_pedidos.column('cliente', width=200)
        self.tabla_pedidos.column('fecha', width=100)
        self.tabla_pedidos.column('estado', width=100)
        self.tabla_pedidos.column('total', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_pedidos.yview)
        self.tabla_pedidos.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Eventos
        self.tabla_pedidos.bind("<Double-1>", lambda event: self.ver_detalles_pedido())
        self.tabla_pedidos.bind("<Button-3>", self.mostrar_menu_contextual)  # Botón derecho
        
        # Crear menú contextual
        self.menu_contextual = tk.Menu(self.root, tearoff=0)
        self.menu_contextual.add_command(label="Ver Detalles", command=self.ver_detalles_pedido)
        self.menu_contextual.add_command(label="Editar Pedido", command=self.editar_pedido)
        
        # Submenú para cambiar estado
        self.submenu_estado = tk.Menu(self.menu_contextual, tearoff=0)
        self.submenu_estado.add_command(label="Pendiente", command=lambda: self.cambiar_estado_desde_menu("Pendiente"))
        self.submenu_estado.add_command(label="En proceso", command=lambda: self.cambiar_estado_desde_menu("En proceso"))
        self.submenu_estado.add_command(label="Completado", command=lambda: self.cambiar_estado_desde_menu("Completado"))
        self.submenu_estado.add_command(label="Cancelado", command=lambda: self.cambiar_estado_desde_menu("Cancelado"))
        
        self.menu_contextual.add_cascade(label="Cambiar Estado", menu=self.submenu_estado)
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="Eliminar Pedido", command=self.eliminar_pedido)
    
    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual para la tabla de pedidos"""
        try:
            # Seleccionar el ítem donde se hizo clic
            item = self.tabla_pedidos.identify_row(event.y)
            if item:
                self.tabla_pedidos.selection_set(item)
                self.menu_contextual.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"[MainWindow] Error al mostrar menú contextual: {str(e)}")
    
    def cambiar_estado_desde_menu(self, nuevo_estado):
        """Cambia el estado del pedido seleccionado desde el menú contextual"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Cambiar Estado", "Por favor, seleccione un pedido para cambiar su estado")
            return
        
        # Obtener el ID del pedido seleccionado
        item = self.tabla_pedidos.item(seleccion[0])
        pedido_id = item['values'][0]  # El ID está en la primera columna
        
        # Cambiar el estado sin abrir ventana de detalles
        resultado, mensaje = self.pedido_controller.cambiar_estado_pedido(pedido_id, nuevo_estado)
        
        if resultado:
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", mensaje)
            
            # Actualizar tabla de pedidos
            self.cargar_datos_pedidos()
            
            # Seleccionar el pedido en la tabla
            self.seleccionar_pedido_en_tabla(pedido_id)
            
            # Mostrar los detalles del pedido actualizado
            self.ver_detalles_pedido()
            
            # Actualizar barra de estado
            self.barra_estado.config(text=f"Estado del pedido #{pedido_id} cambiado a '{nuevo_estado}'")
        else:
            # Mostrar mensaje de error
            messagebox.showerror("Error", mensaje)
    
    def cargar_datos_pedidos(self):
        """Cargar datos de pedidos en la tabla"""
        try:
            print("[MainWindow] Cargando datos de pedidos...")
            pedidos = self.pedido_controller.obtener_pedidos()
            
            # Convertir a DataFrame si no lo es
            if not isinstance(pedidos, pd.DataFrame):
                pedidos = pd.DataFrame(pedidos)
            
            print(f"[MainWindow] Pedidos obtenidos: {len(pedidos)}")
            if not pedidos.empty:
                print(f"[MainWindow] Columnas disponibles: {pedidos.columns.tolist()}")
            
            # Actualizar tabla usando el método común
            self.actualizar_tabla_pedidos(pedidos)
            
            # Actualizar barra de estado
            self.barra_estado.config(text=f"Se cargaron {len(pedidos) if not pedidos.empty else 0} pedidos")
        except Exception as e:
            print(f"[MainWindow] Error al cargar los pedidos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cargar los pedidos: {str(e)}")
            self.barra_estado.config(text="Error al cargar pedidos")
    
    def configurar_clientes(self):
        """Configurar la pestaña de clientes"""
        # Frame superior con botones de acción
        frame_acciones = ttk.Frame(self.tab_clientes)
        frame_acciones.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame_acciones, text="Nuevo Cliente", command=self.nuevo_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Editar Cliente", command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Eliminar Cliente", command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)
        
        # Frame de búsqueda
        frame_busqueda = ttk.LabelFrame(self.tab_clientes, text="Búsqueda")
        frame_busqueda.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_busqueda, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.nombre_cliente_entry = ttk.Entry(frame_busqueda)
        self.nombre_cliente_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame_busqueda, text="Buscar", command=self.buscar_clientes).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame_busqueda, text="Mostrar Todos", command=self.mostrar_todos_clientes).grid(row=0, column=3, padx=5, pady=5)
        
        # Tabla de clientes
        frame_tabla = ttk.Frame(self.tab_clientes)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columnas = ('id', 'nombre', 'apellido', 'email', 'telefono')
        self.tabla_clientes = ttk.Treeview(frame_tabla, columns=columnas, show='headings')
        
        # Configurar columnas
        self.tabla_clientes.heading('id', text='ID')
        self.tabla_clientes.heading('nombre', text='Nombre')
        self.tabla_clientes.heading('apellido', text='Apellido')
        self.tabla_clientes.heading('email', text='Email')
        self.tabla_clientes.heading('telefono', text='Teléfono')
        
        self.tabla_clientes.column('id', width=50)
        self.tabla_clientes.column('nombre', width=150)
        self.tabla_clientes.column('apellido', width=150)
        self.tabla_clientes.column('email', width=200)
        self.tabla_clientes.column('telefono', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_clientes.yview)
        self.tabla_clientes.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de doble clic
        self.tabla_clientes.bind("<Double-1>", lambda event: self.ver_detalles_cliente())
    
    def configurar_productos(self):
        """Configurar la pestaña de productos"""
        # Frame superior con botones de acción
        frame_acciones = ttk.Frame(self.tab_productos)
        frame_acciones.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame_acciones, text="Nuevo Producto", command=self.nuevo_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Editar Producto", command=self.editar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acciones, text="Eliminar Producto", command=self.eliminar_producto).pack(side=tk.LEFT, padx=5)
        
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(self.tab_productos, text="Filtros")
        frame_filtros.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_filtros, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.nombre_entry = ttk.Entry(frame_filtros)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame_filtros, text="Filtrar", command=self.filtrar_productos).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame_filtros, text="Limpiar Filtros", command=self.limpiar_filtros_productos).grid(row=0, column=3, padx=5, pady=5)
        
        # Tabla de productos
        frame_tabla = ttk.Frame(self.tab_productos)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columnas = ('id', 'nombre', 'descripcion', 'precio_compra', 'precio_venta', 'margen')
        self.tabla_productos = ttk.Treeview(frame_tabla, columns=columnas, show='headings')
        
        # Configurar columnas
        self.tabla_productos.heading('id', text='ID')
        self.tabla_productos.heading('nombre', text='Nombre')
        self.tabla_productos.heading('descripcion', text='Descripción')
        self.tabla_productos.heading('precio_compra', text='Precio Compra')
        self.tabla_productos.heading('precio_venta', text='Precio Venta')
        self.tabla_productos.heading('margen', text='Margen %')
        
        self.tabla_productos.column('id', width=50)
        self.tabla_productos.column('nombre', width=150)
        self.tabla_productos.column('descripcion', width=200)
        self.tabla_productos.column('precio_compra', width=100)
        self.tabla_productos.column('precio_venta', width=100)
        self.tabla_productos.column('margen', width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla_productos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Evento de doble clic
        self.tabla_productos.bind("<Double-1>", lambda event: self.ver_detalles_producto())
    
    # Métodos para menú Archivo
    def exportar_datos(self):
        messagebox.showinfo("Exportar Datos", "Función de exportación de datos")
        
    def importar_datos(self):
        messagebox.showinfo("Importar Datos", "Función de importación de datos")
    
    # Métodos para gestión de pedidos
    def nuevo_pedido(self):
        """Abre el diálogo para crear un nuevo pedido"""
        abrir_dialogo_pedido(self.root, self.on_pedido_guardado)
        
    def on_pedido_guardado(self, pedido):
        """Callback para cuando se guarda un pedido"""
        try:
            print(f"[MainWindow] Pedido guardado - ID: {pedido.id}, Cliente: {pedido.cliente_id}")
            
            # Refrescar la tabla de pedidos
            self.cargar_datos_pedidos()
            
            # Mostrar mensaje de éxito
            accion = "actualizado" if hasattr(pedido, 'id_original') else "creado"
            total = pedido.total if hasattr(pedido, 'total') else "N/A"
            
            mensaje = f"Pedido #{pedido.id} {accion} correctamente."
            if hasattr(pedido, 'items'):
                mensaje += f" ({len(pedido.items)} productos, total: ${float(total):.2f})"
            
            self.barra_estado.config(text=mensaje)
            
            # Si estamos en la pestaña de pedidos, seleccionar el pedido
            if self.notebook.index(self.notebook.select()) == 0:  # La pestaña de pedidos es la primera (índice 0)
                self.seleccionar_pedido_en_tabla(pedido.id)
                
                # Mostrar los detalles del pedido guardado
                self.root.after(200, self.ver_detalles_pedido)  # Pequeño delay para asegurar que la tabla se actualice primero
                
        except Exception as e:
            print(f"[MainWindow] Error en callback de pedido guardado: {str(e)}")
            import traceback
            traceback.print_exc()
            self.barra_estado.config(text=f"Pedido guardado, pero ocurrió un error al actualizar la interfaz")
    
    def seleccionar_pedido_en_tabla(self, pedido_id):
        """Selecciona un pedido en la tabla por su ID"""
        try:
            # Buscar el pedido en la tabla
            for item in self.tabla_pedidos.get_children():
                valores = self.tabla_pedidos.item(item, 'values')
                if valores[0] == pedido_id:  # El ID está en la primera columna
                    # Seleccionar y hacer visible
                    self.tabla_pedidos.selection_set(item)
                    self.tabla_pedidos.see(item)
                    return True
            return False
        except Exception as e:
            print(f"[MainWindow] Error al seleccionar pedido en tabla: {str(e)}")
            return False
    
    def buscar_pedido(self):
        messagebox.showinfo("Buscar Pedido", "Función para buscar pedidos")
        
    def editar_pedido(self):
        """Abre el diálogo para editar un pedido existente"""
        # Verificar que hay un pedido seleccionado
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Editar Pedido", "Por favor, seleccione un pedido para editar")
            return
        
        try:
            # Obtener el ID del pedido seleccionado
            item = self.tabla_pedidos.item(seleccion[0])
            pedido_id = item['values'][0]  # El ID está en la primera columna
            
            print(f"[MainWindow] Editando pedido con ID: {pedido_id}")
            
            # Obtener el pedido completo con sus ítems
            pedido_completo = self.pedido_controller.obtener_detalles_pedido(pedido_id)
            
            if not pedido_completo:
                messagebox.showerror("Error", f"No se encontró el pedido con ID {pedido_id}")
                return
            
            # Crear un objeto Pedido con los datos
            from app.models.pedido import Pedido, ItemPedido
            
            # Crear los objetos ItemPedido a partir de los detalles
            items = []
            if 'items' in pedido_completo and pedido_completo['items']:
                print(f"[MainWindow] Cargando {len(pedido_completo['items'])} ítems para la edición")
                for item_data in pedido_completo['items']:
                    item = ItemPedido(
                        id=item_data.get('id', None),
                        producto_id=item_data.get('producto_id', None),
                        descripcion=item_data.get('descripcion', 'Sin descripción'),
                        cantidad=item_data.get('cantidad', 0),
                        precio_unitario=item_data.get('precio_unitario', 0),
                        descuento=item_data.get('descuento', 0)
                    )
                    items.append(item)
            
            # Crear el objeto Pedido
            pedido = Pedido(
                id=pedido_completo['id'],
                cliente_id=pedido_completo['cliente_id'],
                fecha=pedido_completo['fecha'],
                estado=pedido_completo['estado'],
                items=items,
                total=pedido_completo.get('total', 0),
                notas=pedido_completo.get('notas', '')
            )
            
            # Abrir el diálogo de edición
            from app.views.pedido_dialog import abrir_dialogo_editar_pedido
            abrir_dialogo_editar_pedido(self.root, pedido, self.on_pedido_guardado)
            
        except Exception as e:
            print(f"[MainWindow] Error al editar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al editar el pedido: {str(e)}")
    
    def eliminar_pedido(self):
        """Elimina el pedido seleccionado"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar Pedido", "Por favor, seleccione un pedido para eliminar")
            return
        
        try:
            # Obtener el ID del pedido seleccionado
            item = self.tabla_pedidos.item(seleccion[0])
            pedido_id = item['values'][0]  # El ID está en la primera columna
            
            # Confirmar eliminación
            confirmacion = messagebox.askyesno(
                "Eliminar Pedido", 
                f"¿Está seguro de eliminar el pedido #{pedido_id}?\n\nEsta acción no se puede deshacer."
            )
            
            if not confirmacion:
                return
            
            # Eliminar el pedido usando el controlador
            resultado, mensaje = self.pedido_controller.eliminar_pedido(pedido_id)
            
            if resultado:
                # Actualizar la tabla
                self.cargar_datos_pedidos()
                messagebox.showinfo("Éxito", mensaje)
                self.barra_estado.config(text=f"Pedido #{pedido_id} eliminado correctamente")
            else:
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            print(f"[MainWindow] Error al eliminar pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al eliminar el pedido: {str(e)}")
    
    def filtrar_pedidos(self):
        """Aplica filtros a la lista de pedidos"""
        try:
            print("[MainWindow] Aplicando filtros a pedidos...")
            
            # Obtener valores de los filtros
            estado = self.estado_combo.get()
            cliente = self.cliente_entry.get().strip()
            
            print(f"[MainWindow] Filtros: Estado={estado}, Cliente={cliente}")
            
            # Preparar filtros
            filtros = {}
            
            if estado and estado != "Todos":
                filtros['estado'] = estado
            
            # Obtener pedidos con los filtros
            pedidos_df = self.pedido_controller.obtener_pedidos(filtros)
            
            # Si hay filtro de cliente, aplicarlo manualmente (ya que requiere join con clientes)
            if cliente:
                # Obtener clientes
                clientes_df = self.cliente_controller.obtener_clientes()
                
                # Filtrar clientes por nombre o apellido que contengan el texto
                if not clientes_df.empty:
                    clientes_filtrados = clientes_df[
                        clientes_df['nombre'].str.contains(cliente, case=False, na=False) |
                        clientes_df['apellido'].str.contains(cliente, case=False, na=False)
                    ]
                    
                    if not clientes_filtrados.empty:
                        # Obtener IDs de clientes que coinciden
                        cliente_ids = clientes_filtrados['id'].tolist()
                        
                        # Filtrar pedidos por esos IDs de cliente
                        pedidos_df = pedidos_df[pedidos_df['cliente_id'].isin(cliente_ids)]
            
            # Actualizar tabla
            self.actualizar_tabla_pedidos(pedidos_df)
            
            # Actualizar barra de estado
            self.barra_estado.config(text=f"Se encontraron {len(pedidos_df)} pedidos con los filtros aplicados")
            
        except Exception as e:
            print(f"[MainWindow] Error al filtrar pedidos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al aplicar filtros: {str(e)}")
    
    def actualizar_tabla_pedidos(self, pedidos_df):
        """Actualiza la tabla de pedidos con los datos proporcionados"""
        try:
            # Limpiar tabla existente
            for item in self.tabla_pedidos.get_children():
                self.tabla_pedidos.delete(item)
            
            # Si no hay datos, terminar
            if pedidos_df.empty:
                return
            
            # Obtener datos de clientes para mostrar nombres en lugar de IDs
            df_clientes = self.cliente_controller.obtener_clientes()
            cliente_dict = {}
            
            if not df_clientes.empty:
                for _, cliente in df_clientes.iterrows():
                    if 'id' in cliente and 'nombre' in cliente and 'apellido' in cliente:
                        nombre_completo = f"{cliente['nombre']} {cliente['apellido']}".strip()
                        cliente_dict[cliente['id']] = nombre_completo
            
            # Insertar cada pedido en la tabla
            for index, row in pedidos_df.iterrows():
                pedido_id = row.get('id', '')
                
                # Obtener nombre del cliente usando el cliente_id
                cliente_id = row.get('cliente_id', '')
                nombre_cliente = cliente_dict.get(cliente_id, f"Cliente {cliente_id}")
                
                fecha = row.get('fecha', '')
                estado = row.get('estado', 'Pendiente')
                total = row.get('total', 0)
                
                try:
                    total_formateado = f"${float(total):.2f}"
                except (ValueError, TypeError):
                    total_formateado = f"${0:.2f}"
                
                self.tabla_pedidos.insert('', tk.END, values=(
                    pedido_id, 
                    nombre_cliente, 
                    fecha, 
                    estado, 
                    total_formateado
                ))
                
        except Exception as e:
            print(f"[MainWindow] Error al actualizar tabla: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def limpiar_filtros_pedidos(self):
        """Limpia todos los filtros y muestra todos los pedidos"""
        try:
            # Limpiar campos de filtro
            self.estado_combo.current(0)  # Seleccionar "Todos"
            self.cliente_entry.delete(0, tk.END)
            
            # Cargar todos los pedidos
            self.cargar_datos_pedidos()
            self.barra_estado.config(text="Filtros limpios. Mostrando todos los pedidos.")
            
        except Exception as e:
            print(f"[MainWindow] Error al limpiar filtros: {str(e)}")
            messagebox.showerror("Error", f"Error al limpiar filtros: {str(e)}")
    
    def ver_detalles_pedido(self):
        """Muestra los detalles del pedido seleccionado"""
        seleccion = self.tabla_pedidos.selection()
        if not seleccion:
            messagebox.showwarning("Ver Detalles", "Por favor, seleccione un pedido para ver sus detalles")
            return
        
        try:
            # Obtener el ID del pedido seleccionado
            item = self.tabla_pedidos.item(seleccion[0])
            pedido_id = item['values'][0]  # El ID está en la primera columna
            
            print(f"[MainWindow] Viendo detalles del pedido con ID: {pedido_id}")
            
            # Obtener el pedido desde el controlador
            pedidos_df = self.pedido_controller.obtener_pedidos()
            
            if pedidos_df.empty:
                messagebox.showerror("Error", "No se pudo obtener la lista de pedidos")
                return
                
            # Filtrar el pedido por ID
            pedido_df = pedidos_df[pedidos_df['id'] == pedido_id]
            
            if pedido_df.empty:
                messagebox.showerror("Error", f"No se encontró el pedido con ID {pedido_id}")
                return
                
            # Obtener datos del pedido
            pedido_data = pedido_df.iloc[0]
            
            # Obtener datos del cliente
            cliente_id = pedido_data['cliente_id']
            nombre_cliente = "Cliente desconocido"
            
            df_clientes = self.cliente_controller.obtener_clientes()
            if not df_clientes.empty:
                cliente_df = df_clientes[df_clientes['id'] == cliente_id]
                if not cliente_df.empty:
                    cliente = cliente_df.iloc[0]
                    nombre = cliente.get('nombre', '')
                    apellido = cliente.get('apellido', '')
                    nombre_cliente = f"{nombre} {apellido}".strip()
            
            # Crear ventana para mostrar detalles
            ventana = tk.Toplevel(self.root)
            ventana.title(f"Detalles del Pedido #{pedido_id}")
            ventana.geometry("800x600")
            ventana.transient(self.root)
            ventana.grab_set()
            
            # Frame principal
            main_frame = ttk.Frame(ventana, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Información general del pedido
            info_frame = ttk.LabelFrame(main_frame, text="Información del Pedido", padding=10)
            info_frame.pack(fill=tk.X, pady=5)
            
            # Información en dos columnas
            ttk.Label(info_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=pedido_id).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            
            ttk.Label(info_frame, text="Cliente:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=nombre_cliente).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
            
            ttk.Label(info_frame, text="Fecha:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=pedido_data.get('fecha', 'No disponible')).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
            
            ttk.Label(info_frame, text="Estado:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=pedido_data.get('estado', 'No disponible')).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
            
            ttk.Label(info_frame, text="Total:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
            total = pedido_data.get('total', 0)
            ttk.Label(info_frame, text=f"${float(total):.2f}").grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
            
            # Obtener detalles de los ítems
            try:
                # Usar el controlador para obtener todos los detalles
                pedido_completo = self.pedido_controller.obtener_detalles_pedido(pedido_id)
                
                if pedido_completo and 'items' in pedido_completo and pedido_completo['items']:
                    items = pedido_completo['items']
                    print(f"[MainWindow] Se obtuvieron {len(items)} ítems del pedido mediante el controlador")
                    
                    # Frame para ítems
                    items_frame = ttk.LabelFrame(main_frame, text="Productos del Pedido", padding=10)
                    items_frame.pack(fill=tk.BOTH, expand=True, pady=5)
                    
                    # Tabla de ítems
                    columns = ('descripcion', 'cantidad', 'precio', 'descuento', 'subtotal')
                    items_tabla = ttk.Treeview(items_frame, columns=columns, show='headings')
                    
                    # Configurar columnas
                    items_tabla.heading('descripcion', text='Producto')
                    items_tabla.heading('cantidad', text='Cantidad')
                    items_tabla.heading('precio', text='Precio Unit.')
                    items_tabla.heading('descuento', text='Descuento %')
                    items_tabla.heading('subtotal', text='Subtotal')
                    
                    items_tabla.column('descripcion', width=250)
                    items_tabla.column('cantidad', width=80)
                    items_tabla.column('precio', width=100)
                    items_tabla.column('descuento', width=100)
                    items_tabla.column('subtotal', width=100)
                    
                    # Scroll para la tabla
                    scroll = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=items_tabla.yview)
                    items_tabla.configure(yscroll=scroll.set)
                    
                    # Empaquetar tabla y scrollbar
                    items_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    scroll.pack(side=tk.RIGHT, fill=tk.Y)
                    
                    # Llenar tabla con ítems
                    for item in items:
                        descripcion = item.get('descripcion', 'Sin descripción')
                        cantidad = item.get('cantidad', 0)
                        precio = item.get('precio_unitario', 0)
                        descuento = item.get('descuento', 0)
                        subtotal = item.get('subtotal', 0)
                        
                        print(f"[MainWindow] Agregando item: {descripcion}, {cantidad} x ${precio}")
                        
                        items_tabla.insert('', tk.END, values=(
                            descripcion,
                            cantidad,
                            f"${float(precio):.2f}",
                            f"{float(descuento):.0f}%",
                            f"${float(subtotal):.2f}"
                        ))
                else:
                    # No hay items para este pedido
                    ttk.Label(main_frame, text="Este pedido no tiene productos registrados", 
                            font=('Helvetica', 10, 'italic')).pack(pady=10)
                    print(f"[MainWindow] No se encontraron ítems para el pedido {pedido_id}")
            except Exception as e:
                print(f"[MainWindow] Error al cargar los detalles del pedido: {str(e)}")
                import traceback
                traceback.print_exc()
                ttk.Label(main_frame, text=f"Error al cargar detalles: {str(e)}", foreground="red").pack(pady=10)
            
            # Botones
            botones_frame = ttk.Frame(main_frame)
            botones_frame.pack(fill=tk.X, pady=10)
            
            # Botón para cambiar estado
            estados_posibles = ["Pendiente", "En proceso", "Completado", "Cancelado"]
            estado_actual = pedido_data.get('estado', 'Pendiente')
            
            estado_frame = ttk.LabelFrame(botones_frame, text="Cambiar Estado")
            estado_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Variable para el ComboBox
            self.cambio_estado_var = tk.StringVar()
            self.cambio_estado_var.set(estado_actual)
            
            # ComboBox y botón de actualizar
            estado_combo = ttk.Combobox(estado_frame, textvariable=self.cambio_estado_var, values=estados_posibles, state="readonly", width=15)
            estado_combo.pack(side=tk.LEFT, padx=5, pady=5)
            
            ttk.Button(estado_frame, text="Actualizar Estado", 
                     command=lambda: self.cambiar_estado_pedido(pedido_id, self.cambio_estado_var.get(), ventana)).pack(side=tk.LEFT, padx=5, pady=5)
            
            # Botones de acción principales
            ttk.Button(botones_frame, text="Cerrar", command=ventana.destroy).pack(side=tk.RIGHT, padx=5)
            ttk.Button(botones_frame, text="Editar Pedido", command=lambda: [ventana.destroy(), self.editar_pedido()]).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            print(f"[MainWindow] Error al ver detalles del pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al ver detalles del pedido: {str(e)}")
    
    # Métodos para gestión de clientes
    def nuevo_cliente(self):
        """Abre el diálogo para crear un nuevo cliente"""
        abrir_dialogo_cliente(self.root, self.on_cliente_saved)
        
    def on_cliente_saved(self, cliente):
        """Callback para cuando se guarda un cliente"""
        self.cargar_datos_clientes()
        self.barra_estado.config(text=f"Cliente {cliente.nombre} {cliente.apellido} guardado correctamente")

    def editar_cliente(self):
        """Edita el cliente seleccionado"""
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Editar Cliente", "Por favor, seleccione un cliente para editar")
            return
        
        # Obtener ID del cliente seleccionado
        item = self.tabla_clientes.item(seleccion[0])
        cliente_id = int(item['values'][0])
        
        # Obtener el cliente completo
        cliente = self.cliente_controller.obtener_cliente_por_id(cliente_id)
        
        if cliente:
            abrir_dialogo_editar_cliente(self.root, cliente, self.on_cliente_saved)
        else:
            messagebox.showerror("Error", "No se pudo obtener los datos del cliente")

    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar Cliente", "Por favor, seleccione un cliente para eliminar")
            return
        
        confirmacion = messagebox.askyesno("Eliminar Cliente", "¿Está seguro de eliminar el cliente seleccionado?")
        if confirmacion:
            # Obtener ID del cliente seleccionado
            item = self.tabla_clientes.item(seleccion[0])
            cliente_id = int(item['values'][0])
            
            # Eliminar cliente
            resultado, mensaje = self.cliente_controller.eliminar_cliente(cliente_id)
            
            if resultado:
                messagebox.showinfo("Éxito", mensaje)
                self.cargar_datos_clientes()
            else:
                messagebox.showerror("Error", mensaje)
    
    def buscar_clientes(self):
        """Busca clientes por nombre o apellido"""
        nombre_busqueda = self.nombre_cliente_entry.get().strip()
        
        if nombre_busqueda:
            filtros = {'nombre': nombre_busqueda}
            df_clientes = self.cliente_controller.obtener_clientes(filtros)
        else:
            df_clientes = self.cliente_controller.obtener_clientes()
        
        self.actualizar_tabla_clientes(df_clientes)
        
    def mostrar_todos_clientes(self):
        """Muestra todos los clientes"""
        self.nombre_cliente_entry.delete(0, tk.END)
        self.cargar_datos_clientes()
        
    def ver_detalles_cliente(self):
        """Muestra los detalles del cliente seleccionado"""
        seleccion = self.tabla_clientes.selection()
        if not seleccion:
            return
        
        # Obtener ID del cliente seleccionado
        item = self.tabla_clientes.item(seleccion[0])
        cliente_id = int(item['values'][0])
        
        # Obtener el cliente completo
        cliente = self.cliente_controller.obtener_cliente_por_id(cliente_id)
        
        if cliente:
            mensaje = f"Nombre: {cliente.nombre} {cliente.apellido}\n"
            mensaje += f"Email: {cliente.email or 'No disponible'}\n"
            mensaje += f"Teléfono: {cliente.telefono or 'No disponible'}\n"
            mensaje += f"Dirección: {cliente.direccion or 'No disponible'}"
            
            messagebox.showinfo("Detalles del Cliente", mensaje)
    
    def cargar_datos_clientes(self):
        """Carga los datos de clientes en la tabla"""
        df_clientes = self.cliente_controller.obtener_clientes()
        self.actualizar_tabla_clientes(df_clientes)
    
    def actualizar_tabla_clientes(self, df_clientes):
        """Actualiza la tabla de clientes con los datos del DataFrame"""
        # Limpiar tabla
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)
        
        # Si no hay datos, salir
        if df_clientes.empty:
            return
        
        # Agregar filas a la tabla
        for _, row in df_clientes.iterrows():
            self.tabla_clientes.insert("", "end", values=(
                row['id'],
                row['nombre'],
                row['apellido'],
                row.get('email', ''),
                row.get('telefono', '')
            ))
    
    # Métodos para gestión de productos
    def nuevo_producto(self):
        """Abre el diálogo para crear un nuevo producto"""
        abrir_dialogo_producto(self.root, self.on_producto_guardado)
    
    def on_producto_guardado(self, producto):
        """Callback para cuando se guarda un producto"""
        self.cargar_datos_productos()
        self.barra_estado.config(text=f"Producto '{producto.nombre}' guardado correctamente")
    
    def editar_producto(self):
        """Abre el diálogo para editar un producto existente"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Editar Producto", "Por favor, seleccione un producto para editar")
            return
        
        # Obtener ID del producto seleccionado
        producto_id = self.tabla_productos.item(seleccion[0])["values"][0]
        
        # Obtener producto del controlador
        producto = self.producto_controller.obtener_producto_por_id(producto_id)
        
        if not producto:
            messagebox.showerror("Error", f"No se encontró el producto con ID {producto_id}")
            return
        
        # Abrir diálogo de edición
        abrir_dialogo_editar_producto(self.root, producto, self.on_producto_guardado)
    
    def eliminar_producto(self):
        """Elimina un producto"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar Producto", "Por favor, seleccione un producto para eliminar")
            return
        
        # Obtener ID del producto seleccionado
        producto_id = self.tabla_productos.item(seleccion[0])["values"][0]
        producto_nombre = self.tabla_productos.item(seleccion[0])["values"][1]
        
        # Confirmar eliminación
        confirmacion = messagebox.askyesno("Eliminar Producto", 
                                           f"¿Está seguro que desea eliminar el producto '{producto_nombre}'?")
        if not confirmacion:
            return
        
        # Eliminar producto
        resultado, mensaje = self.producto_controller.eliminar_producto(producto_id)
        
        if resultado:
            messagebox.showinfo("Éxito", mensaje)
            self.cargar_datos_productos()
            self.barra_estado.config(text=f"Producto '{producto_nombre}' eliminado correctamente")
        else:
            messagebox.showerror("Error", mensaje)
    
    def filtrar_productos(self):
        """Filtra productos según los criterios especificados"""
        # Obtener valores de los filtros
        nombre = self.nombre_entry.get().strip() if hasattr(self, 'nombre_entry') else ""
        
        # Crear filtro
        filtro = {}
        if nombre:
            filtro['nombre'] = nombre
        
        # Aplicar filtro
        productos_filtrados = self.producto_controller.obtener_productos(filtro)
        
        # Actualizar tabla
        self.actualizar_tabla_productos(productos_filtrados)
        
        # Actualizar barra de estado
        self.barra_estado.config(text=f"Se encontraron {len(productos_filtrados) if not productos_filtrados.empty else 0} productos")
    
    def actualizar_tabla_productos(self, productos):
        """Actualiza la tabla de productos con los datos del DataFrame"""
        # Limpiar tabla existente
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        # Insertar datos en la tabla
        if not productos.empty:
            for index, row in productos.iterrows():
                # Asegurarse de que todas las columnas existan
                nombre = row.get('nombre', 'Desconocido')
                descripcion = row.get('descripcion', '')
                precio_compra = float(row.get('precio_compra', 0))
                precio_venta = float(row.get('precio_venta', 0))
                
                # Calcular margen
                margen = 0
                if precio_compra > 0:
                    margen = ((precio_venta - precio_compra) / precio_compra) * 100
                
                self.tabla_productos.insert('', tk.END, values=(
                    row.get('id', ''), 
                    nombre, 
                    descripcion, 
                    f"${precio_compra:.2f}", 
                    f"${precio_venta:.2f}",
                    f"{margen:.1f}%"
                ))
    
    def limpiar_filtros_productos(self):
        """Limpia los filtros de productos y muestra todos"""
        if hasattr(self, 'nombre_entry'):
            self.nombre_entry.delete(0, tk.END)
        
        self.cargar_datos_productos()
        self.barra_estado.config(text="Filtros de productos limpiados")
    
    def ver_detalles_producto(self):
        """Muestra los detalles del producto seleccionado"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            return
        
        # Obtener ID del producto seleccionado
        item = self.tabla_productos.item(seleccion[0])
        producto_id = item['values'][0]
        
        # Obtener producto completo
        producto = self.producto_controller.obtener_producto_por_id(producto_id)
        
        if producto:
            # Calcular margen
            margen = 0
            if producto.precio_compra > 0:
                margen = ((producto.precio_venta - producto.precio_compra) / producto.precio_compra) * 100
                
            # Crear mensaje con detalles
            mensaje = f"Nombre: {producto.nombre}\n\n"
            mensaje += f"Descripción: {producto.descripcion}\n\n"
            mensaje += f"Precio de Compra: ${producto.precio_compra:.2f}\n"
            mensaje += f"Precio de Venta: ${producto.precio_venta:.2f}\n"
            mensaje += f"Margen de Ganancia: {margen:.2f}%\n\n"
            
            messagebox.showinfo("Detalles del Producto", mensaje)
        else:
            messagebox.showerror("Error", f"No se encontró el producto con ID {producto_id}")
    
    def cargar_datos_productos(self):
        """Carga los datos de productos en la tabla"""
        try:
            productos = self.producto_controller.obtener_productos()
            # Convertir a DataFrame si no lo es
            if not isinstance(productos, pd.DataFrame):
                productos = pd.DataFrame(productos)
            
            # Limpiar tabla existente
            for item in self.tabla_productos.get_children():
                self.tabla_productos.delete(item)
            
            # Insertar datos en la tabla
            if not productos.empty:
                for index, row in productos.iterrows():
                    # Asegurarse de que todas las columnas existan
                    nombre = row.get('nombre', 'Desconocido')
                    descripcion = row.get('descripcion', '')
                    precio_compra = float(row.get('precio_compra', 0))
                    precio_venta = float(row.get('precio_venta', 0))
                    
                    # Calcular margen
                    margen = 0
                    if precio_compra > 0:
                        margen = ((precio_venta - precio_compra) / precio_compra) * 100
                    
                    self.tabla_productos.insert('', tk.END, values=(
                        row.get('id', ''), 
                        nombre, 
                        descripcion, 
                        f"${precio_compra:.2f}", 
                        f"${precio_venta:.2f}",
                        f"{margen:.1f}%"
                    ))
            
            self.barra_estado.config(text=f"Se cargaron {len(productos) if not productos.empty else 0} productos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los productos: {str(e)}")
            self.barra_estado.config(text="Error al cargar productos")
    
    # Métodos para reportes
    def reporte_ventas(self):
        messagebox.showinfo("Reporte de Ventas", "Generando reporte de ventas")
        
    def reporte_productos(self):
        messagebox.showinfo("Reporte de Productos", "Generando reporte de productos")
        
    def reporte_clientes(self):
        messagebox.showinfo("Reporte de Clientes", "Generando reporte de clientes")
        
    def generar_reporte(self):
        messagebox.showinfo("Generar Reporte", "Generando el reporte seleccionado")
        
    def ver_ultimo_reporte(self):
        messagebox.showinfo("Ver Último Reporte", "Mostrando el último reporte generado")
    
    # Métodos para ayuda
    def mostrar_manual(self):
        messagebox.showinfo("Manual de Usuario", "Mostrando manual de usuario")
        
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", "Sistema de Gestión de Pedidos - Ciabatta\nVersión 1.0\n\nDesarrollado para gestionar pedidos y generar reportes.")

    # Métodos para gestionar presupuestos
    def nuevo_presupuesto(self):
        """Abre el diálogo para crear un nuevo presupuesto"""
        abrir_dialogo_presupuesto(self.root, self.on_presupuesto_guardado)
    
    def editar_presupuesto(self):
        """Abre el diálogo para editar un presupuesto"""
        seleccion = self.tabla_presupuestos.selection()
        if not seleccion:
            messagebox.showwarning("Editar Presupuesto", "Por favor, seleccione un presupuesto para editar")
            return
        
        # Obtener ID del presupuesto
        item = self.tabla_presupuestos.item(seleccion[0])
        presupuesto_id = item['values'][0]
        
        # Obtener presupuesto completo
        presupuesto = self.presupuesto_controller.obtener_presupuesto_completo(presupuesto_id)
        if not presupuesto:
            messagebox.showerror("Error", f"No se pudo encontrar el presupuesto con ID {presupuesto_id}")
            return
        
        # Abrir diálogo de edición
        abrir_dialogo_editar_presupuesto(self.root, presupuesto, self.on_presupuesto_guardado)
    
    def eliminar_presupuesto(self):
        """Elimina un presupuesto seleccionado"""
        seleccion = self.tabla_presupuestos.selection()
        if not seleccion:
            messagebox.showwarning("Eliminar Presupuesto", "Por favor, seleccione un presupuesto para eliminar")
            return
        
        # Obtener ID del presupuesto
        item = self.tabla_presupuestos.item(seleccion[0])
        presupuesto_id = item['values'][0]
        cliente_nombre = item['values'][1]
        
        # Confirmar eliminación
        confirmacion = messagebox.askyesno("Eliminar Presupuesto", 
                                         f"¿Está seguro de eliminar el presupuesto {presupuesto_id} de {cliente_nombre}?")
        if not confirmacion:
            return
        
        # Implementar eliminación (aún no implementado en el controlador)
        messagebox.showinfo("Eliminar Presupuesto", "Funcionalidad aún no implementada")
    
    def ver_detalles_presupuesto(self):
        """Muestra los detalles de un presupuesto"""
        seleccion = self.tabla_presupuestos.selection()
        if not seleccion:
            messagebox.showwarning("Ver Detalles", "Por favor, seleccione un presupuesto para ver sus detalles")
            return
        
        # Obtener ID del presupuesto
        item = self.tabla_presupuestos.item(seleccion[0])
        presupuesto_id = item['values'][0]
        
        # Obtener presupuesto completo
        presupuesto = self.presupuesto_controller.obtener_presupuesto_completo(presupuesto_id)
        if not presupuesto:
            messagebox.showerror("Error", f"No se pudo encontrar el presupuesto con ID {presupuesto_id}")
            return
        
        # Crear ventana para mostrar detalles
        detalles_window = tk.Toplevel(self.root)
        detalles_window.title(f"Detalles del Presupuesto {presupuesto_id}")
        detalles_window.geometry("800x600")
        detalles_window.minsize(800, 600)
        detalles_window.transient(self.root)
        detalles_window.grab_set()
        
        # Centrar ventana
        detalles_window.update_idletasks()
        width = detalles_window.winfo_width()
        height = detalles_window.winfo_height()
        x = (detalles_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detalles_window.winfo_screenheight() // 2) - (height // 2)
        detalles_window.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(detalles_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Datos del presupuesto
        datos_frame = ttk.LabelFrame(main_frame, text="Datos del Presupuesto", padding=10)
        datos_frame.pack(fill=tk.X, pady=10)
        
        # Cliente
        ttk.Label(datos_frame, text="Cliente:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        cliente_nombre = f"{presupuesto.cliente.nombre} {presupuesto.cliente.apellido}"
        ttk.Label(datos_frame, text=cliente_nombre).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Fecha
        ttk.Label(datos_frame, text="Fecha:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(datos_frame, text=presupuesto.fecha).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Validez
        ttk.Label(datos_frame, text="Validez:", font=('Helvetica', 10, 'bold')).grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        ttk.Label(datos_frame, text=f"{presupuesto.validez} días").grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Estado
        ttk.Label(datos_frame, text="Estado:", font=('Helvetica', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(datos_frame, text=presupuesto.estado).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Notas
        ttk.Label(datos_frame, text="Notas:", font=('Helvetica', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        notas_text = tk.Text(datos_frame, height=3, width=60)
        notas_text.grid(row=3, column=1, columnspan=3, sticky=tk.W, pady=5)
        notas_text.insert(tk.END, presupuesto.notas if presupuesto.notas else "")
        notas_text.config(state=tk.DISABLED)
        
        # Ítems del presupuesto
        items_frame = ttk.LabelFrame(main_frame, text="Ítems del Presupuesto", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Tabla de ítems
        columnas = ('id', 'descripcion', 'cantidad', 'precio', 'descuento', 'subtotal')
        tabla_items = ttk.Treeview(items_frame, columns=columnas, show='headings')
        
        # Configurar columnas
        tabla_items.heading('id', text='ID')
        tabla_items.heading('descripcion', text='Descripción')
        tabla_items.heading('cantidad', text='Cantidad')
        tabla_items.heading('precio', text='Precio Unit.')
        tabla_items.heading('descuento', text='Descuento %')
        tabla_items.heading('subtotal', text='Subtotal')
        
        tabla_items.column('id', width=50)
        tabla_items.column('descripcion', width=300)
        tabla_items.column('cantidad', width=80)
        tabla_items.column('precio', width=100)
        tabla_items.column('descuento', width=100)
        tabla_items.column('subtotal', width=120)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=tabla_items.yview)
        tabla_items.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        tabla_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Agregar ítems a la tabla
        for item in presupuesto.items:
            tabla_items.insert("", "end", values=(
                item.id,
                item.descripcion,
                item.cantidad,
                f"${item.precio_unitario:.2f}",
                f"{item.descuento}%",
                f"${item.subtotal:.2f}"
            ))
        
        # Total
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(footer_frame, text="Total:", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Label(footer_frame, text=f"${presupuesto.total:.2f}", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Botones de acción
        ttk.Button(footer_frame, text="Cerrar", command=detalles_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Si el presupuesto está pendiente, mostrar botones para cambiar estado
        if presupuesto.estado == "Pendiente":
            ttk.Button(footer_frame, text="Aceptar Presupuesto", 
                     command=lambda: self.cambiar_estado_presupuesto(presupuesto.id, "Aceptado", detalles_window)).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(footer_frame, text="Rechazar Presupuesto", 
                     command=lambda: self.cambiar_estado_presupuesto(presupuesto.id, "Rechazado", detalles_window)).pack(side=tk.RIGHT, padx=5)
    
    def cambiar_estado_presupuesto(self, presupuesto_id, nuevo_estado, ventana=None):
        """Cambia el estado de un presupuesto"""
        confirmacion = messagebox.askyesno("Cambiar Estado", 
                                         f"¿Está seguro de cambiar el estado del presupuesto a '{nuevo_estado}'?")
        if not confirmacion:
            return
        
        try:
            # Actualizar estado
            self.presupuesto_controller.actualizar_estado_presupuesto(presupuesto_id, nuevo_estado)
            messagebox.showinfo("Éxito", f"Estado del presupuesto actualizado a '{nuevo_estado}'")
            
            # Si se aceptó, preguntar si desea ver el pedido generado
            if nuevo_estado == "Aceptado":
                ver_pedido = messagebox.askyesno("Pedido Generado", 
                                               "El presupuesto ha sido convertido a pedido. ¿Desea ver los pedidos?")
                if ver_pedido:
                    # Cambiar a la pestaña de pedidos
                    self.notebook.select(self.tab_pedidos)
                    # Actualizar tabla de pedidos
                    self.cargar_datos_pedidos()
            
            # Cerrar ventana de detalles si se proporcionó
            if ventana:
                ventana.destroy()
            
            # Actualizar tabla de presupuestos
            self.cargar_datos_presupuestos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
    
    def convertir_a_pedido(self):
        """Convierte un presupuesto en pedido"""
        seleccion = self.tabla_presupuestos.selection()
        if not seleccion:
            messagebox.showwarning("Convertir a Pedido", "Por favor, seleccione un presupuesto para convertir")
            return
        
        # Obtener ID del presupuesto
        item = self.tabla_presupuestos.item(seleccion[0])
        presupuesto_id = item['values'][0]
        estado = item['values'][5]
        
        # Verificar que el presupuesto esté pendiente
        if estado != "Pendiente":
            messagebox.showwarning("Convertir a Pedido", 
                                 f"Solo se pueden convertir presupuestos en estado 'Pendiente'. Estado actual: {estado}")
            return
        
        # Cambiar estado a Aceptado (esto automáticamente convierte a pedido)
        self.cambiar_estado_presupuesto(presupuesto_id, "Aceptado")
    
    def buscar_presupuesto(self):
        """Busca un presupuesto según el filtro"""
        filtro = self.filtro_presupuesto_var.get().strip()
        if not filtro:
            messagebox.showinfo("Buscar Presupuesto", "Por favor, ingrese un criterio de búsqueda")
            return
        
        self.cargar_datos_presupuestos(filtro)
    
    def mostrar_todos_presupuestos(self):
        """Muestra todos los presupuestos"""
        self.filtro_presupuesto_var.set("")
        self.cargar_datos_presupuestos()
    
    def cargar_datos_presupuestos(self, filtro=None):
        """Carga los datos de presupuestos en la tabla"""
        # Limpiar tabla
        for item in self.tabla_presupuestos.get_children():
            self.tabla_presupuestos.delete(item)
        
        try:
            # Obtener presupuestos
            df_presupuestos = self.presupuesto_controller.obtener_presupuestos()
            
            if df_presupuestos.empty:
                return
            
            # Aplicar filtro si se proporcionó
            if filtro:
                # Convertir todas las columnas a string para búsqueda
                df_filtrado = df_presupuestos.astype(str)
                
                # Aplicar filtro en todas las columnas
                mask = df_filtrado.apply(lambda x: x.str.contains(filtro, case=False).any(), axis=1)
                df_presupuestos = df_presupuestos[mask]
            
            # Agregar presupuestos a la tabla
            for _, row in df_presupuestos.iterrows():
                # Obtener datos del cliente
                cliente = self.cliente_controller.obtener_cliente_por_id(row['cliente_id'])
                cliente_nombre = f"{cliente.nombre} {cliente.apellido}" if cliente else "Cliente no encontrado"
                
                self.tabla_presupuestos.insert("", "end", values=(
                    row['id'],
                    cliente_nombre,
                    row['fecha'],
                    f"{row['validez']} días",
                    f"${float(row['total']):.2f}",
                    row['estado']
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar presupuestos: {str(e)}")
    
    def on_presupuesto_guardado(self, presupuesto):
        """Callback para cuando se guarda un presupuesto"""
        self.cargar_datos_presupuestos()

    def cambiar_estado_pedido(self, pedido_id, nuevo_estado, ventana=None):
        """Cambia el estado de un pedido"""
        try:
            # Confirmar cambio de estado
            confirmacion = messagebox.askyesno("Cambiar Estado", 
                                            f"¿Está seguro de cambiar el estado del pedido a '{nuevo_estado}'?")
            if not confirmacion:
                return
            
            # Actualizar estado usando el controlador
            resultado, mensaje = self.pedido_controller.cambiar_estado_pedido(pedido_id, nuevo_estado)
            
            if resultado:
                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", mensaje)
                
                # Actualizar tabla de pedidos
                self.cargar_datos_pedidos()
                
                # Actualizar barra de estado
                self.barra_estado.config(text=f"Estado del pedido #{pedido_id} cambiado a '{nuevo_estado}'")
                
                # Si hay una ventana de detalles abierta, cerrarla y abrir una nueva con los datos actualizados
                if ventana:
                    ventana.destroy()
                    # Seleccionar el pedido en la tabla para poder mostrar los detalles actualizados
                    self.seleccionar_pedido_en_tabla(pedido_id)
                    # Abrir nuevos detalles
                    self.ver_detalles_pedido()
            else:
                # Mostrar mensaje de error
                messagebox.showerror("Error", mensaje)
                
        except Exception as e:
            print(f"[MainWindow] Error al cambiar estado del pedido: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop() 