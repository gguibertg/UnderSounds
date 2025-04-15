class GeneroDTO:
    def __init__(self):
        self.id: str = None
        self.nombre: str = None

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_nombre(self) -> str:
        return self.nombre

    def set_nombre(self, nombre: str):
        self.nombre = nombre

    def genero_to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre
        }