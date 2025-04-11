import json

class UsuariosDTO():
    def _init_(self):
        self.userlist = []
        
    def insertUser (self, elem):
        self.userlist.append(elem)
        
    def deleteUser (self, elem):
        self.userlist.remove(elem)
        
    def userlist_to_json(self):
        return json.dumps(self.userlist)
        
        
class UsuarioDTO():
    def _init_(self):
        self.id = None
        self.bio = None
        self.email = None
        self.contraseña = None
        self.imagen = None
        self.url = None
        self.nombre = None
        self.telefono = None
        self.esArtista = None
        
    def get_id(self):
        return self.id
    
    def get_bio(self):
        return self.bio
    
    def get_email(self):
        return self.email
    
    def get_contrasena(self):
        return self.contraseña
    
    def get_imagen(self):
        return self.imagen
    
    def get_url(self):
        return self.url
    
    def get_nombre(self):
        return self.nombre
    
    def get_telefono(self):
        return self.telefono
    
    def get_esArtista(self):
        return self.esArtista
    
    def set_id(self, id):
        self.id = id
    
    def set_bio(self, bio):
        self.bio = bio
    
    def set_email(self, email):
        self.email = email
    
    def set_contrasena(self, contraseña):
        self.contraseña = contraseña
    
    def set_imagen(self, imagen):
        self.imagen = imagen
    
    def set_url(self, url):
        self.url = url
    
    def set_nombre(self, nombre):
        self.nombre = nombre
    
    def set_telefono(self, telefono):
        self.telefono, telefono
    
    def set_esArtista(self, esArtista):
        self.esArtista = esArtista
    
    def usuario_to_dict(self):
        return {
            "id": self.id,
            "bio": self.bio,
            "email": self.email,
            "contraseña": self.contraseña,
            "imagen": self.imagen,
            "url": self.url,
            "nombre": self.nombre,
            "telefono": self.telefono
        }