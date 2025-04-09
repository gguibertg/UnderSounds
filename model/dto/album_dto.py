from pydantic import BaseModel, Field
from typing import Set
from model.dto.cancion_dto import Cancion
from model.dto.usuarios_dto import Usuario
from datetime import datetime
from model.dto.generos_dto import Genero

class Album(BaseModel):
    id: str = Field(default=None)
    title: str
    lista_canciones: Set[Cancion]
    portada: str
    precio: int
    autor: Usuario
    descripcion: str
    fecha: datetime
    genero: Set[Genero]
    nCanciones: int
    nVisualizaciones: int