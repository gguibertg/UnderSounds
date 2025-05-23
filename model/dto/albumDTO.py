import json
from datetime import datetime

class AlbumsDTO:
    def __init__(self):
        self.albumlist = []

    def get_albumlist(self):
        return self.albumlist

    def insertSong(self, elem):
        self.albumlist.append(elem)

    def albumlist_to_json(self):
        return json.dumps(self.albumlist)

class AlbumDTO:
    def __init__(self):
        self.id: str = None
        self.titulo: str = None
        self.autor: str = None
        self.colaboradores: str = None # Si, se que es un string y no una lista, pero a quien le importa realmente? Nunca lo vamos a usar como una lista de todas formas
        self.descripcion: str = None
        self.fecha: str = None
        self.fechaUltimaModificacion: str = None
        self.generos: list[str] = []
        self.canciones: list[str] = []       
        self.visitas: int = None
        self.portada: str = None
        self.precio: float = None
        self.likes: int = None
        self.visible: bool = None
        self.historial: list[dict] = []

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

    def get_colaboradores(self) -> str:
        return self.colaboradores
    
    def set_colaboradores(self, colaboradores: str):
        self.colaboradores = colaboradores

    def get_descripcion(self) -> str:
        return self.descripcion

    def set_descripcion(self, descripcion: str):
        self.descripcion = descripcion

    def get_fecha(self) -> str:
        return self.fecha

    def set_fecha(self, fecha: str):
        self.fecha = fecha

    def get_fechaUltimaModificacion(self) -> str:
        return self.fechaUltimaModificacion
    
    def set_fechaUltimaModificacion(self, fecha: str):
        self.fechaUltimaModificacion = fecha

    def set_generos(self, generos: list[str]):
        self.generos = generos

    def add_genero(self, genero_id: str):
        self.generos.append(genero_id)

    def remove_genero(self, genero_id: str):
        if genero_id in self.generos:
            self.generos.remove(genero_id)

    def get_generos(self) -> list[str]:
        return self.generos

    def set_canciones(self, canciones: list[str]):
        self.canciones = canciones

    def add_cancion(self, cancion_id: str):
        self.canciones.append(cancion_id)

    def remove_cancion(self, cancion_id: str):
        if cancion_id in self.canciones:
            self.canciones.remove(cancion_id)

    def get_canciones(self) -> list[str]:
        return self.canciones

    def get_visitas(self) -> int:
        return self.visitas

    def set_visitas(self, visitas: int):
        self.visitas = visitas

    def get_portada(self) -> str:
        return self.portada

    def set_portada(self, portada: str):
        self.portada = portada

    def get_precio(self) -> float:
        return self.precio

    def set_precio(self, precio: float):
        self.precio = precio

    def get_likes(self) -> int:
        return self.likes

    def set_likes(self, likes: int):
        self.likes = likes

    def get_visible(self) -> bool:
        return self.visible

    def set_visible(self, visible: bool):
        self.visible = visible

    def get_historial(self) -> list[dict]:
        return self.historial
    
    def add_historial(self, old_song_dict: dict):
        def clean_historial(d: dict) -> dict:
            cleaned = dict(d)  # copia superficial
            cleaned.pop("historial", None)  # elimina historial si existe
            return cleaned
        
        cleaned_version = clean_historial(old_song_dict)
        self.historial.append(cleaned_version)

    def remove_historial(self, historial: dict):
        if historial in self.historial:
            self.historial.remove(historial)

    def set_historial(self, historial: list[dict]):
        self.historial = historial

    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.titulo = data.get("titulo")
        self.autor = data.get("autor")
        self.colaboradores = data.get("colaboradores")
        self.descripcion = data.get("descripcion")
        self.fecha = data.get("fecha")
        self.fechaUltimaModificacion = data.get("fechaUltimaModificacion")
        self.generos = data.get("generos", [])
        self.canciones = data.get("canciones", [])
        self.visitas = data.get("visitas")
        self.portada = data.get("portada")
        self.precio = data.get("precio")
        self.likes = data.get("likes")
        self.visible = data.get("visible")
        self.historial = []
        for entry in data.get("historial", []):
            if isinstance(entry, dict):
                cleaned = {k: v for k, v in entry.items() if k != "historial"}
                self.historial.append(cleaned)

    def album_to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "colaboradores": self.colaboradores,
            "descripcion": self.descripcion,
            "fecha": self.fecha,
            "fechaUltimaModificacion": self.fechaUltimaModificacion,
            "generos": self.generos,
            "canciones": self.canciones,
            "visitas": self.visitas,
            "portada": self.portada,
            "precio": self.precio,
            "likes": self.likes,
            "visible": self.visible,
            "historial": [self._clean_historial_entry(h) for h in self.historial or []]
        }
    
    def _clean_historial_entry(self, h: dict) -> dict:
        return {k: v for k, v in h.items() if k != "historial"}
    
    def revert_to_version_by_fecha(self, fecha_objetivo: str) -> bool:

        try:
            fecha_objetivo_dt = datetime.fromisoformat(fecha_objetivo)
        except ValueError:
            print("Error: La fecha objetivo no tiene un formato válido.")
            return False

        for version in reversed(self.historial):  # reversed para ir de la más reciente a la más antigua
            fecha_version = version.get("fechaUltimaModificacion")

            if isinstance(fecha_version, str):
                try:
                    fecha_version_dt = datetime.fromisoformat(fecha_version)
                except ValueError:
                    continue  # ignorar si no es válida
            else:
                fecha_version_dt = fecha_version

            if fecha_version_dt and fecha_version_dt <= fecha_objetivo_dt:
                self._load_partial(version)
                return True

        return False # No se encontró una versión anterior a esa fecha

    def _load_partial(self, data: dict):
        #Carga solo los campos de edición
        self.titulo = data.get("titulo")
        self.autor = data.get("autor")
        self.colaboradores = data.get("colaboradores")
        self.descripcion = data.get("descripcion")
        self.generos = data.get("generos", [])
        self.portada = data.get("portada")
        self.precio = data.get("precio")
        self.visible = data.get("visible")
        self.canciones = data.get("canciones")