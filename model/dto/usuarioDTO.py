import json

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
        self.bio: str = None
        self.email: str = None
        self.imagen: str = None
        self.url: str = None
        self.nombre: str = None
        self.esArtista: bool = None
        self.studio_albumes: list[str] = []
        self.studio_canciones: list[str] = []
        
    def get_id(self) -> str:
        return self.id
    
    def get_bio(self) -> str:
        return self.bio
    
    def get_email(self) -> str:
        return self.email
    
    def get_imagen(self) -> str:
        return self.imagen
    
    def get_url(self) -> str:
        return self.url
    
    def get_nombre(self) -> str:
        return self.nombre
    
    def get_esArtista(self) -> bool:
        return self.esArtista
    
    def set_id(self, id: str):
        self.id = id
    
    def set_bio(self, bio: str):
        self.bio = bio
    
    def set_email(self, email: str):
        self.email = email
    
    def set_imagen(self, imagen: str):
        self.imagen = imagen
    
    def set_url(self, url: str):
        self.url = url
    
    def set_nombre(self, nombre: str):
        self.nombre = nombre
    
    def set_esArtista(self, esArtista: bool):
        self.esArtista = esArtista

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

    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.nombre = data.get("nombre")
        self.email = data.get("email")
        self.bio = data.get("bio")
        self.imagen = data.get("imagen")
        self.url = data.get("url")
        self.esArtista = data.get("esArtista", False)
        self.studio_albumes = data.get("studio_albumes", [])
        self.studio_canciones = data.get("studio_canciones", [])

    def usuario_to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "bio": self.bio,
            "imagen": self.imagen,
            "url": self.url,
            "esArtista": self.esArtista,
            "studio_albumes": self.studio_albumes,
            "studio_canciones": self.studio_canciones
        }