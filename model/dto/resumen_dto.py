from pydantic import BaseModel, Field
from typing import Union, List
from model.dto.merch_dto import Merch
from model.dto.cancion_dto import Cancion
from model.dto.album_dto import Album
class Resumen(BaseModel):
    id: str = Field(default=None)
    subtotal: int = Field(default=0)
    articulos: List[Union[Merch, Cancion, Album]] = Field(default="")