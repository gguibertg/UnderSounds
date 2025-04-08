from pydantic import BaseModel

class Usuario(BaseModel):
    id: str | None
    bio: str
    email: str
    imagen: str
    url: str
    telefono: int