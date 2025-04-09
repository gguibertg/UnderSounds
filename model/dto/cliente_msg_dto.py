from pydantic import BaseModel, Field
from model.dto import Usuario
class Cliente_msg(BaseModel):
    id: str = Field(default=None)
    usuario: Usuario
    mensaje: str
    