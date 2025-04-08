from pydantic import BaseModel
from dto import Cancion
from dto import Usuario
from datetime import datetime
from dto import Genero

class Album(BaseModel):
    id: str | None
    title: str
    lista_canciones: Cancion
    portada: str
    precio: int
    autor: Usuario
    descripcion: str
    fecha: datetime
    genero: Genero
    nCanciones: int
    nVisualizaciones: int