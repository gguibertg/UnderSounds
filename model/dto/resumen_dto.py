from pydantic import BaseModel

class Resumen(BaseModel):
    id: str | None
    bio: str
    email: str
    imagen: str
    url: str
    telefono: int