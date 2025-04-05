from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
templates = Jinja2Templates(directory="view/templates") # Esta ruta es la que se va a usar para renderizar las plantillas
# Las templates se cargaran y podrán incluir entradas especiales para cargar variables.
# Luego, las templates se renderizan y se devuelven al cliente como respuesta a la petición HTTP.

# Esta clase es la que se va a usar para renderizar las templates.
class View():


    # Al crear la clase no tenemos que hacer nada.
    def __init__(self): 
        pass

    # Esta función se va a usar para renderizar la template index.html
    def get_index_view(self, request: Request): 
        return templates.TemplateResponse("index.html", {"request" : request})
    
    # Esta función se va a usar para renderizar la template songs.html
    def get_songs_view(self, request: Request, songs):
        songs_list = json.loads(songs)
        # print(songs_list)
        # Renderizar la template con los parametros adecuados y devolverla al cliente.
        return templates.TemplateResponse("songs.html", {"request" :request, "songs" : songs_list})
    

    
    # Seguir añadiendo funciones para renderizar las templates que se necesiten...