from pydantic import BaseModel, Field
from typing import Union, List
from model.dto.merch_dto import Merch
from model.dto.cancion_dto import Cancion
from model.dto.album_dto import Album
from model.dto.generos_dto import Genero
class Tienda(BaseModel):
    id: str = Field(default=None)
    articulos: List[Union[Merch, Cancion, Album]] = Field(default="")
    genero: Genero
    
    