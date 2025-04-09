from pydantic import BaseModel, Field
from model.dto import Subgenero

class Genero(BaseModel):
    id: str = Field(default=None)
    nombre: str
    subgenero: Subgenero