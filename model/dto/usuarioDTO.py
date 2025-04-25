import json
from datetime import date
from datetime import datetime

class UsuariosDTO():
    def __init__(self):
        self.userlist = []
        
    def insertUser(self, elem):
        self.userlist.append(elem)
        
    def deleteUser(self, elem):
        self.userlist.remove(elem)
        
    def userlist_to_json(self) -> str:
        return json.dumps(self.userlist)

class UsuarioDTO():
    def __init__(self):   
        self.id: str = None
        self.nombre: str = None
        self.bio: str = None
        self.email: str = None
        self.imagen: str = None
        self.url: str = None
        self.fechaIngreso: datetime = None
        self.esArtista: bool = None
        self.esVisible: bool = None
        self.emailVisible: bool = None
        self.studio_albumes: list[str] = []
        self.studio_canciones: list[str] = []
        self.biblioteca: list[str] = []
        self.listas_reproduccion: list[dict[str, list[str]]] = []
        self.id_likes: list[str] = []

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_nombre(self) -> str:
        return self.nombre

    def set_nombre(self, nombre: str):
        self.nombre = nombre

    def get_bio(self) -> str:
        return self.bio

    def set_bio(self, bio: str):
        self.bio = bio

    def get_email(self) -> str:
        return self.email

    def set_email(self, email: str):
        self.email = email

    def get_imagen(self) -> str:
        return self.imagen

    def set_imagen(self, imagen: str):
        self.imagen = imagen

    def get_url(self) -> str:
        return self.url

    def set_url(self, url: str):
        self.url = url

    def get_fechaIngreso(self) -> datetime:
        return self.fechaIngreso

    def set_fechaIngreso(self, fechaIngreso: datetime):
        self.fechaIngreso = fechaIngreso

    def get_esArtista(self) -> bool:
        return self.esArtista

    def set_esArtista(self, esArtista: bool):
        self.esArtista = esArtista

    def get_esVisible(self) -> bool:
        return self.esVisible

    def set_esVisible(self, esVisible: bool):
        self.esVisible = esVisible

    def get_emailVisible(self) -> bool:
        return self.emailVisible

    def set_emailVisible(self, emailVisible: bool):
        self.emailVisible = emailVisible

    def set_studio_albumes(self, studio_albumes: list[str]):
        self.studio_albumes = studio_albumes

    def add_studio_album(self, album_id: str):
        self.studio_albumes.append(album_id)

    def remove_studio_album(self, album_id: str):
        if album_id in self.studio_albumes:
            self.studio_albumes.remove(album_id)

    def set_studio_canciones(self, studio_canciones: list[str]):
        self.studio_canciones = studio_canciones

    def add_studio_cancion(self, cancion_id: str):
        self.studio_canciones.append(cancion_id)

    def remove_studio_cancion(self, cancion_id: str):
        if cancion_id in self.studio_canciones:
            self.studio_canciones.remove(cancion_id)

    def set_biblioteca(self, biblioteca: list[str]):
        self.biblioteca = biblioteca
    
    def get_biblioteca(self) -> list[str]:
        return self.biblioteca
    
    def add_song_to_biblioteca(self, song_id: str):
        if song_id not in self.biblioteca:
            self.biblioteca.append(song_id)
        
    def remove_song_from_biblioteca(self, song_id: str):
        if song_id in self.biblioteca:
            self.biblioteca.remove(song_id)

    def set_listas_reproduccion(self, listas_reproduccion: list[dict[str, list[str]]]):
        self.listas_reproduccion = listas_reproduccion

    def get_listas_reproduccion(self):
        return self.listas_reproduccion
    
    def add_lista_reproduccion(self, nombre: str):
        if not any(l["nombre"] == nombre for l in self.listas_reproduccion):
            self.listas_reproduccion.append({"nombre": nombre, "canciones": []})

    def remove_lista_reproduccion(self, nombre: str):
        for i, lista in enumerate(self.listas_reproduccion):
            if lista["nombre"] == nombre:
                del self.listas_reproduccion[i]
                return True
        return False  # Si no se encuentra

    def add_song_to_lista_reproduccion(self, nombre_lista: str, id_cancion: str):
        for lista in self.listas_reproduccion:
            if lista["nombre"] == nombre_lista:
                if id_cancion not in lista["canciones"]:
                    lista["canciones"].append(id_cancion)
                return True
        return False
    
    def remove_song_from_lista_reproduccion(self, nombre_lista: str, id_cancion: str):
        for lista in self.listas_reproduccion:
            if lista["nombre"] == nombre_lista:
                if id_cancion in lista["canciones"]:
                    lista["canciones"].remove(id_cancion)
                return True
        return False

    def get_canciones_from_lista_reproduccion(self, nombre: str):
        for lista in self.listas_reproduccion:
            if lista["nombre"] == nombre:
                return lista["canciones"]
        return None

    def set_id_likes(self, id_likes: list[str]):
        self.id_likes = id_likes

    def add_id_like(self, like_id: str):
        self.id_likes.append(like_id)

    def remove_id_like(self, like_id: str):
        if like_id in self.id_likes:
            self.id_likes.remove(like_id)

    def get_id_likes(self) -> list[str]:
        return self.id_likes

    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.nombre = data.get("nombre")
        self.bio = data.get("bio")
        self.email = data.get("email")
        self.imagen = data.get("imagen")
        self.url = data.get("url")
        self.fechaIngreso = data.get("fechaIngreso")
        self.esArtista = data.get("esArtista", False)
        self.esVisible = data.get("esVisible", True)
        self.emailVisible = data.get("emailVisible", True)
        self.studio_albumes = data.get("studio_albumes", [])
        self.studio_canciones = data.get("studio_canciones", [])
        self.biblioteca = data.get("biblioteca", [])
        self.listas_reproduccion = data.get("listas_reproduccion", [])
        self.id_likes = data.get("id_likes", [])

    def usuario_to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "bio": self.bio,
            "email": self.email,
            "imagen": self.imagen,
            "url": self.url,
            "fechaIngreso": self.fechaIngreso,
            "esArtista": self.esArtista,
            "esVisible": self.esVisible,
            "emailVisible": self.emailVisible,
            "studio_albumes": self.studio_albumes,
            "studio_canciones": self.studio_canciones,
            "id_likes": self.id_likes,
            "biblioteca": self.biblioteca,
            "listas_reproduccion": self.listas_reproduccion
        }