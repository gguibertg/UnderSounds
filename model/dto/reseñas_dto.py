from pydantic import BaseModel, Field
from model.dto import Usuario

class Reseña(BaseModel):
    id: str = Field(default=None)
    reseña: str
    usuario: Usuario