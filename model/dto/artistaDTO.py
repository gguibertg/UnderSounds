import json

class ArtistasDTO:
    def __init__(self):
        self.artistasList = []

    def insertArtista(self, artista):
        self.artistasList.append(artista)

    def artistasList_to_json(self):
        return json.dumps(self.artistasList)

class ArtistaDTO:

    id: str
    nombre: str

    def __init__(self):
        self.id = None
        self.nombre = None
        
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def is_empty(self):
        return (self.id is None and self.nombre)

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_nombre(self):
        return self.nombre

    def set_nombre(self, nombre):
        self.nombre = nombre

    def faqdto_to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
        }
