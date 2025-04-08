from pydantic import BaseModel
from dto import Genero
from dto import Usuario
from dto import Reseña
from datetime import datetime

class Cancion(BaseModel):
    id: str | None
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
    
    
    
    
    
    
    