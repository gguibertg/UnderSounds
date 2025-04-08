from pydantic import BaseModel
from dto import Usuario
class Cliente_msg(BaseModel):
    id: str | None
    usuario: Usuario
    mensaje: str
    