from pydantic import BaseModel
from dto import Usuario

class Reseña(BaseModel):
    id: str | None
    reseña: str
    usuario: Usuario