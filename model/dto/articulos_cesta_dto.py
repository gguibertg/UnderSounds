from pydantic import BaseModel, Field

class Articulo_cesta(BaseModel):
    id: str = Field(default=None)
    bio: str
    email: str
    imagen: str
    url: str
    telefono: int