from pydantic import BaseModel, Field
class Tienda(BaseModel):
    id: str = Field(default=None)
    
    
    