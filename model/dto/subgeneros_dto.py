from pydantic import BaseModel, Field

class Subgenero(BaseModel):
    id: str = Field(default=None)
    nombre: str