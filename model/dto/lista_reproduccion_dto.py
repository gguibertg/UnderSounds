from pydantic import BaseModel
from dto import Cancion

class Lista_reproduccion(BaseModel):
    id: str | None
    cancion: Cancion
    