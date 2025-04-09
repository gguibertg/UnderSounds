from pydantic import BaseModel, Field
from model.dto import Cancion
from model.dto import Usuario
from datetime import datetime
from model.dto import Genero

class Album(BaseModel):
    id: str = Field(default=None)
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