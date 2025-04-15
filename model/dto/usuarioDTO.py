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
        self.studio_album: list[str] = []
        
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

    def set_studio_album(self, studio_album: list[str]):
        self.studio_album = studio_album

    def add_studio_album(self, album_id: str):
        self.studio_album.append(album_id)

    def remove_studio_album(self, album_id: str):
        if album_id in self.studio_album:
            self.studio_album.remove(album_id)

    def usuario_to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "bio": self.bio,
            "imagen": self.imagen,
            "url": self.url,
            "esArtista": self.esArtista,
            "studio_album": self.studio_album
        }