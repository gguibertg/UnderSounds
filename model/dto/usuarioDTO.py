import json

class UsuariosDTO():
    def __init__(self):
        self.userlist = []
        
    def insertUser (self, elem):
        self.userlist.append(elem)
        
    def deleteUser (self, elem):
        self.userlist.remove(elem)
        
    def userlist_to_json(self):
        return json.dumps(self.userlist)
        
        
class UsuarioDTO():
    def __init__(self):
        self.id = None
        self.bio = None
        self.email = None
        self.imagen = None
        self.url = None
        self.nombre = None
        self.esArtista = None
        
    def get_id(self):
        return self.id
    
    def get_bio(self):
        return self.bio
    
    def get_email(self):
        return self.email
    
    def get_imagen(self):
        return self.imagen
    
    def get_url(self):
        return self.url
    
    def get_nombre(self):
        return self.nombre
    
    def get_esArtista(self):
        return self.esArtista
    
    def set_id(self, id):
        self.id = id
    
    def set_bio(self, bio):
        self.bio = bio
    
    def set_email(self, email):
        self.email = email
    
    def set_imagen(self, imagen):
        self.imagen = imagen
    
    def set_url(self, url):
        self.url = url
    
    def set_nombre(self, nombre):
        self.nombre = nombre
    
    def set_esArtista(self, esArtista):
        self.esArtista = esArtista

    def usuario_to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "bio": self.bio,
            "imagen": self.imagen,
            "url": self.url,
            "esArtista": self.esArtista
        }