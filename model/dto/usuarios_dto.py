from pydantic import BaseModel, Field


class Usuario(BaseModel):
    id: str = Field(default=None)
    bio: str = Field(default="")
    email: str 
    contraseña: str
    imagen: str = Field(default="")
    url: str = Field(default="")
    nombre: str = Field(default="")
    telefono: int = Field(default=0)
    esArtista: bool = Field(default=False)