from pydantic import BaseModel

class Biblioteca(BaseModel):
    id: str | None
    bio: str
    email: str
    imagen: str
    url: str
    telefono: int