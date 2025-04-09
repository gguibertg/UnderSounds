from pydantic import BaseModel, Field
from typing import Set
from model.dto.cancion_dto import Cancion

class Biblioteca(BaseModel):
    id: str = Field(default=None)
    canciones: Set[Cancion]