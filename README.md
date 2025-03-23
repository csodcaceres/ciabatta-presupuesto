# Sistema de Gestión de Pedidos y Presupuestos para Ciabatta

Sistema desarrollado en Python para la gestión de pedidos, presupuestos y clientes de Ciabatta Panadería.

## Características

- **Gestión de Clientes**: Agregar, editar, eliminar y buscar clientes.
- **Gestión de Productos**: Administrar el catálogo de productos.
- **Gestión de Pedidos**: Crear, editar y dar seguimiento a pedidos.
- **Gestión de Presupuestos**: Crear presupuestos para clientes que luego pueden convertirse en pedidos.
- **Reportes**: Generar reportes de ventas y otros datos importantes.
- **Excel Integration**: Almacenamiento de datos usando Excel para fácil manejo.

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)
- Pandas
- Openpyxl

## Instalación

1. Clonar o descargar este repositorio
2. Instalar las dependencias:

```bash
pip install pandas openpyxl
```

3. Ejecutar el programa:

```bash
python main.py
```

## Estructura del Proyecto

El proyecto sigue el patrón MVC (Modelo-Vista-Controlador):

- **app/models/**: Definiciones de clases de datos (Cliente, Producto, Pedido, Presupuesto)
- **app/views/**: Interfaces gráficas
- **app/controllers/**: Lógica de negocio
- **app/utils/**: Utilidades como la gestión de Excel
- **data/**: Almacenamiento de archivos Excel

## Funcionalidades Principales

### Gestión de Clientes

- Agregar nuevos clientes con sus datos de contacto
- Búsqueda y filtrado de clientes
- Edición y eliminación de registros

### Gestión de Productos

- Mantenimiento del catálogo de productos
- Precios y categorías
- Búsqueda de productos

### Gestión de Pedidos

- Creación de pedidos asociados a clientes
- Seguimiento del estado (pendiente, en proceso, completado)
- Historial de pedidos por cliente

### Gestión de Presupuestos

- Creación de presupuestos para clientes
- Agregar múltiples ítems con precios y descuentos
- Manejo de validez del presupuesto (en días)
- Estados: Pendiente, Aceptado, Rechazado
- Conversión automática de presupuestos aceptados a pedidos

## Uso del Sistema

### Creación de Presupuestos

1. Seleccione la pestaña "Presupuestos"
2. Haga clic en "Nuevo Presupuesto"
3. Seleccione un cliente o cree uno nuevo
4. Agregue los ítems al presupuesto con sus cantidades, precios y descuentos
5. Especifique la validez del presupuesto en días
6. Guarde el presupuesto

### Conversión de Presupuesto a Pedido

1. Seleccione un presupuesto en estado "Pendiente"
2. Pulse el botón "Convertir a Pedido" o "Aceptar Presupuesto" en la vista detallada
3. Confirme la operación
4. El sistema creará automáticamente un nuevo pedido basado en el presupuesto

## Licencia

Este proyecto es software privado desarrollado para Ciabatta Panadería.
