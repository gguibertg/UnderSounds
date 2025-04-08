from pydantic import BaseModel

class Concierto(BaseModel):
    id: str | None
    nombre: str
    precio: str