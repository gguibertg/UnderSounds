import json
from .reseñasDTO import ReseñaDTO

class SongsDTO():
    def __init__(self):
        self.songlist = []

    def get_songlist(self):
        return self.songlist

    def insertSong(self, elem):
        self.songlist.append(elem)

    def songlist_to_json(self):
        return json.dumps(self.songlist)

class SongDTO():

    def __init__(self):
        self.id: str = None
        self.titulo: str = None
        self.artista: str = None
        self.colaboradores: list[str] = []
        self.fecha: str = None
        self.descripcion: str = None
        self.duracion: str = None
        self.generos: list[str] = []
        self.likes: int = None
        self.visitas: int = None
        self.portada: str = None
        self.precio: float = None
        self.lista_resenas: list[dict] = []
        self.visible: bool = None
        self.album: str = None

    def is_empty(self):
        return (self.id is None and self.titulo is None and 
                self.artista is None and self.colaboradores is None and 
                self.fecha is None and self.descripcion is None and 
                self.duracion is None and self.generos is None and 
                self.likes is None and self.visitas is None and 
                self.portada is None and self.precio is None and 
                self.lista_resenas is None and self.visible is None and 
                self.album is None)

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_titulo(self) -> str:
        return self.titulo

    def set_titulo(self, titulo: str):
        self.titulo = titulo

    def get_artista(self) -> str:
        return self.artista

    def set_artista(self, artista: str):
        self.artista = artista

    def get_colaboradores(self) -> list[str]:
        return self.colaboradores

    def set_colaboradores(self, colaboradores: list[str]):
        self.colaboradores = colaboradores

    def get_fecha(self) -> str:
        return self.fecha

    def set_fecha(self, fecha: str):
        self.fecha = fecha

    def get_descripcion(self) -> str:
        return self.descripcion

    def set_descripcion(self, descripcion: str):
        self.descripcion = descripcion

    def get_duracion(self) -> str:
        return self.duracion

    def set_duracion(self, duracion: str):
        self.duracion = duracion

    def get_generos(self) -> list[str]:
        return self.generos

    def add_genero(self, genero_id: str):
        self.generos.append(genero_id)

    def remove_genero(self, genero_id: str):
        if genero_id in self.generos:
            self.generos.remove(genero_id)

    def set_generos(self, generos: list[str]):
        self.generos = generos

    def get_likes(self) -> int:
        return self.likes

    def set_likes(self, likes: int):
        self.likes = likes

    def get_visitas(self) -> int:
        return self.visitas

    def set_visitas(self, visitas: int):
        self.visitas = visitas

    def get_portada(self) -> str:
        return self.portada

    def set_portada(self, portada: str):
        self.portada = portada

    def get_precio(self) -> float:
        return self.precio

    def set_precio(self, precio: float):
        self.precio = precio

    def get_lista_resenas(self) -> list[dict]:
        return self.lista_resenas
    
    def add_resenas(self, resenas: dict):
        self.lista_resenas.append(resenas)

    def update_resenas(self, resenas: dict):
        for i, r in enumerate(self.lista_resenas):
            if r["id"] == resenas["id"]:
                r["titulo"] = resenas["titulo"]
                r["reseña"] = resenas["reseña"]

    def remove_resena(self, resenas: dict):
        if resenas in self.lista_resenas:
            self.lista_resenas.remove(resenas)

    def set_lista_resenas(self, lista_resenas: list[dict]):
        self.lista_resenas = lista_resenas

    def get_visible(self) -> bool:
        return self.visible

    def set_visible(self, visible: bool):
        self.visible = visible

    def get_album(self) -> str:
        return self.album

    def set_album(self, album: str):
        self.album = album

    def songdto_to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "artista": self.artista,
            "colaboradores": self.colaboradores,
            "fecha": self.fecha,
            "descripcion": self.descripcion,
            "duracion": self.duracion,
            "generos": self.generos,
            "likes": self.likes,
            "visitas": self.visitas,
            "portada": self.portada,
            "precio": self.precio,
            "lista_resenas": self.lista_resenas,
            "visible": self.visible,
            "album": self.album
        }
    
    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.titulo = data.get("titulo")
        self.artista = data.get("artista")
        self.colaboradores = data.get("colaboradores")
        self.fecha = data.get("fecha")
        self.descripcion = data.get("descripcion")
        self.duracion = data.get("duracion")
        self.generos = data.get("generos", [])
        self.likes = data.get("likes")
        self.visitas = data.get("visitas")
        self.portada = data.get("portada")
        self.precio = data.get("precio")
        self.lista_resenas = data.get("lista_resenas", [])
        self.visible = data.get("visible")
        self.album = data.get("album")
