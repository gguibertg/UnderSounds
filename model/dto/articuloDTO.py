import json

class ArticulosDTO:
    def __init__(self):
        self.articulosList = []

    def insertArticulo(self, articulo):
        self.articulosList.append(articulo)

    def articulosList_to_json(self):
        return json.dumps(self.articulosList)

class ArticuloDTO:

    id: str
    precio: str
    nombre: str
    descripcion: str

    def __init__(self):
        self.id = None
        self.precio = None
        self.nombre = None
        self.descripcion = None
        
    def __init__(self, id, precio, nombre, descripcion):
        self.id = id
        self.precio = precio
        self.nombre = nombre
        self.descripcion = descripcion

    def is_empty(self):
        return (self.id is None and self.precio is None and self.nombre is None and self.descripcion is None)

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_precio(self):
        return self.precio

    def set_precio(self, precio):
        self.precio = precio

    def get_nombre(self):
        return self.nombre

    def set_nombre(self, nombre):
        self.nombre = nombre
        
    def get_descripcion (self):
        return self.descripcion
        
    def set_descripcion (self, descripcion):
        self.descripcion = descripcion

    def faqdto_to_dict(self):
        return {
            "id": self.id,
            "precio": self.precio,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }
