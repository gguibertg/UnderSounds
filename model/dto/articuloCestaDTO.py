import json
from .articuloDTO import ArticuloDTO
from .artistaDTO import ArtistaDTO

class ArticulosCestaDTO:
    def __init__(self):
        self.articulosCestaList = []

    def insertArticuloCesta(self, articuloCesta):
        self.articulosCestaList.append(articuloCesta)

    def articulosCestaList_to_json(self):
        return json.dumps(self.articulosCestaList)

class ArticuloCestaDTO:

    id: str
    articulo: ArticuloDTO
    artista: ArtistaDTO
    cantidad: int
    usuario: str

    def __init__(self):
        self.id = None
        self.articulo = None
        self.artista = None
        self.cantidad = None
        self.usuario = None

    def is_empty(self):
        return (self.id is None and self.articulo is None and self.artista is None and self.cantidad is None)

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_articulo(self):
        return self.articulo

    def set_articulo(self, articulo):
        self.articulo = articulo

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

    def articulocestadto_to_dict(self):
        return {
            "id": self.id,
            "articulo": self.articulo,
            "artista": self.artista,
            "cantidad": self.cantidad,
            "usuario": self.usuario
        }
