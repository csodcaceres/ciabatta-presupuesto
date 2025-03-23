import sys
import os
import tkinter as tk

# Agregar directorio raíz al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.views.main_window import MainWindow

def main():
    """Función principal que inicia la aplicación"""
    # Crear ventana principal
    root = tk.Tk()
    
    # Ajustar tema
    try:
        # Intentar usar un tema más moderno si está disponible
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        # Si no está disponible, usar el tema predeterminado
        pass
    
    # Inicializar aplicación
    app = MainWindow(root)
    
    # Iniciar loop principal
    root.mainloop()

if __name__ == "__main__":
    main() 