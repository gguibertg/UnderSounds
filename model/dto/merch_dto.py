from pydantic import BaseModel, Field
from model.dto import Usuario

class Merch(BaseModel):
    id: str = Field(default=None)
    precio: int
    artista: Usuario
    titulo: str
    portada: str