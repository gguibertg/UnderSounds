from pydantic import BaseModel

class Pregunta(BaseModel):
    id: str | None
    pregunta: str
    respuesta: str