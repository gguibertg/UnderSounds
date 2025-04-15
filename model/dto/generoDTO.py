class GeneroDTO:
    def __init__(self):
        self.id: str = None
        self.nombre: str = None

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_titulo(self) -> str:
        return self.titulo

    def set_titulo(self, titulo: str):
        self.titulo = titulo

    def genero_to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo
        }