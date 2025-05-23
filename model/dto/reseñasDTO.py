import json
from .usuarioDTO import UsuarioDTO

class ReseñasDTO():
    def __init__(self):
        self.reseñalist = []

    def get_reseñalist(self):
        return self.reseñalist

    def insertReseña(self, elem):
        self.reseñalist.append(elem)

    def reseñalist_to_json(self):
        return json.dumps(self.reseñalist)

class ReseñaDTO():

    def __init__(self):
        self.id: str = None
        self.titulo: str = None
        self.reseña: str = None
        self.usuario: str = None

    def is_empty(self):
        return (self.id is None and self.titulo is None and self.reseña is None and self.usuario is None)

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_titulo(self) -> str:
        return self.titulo

    def set_titulo(self, titulo: str):
        self.titulo = titulo

    def get_reseña(self) -> str:
        return self.reseña

    def set_reseña(self, reseña: str):
        self.reseña = reseña

    def get_usuario(self) -> str:
        return self.usuario

    def set_usuario(self, usuario: str):
        self.usuario = usuario

    def reseñadto_to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "reseña": self.reseña,
            "usuario": self.usuario
        }
    
    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.titulo = data.get("titulo")
        self.reseña = data.get("reseña")
        self.usuario = data.get("usuario")