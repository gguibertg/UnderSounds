import json

class ArticulosCestaDTO:
    def __init__(self):
        self.articulosCestaList = []

    def insertArticuloCesta(self, articuloCesta):
        self.articulosCestaList.append(articuloCesta)

    def articulosCestaList_to_json(self):
        return json.dumps(self.articulosCestaList)

class ArticuloCestaDTO:

    id: str
    precio: str
    nombre: str
    descripcion: str
    artista: str
    cantidad: int
    usuario: str
    imagen: str

    def __init__(self):
        self.id = None
        self.precio = None
        self.nombre = None
        self.descripcion = None
        self.artista = None
        self.cantidad = None
        self.usuario = None
        self.imagen = None

    def is_empty(self):
        return (self.id is None and self.precio is None and self.nombre is None and
                self.descripcion is None and self.artista is None and self.cantidad is None
                and self.usuario is None and self.imagen is None)

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
        
    def get_descripcion(self):
        return self.descripcion
    
    def set_descripcion(self, descripcion):
        self.descripcion = descripcion

    def get_artista(self):
        return self.artista

    def set_artista(self, artista):
        self.artista = artista
        
    def get_cantidad (self):
        return self.cantidad
    
    def set_cantidad(self, cantidad):
        self.cantidad = cantidad
        
    def get_usuario(self):
        return self.usuario
    
    def set_usuario(self, usuario):
        self.usuario = usuario
        
    def get_imagen(self):
        return self.imagen
    
    def set_imagen(self, imagen):
        self.imagen = imagen

    def articulocestadto_to_dict(self):
        return {
            "id": self.id,
            "precio": self.precio,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "artista": self.artista,
            "cantidad": self.cantidad,
            "usuario": self.usuario,
            "imagen": self.imagen
        }
