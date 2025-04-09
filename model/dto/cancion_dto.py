from pydantic import BaseModel, Field
from typing import Set, List
from model.dto.generos_dto import Genero
from model.dto.usuarios_dto import Usuario
from model.dto.reseñas_dto import Reseña
from datetime import datetime

class Cancion(BaseModel):
    id: str = Field(default=None)
    nLikes: int
    nVisualizaciones: int
    album: str
    artista: Usuario
    descripcion: str
    genero: Genero
    precio: int
    titulo: str
    colaboradores: Set[Usuario]
    duracion: int
    fecha: datetime
    portada: str
    lista_reseñas: List[Reseña]
    
    
    
    
    
    
    