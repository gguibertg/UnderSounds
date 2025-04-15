class AlbumDTO:
    def __init__(self):
        self.id: str = None
        self.titulo: str = None
        self.autor: str = None
        self.descripcion: str = None
        self.fecha: str = None
        self.generos: list[str] = []
        self.canciones: list[str] = []
        self.nVisualizaciones: int = None
        self.portada: str = None
        self.precio: float = None

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_titulo(self) -> str:
        return self.titulo

    def set_titulo(self, titulo: str):
        self.titulo = titulo

    def get_autor(self) -> str:
        return self.autor

    def set_autor(self, autor: str):
        self.autor = autor

    def get_descripcion(self) -> str:
        return self.descripcion

    def set_descripcion(self, descripcion: str):
        self.descripcion = descripcion

    def get_fecha(self) -> str:
        return self.fecha

    def set_fecha(self, fecha: str):
        self.fecha = fecha

    def set_generos(self, generos: list[str]):
        self.generos = generos

    def add_genero(self, genero_id: str):
        self.generos.append(genero_id)

    def remove_genero(self, genero_id: str):
        if genero_id in self.generos:
            self.generos.remove(genero_id)

    def set_canciones(self, canciones: list[str]):
        self.canciones = canciones

    def add_cancion(self, cancion_id: str):
        self.canciones.append(cancion_id)

    def remove_cancion(self, cancion_id: str):
        if cancion_id in self.canciones:
            self.canciones.remove(cancion_id)

    def get_nVisualizaciones(self) -> int:
        return self.nVisualizaciones

    def set_nVisualizaciones(self, nVisualizaciones: int):
        self.nVisualizaciones = nVisualizaciones

    def get_portada(self) -> str:
        return self.portada

    def set_portada(self, portada: str):
        self.portada = portada

    def get_precio(self) -> float:
        return self.precio

    def set_precio(self, precio: float):
        self.precio = precio

    def album_to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "descripcion": self.descripcion,
            "fecha": self.fecha,
            "genero": self.generos,
            "canciones": self.canciones,
            "nVisualizaciones": self.nVisualizaciones,
            "portada": self.portada,
            "precio": self.precio
        }