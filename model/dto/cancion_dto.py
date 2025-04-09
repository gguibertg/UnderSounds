from pydantic import BaseModel, Field
from model.dto import Genero
from model.dto import Usuario
from model.dto import Reseña
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
    colaboradores: Usuario
    duracion: int
    fecha: datetime
    portada: str
    lista_reseñas: Reseña
    
    
    
    
    
    
    