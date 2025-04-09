from pydantic import BaseModel, Field

class Concierto(BaseModel):
    id: str = Field(default=None)
    nombre: str
    precio: str