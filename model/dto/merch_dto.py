from pydantic import BaseModel
from dto import Usuario

class Merch(BaseModel):
    id: str | None
    precio: int
    artista: Usuario
    titulo: str
    portada: str