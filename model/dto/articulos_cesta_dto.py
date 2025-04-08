from pydantic import BaseModel

class Articulo_cesta(BaseModel):
    id: str | None
    bio: str
    email: str
    imagen: str
    url: str
    telefono: int