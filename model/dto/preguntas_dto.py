from pydantic import BaseModel, Field

class Pregunta(BaseModel):
    id: str = Field(default=None)
    pregunta: str
    respuesta: str