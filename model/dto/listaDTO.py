class ListaDTO:

    def __init__(self):
        self.id: str = None
        self.titulo: str = None
        self.descripcion: str = None
        self.lista_canciones: list[str] = []
        self.esPublico: bool = False

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_titulo(self) -> str:
        return self.titulo

    def set_titulo(self, titulo: str):
        self.titulo = titulo

    def get_descripcion(self) -> str:
        return self.descripcion

    def set_descripcion(self, descripcion: str):
        self.descripcion = descripcion

    def set_lista_canciones(self, lista_canciones: list[str]):
        self.lista_canciones = lista_canciones

    def add_cancion(self, cancion_id: str):
        self.lista_canciones.append(cancion_id)

    def remove_cancion(self, cancion_id: str):
        if cancion_id in self.lista_canciones:
            self.lista_canciones.remove(cancion_id)

    def get_esPublico(self) -> bool:
        return self.esPublico

    def set_esPublico(self, esPublico: bool):
        self.esPublico = esPublico

    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.titulo = data.get("titulo")
        self.descripcion = data.get("descripcion")
        self.lista_canciones = data.get("lista_canciones", [])
        self.esPublico = data.get("esPublico", False)

    def lista_to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "lista_canciones": self.lista_canciones,
            "esPublico": self.esPublico
        }
