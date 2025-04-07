"""
Módulo de la clase View.
Encargado de renderizar las vistas HTML utilizando Jinja2 y FastAPI.
"""

from fastapi.templating import Jinja2Templates
from fastapi import Request
import json

templates = Jinja2Templates(directory="view/templates") # Esta ruta es la que se va a usar para renderizar las plantillas
# Las templates se cargaran y podrán incluir entradas especiales para cargar variables.
# Luego, las templates se renderizan y se devuelven al cliente como respuesta a la petición HTTP.

# Esta clase es la que se va a usar para renderizar las templates.
class View():
    """
    Clase encargada de generar respuestas HTML a partir de plantillas.
    """

    # Al crear la clase no tenemos que hacer nada.
    def __init__(self): 
        """Inicializa la instancia de View."""
        pass

    # Esta función se va a usar para renderizar la template index.html
    def get_index_view(self, request: Request): 
        """
        Renderiza la vista principal de la aplicación.

        :param request: Objeto Request de FastAPI
        :return: Plantilla HTML renderizada
        """
        return templates.TemplateResponse("main/index.html", {"request" : request})
    
    # Esta función se va a usar para renderizar la template songs.html
    def get_songs_view(self, request: Request, songs):
        """
        Renderiza la vista con la lista de canciones.

        :param request: Objeto Request
        :param songs: Canciones en formato JSON
        :return: Plantilla HTML renderizada
        """
        songs_list = json.loads(songs)
        # print(songs_list)
        # Renderizar la template con los parametros adecuados y devolverla al cliente.
        return templates.TemplateResponse("songs.html", {"request" :request, "songs" : songs_list})
    

    
    # Seguir añadiendo funciones para renderizar las templates que se necesiten...

    def get_faqs_view(self, request: Request, faqs):
        """
        Renderiza la vista de preguntas frecuentes.

        :param request: Objeto Request
        :param faqs: Lista serializada de FAQs
        :return: Plantilla HTML renderizada
        """
        return templates.TemplateResponse("main/faqs.html", {"request": request, "faqs": faqs})


    