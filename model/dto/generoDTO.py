import json

class GenerosDTO:
    def __init__(self):
        self.generolist = []

    def get_generolist(self):
        return self.generolist

    def insertGenero(self, elem):
        self.generolist.append(elem)

    def generolist_to_json(self):
        return json.dumps(self.generolist)


class GeneroDTO:
    def __init__(self):
        self.id: str = None
        self.nombre: str = None
        self.esSubGen: bool = False

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_nombre(self) -> str:
        return self.nombre

    def set_nombre(self, nombre: str):
        self.nombre = nombre

    def get_esSubGen(self) -> bool:
        return self.esSubGen
    
    def set_esSubGen(self, esSubGen: bool):
        self.esSubGen = esSubGen

    def genero_to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "esSubGen": self.esSubGen
        }