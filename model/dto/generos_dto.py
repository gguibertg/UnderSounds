from pydantic import BaseModel
from dto import Subgenero

class Genero(BaseModel):
    id: str | None
    nombre: str
    subgenero: Subgenero