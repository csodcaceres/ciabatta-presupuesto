class Cliente:
    def __init__(self, id, nombre, apellido, email=None, telefono=None, direccion=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono = telefono
        self.direccion = direccion

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def actualizar_datos(self, email=None, telefono=None, direccion=None):
        if email:
            self.email = email
        if telefono:
            self.telefono = telefono
        if direccion:
            self.direccion = direccion

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion
        } 