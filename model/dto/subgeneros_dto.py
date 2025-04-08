from pydantic import BaseModel

class Subgenero(BaseModel):
    id: str | None
    nombre: str