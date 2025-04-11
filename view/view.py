from fastapi.templating import Jinja2Templates
from fastapi import Request
import json

templates = Jinja2Templates(directory="view/templates") # Esta ruta es la que se va a usar para renderizar las plantillas
# Las templates se cargaran y podrán incluir entradas especiales para cargar variables.
# Luego, las templates se renderizan y se devuelven al cliente como respuesta a la petición HTTP.

# Esta clase es la que se va a usar para renderizar las templates.
class View():

    def __init__(self): 
        pass

    def get_index_view(self, request: Request): 
        return templates.TemplateResponse("main/index.html", {"request" : request})
    
    def get_about_view(self, request: Request):
        return templates.TemplateResponse("main/about.html", {"request" : request})
    
