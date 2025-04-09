from pydantic import BaseModel, Field
from model.dto.cancion_dto import Cancion

class Lista_reproduccion(BaseModel):
    id: str = Field(default=None)
    cancion: Cancion
    