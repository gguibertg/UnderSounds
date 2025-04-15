from fastapi.templating import Jinja2Templates
from fastapi import Request
from API_KEYS import API_CREDENTIALS

templates = Jinja2Templates(directory="view/templates") # Esta ruta es la que se va a usar para renderizar las plantillas
# Las templates se cargaran y podrán incluir entradas especiales para cargar variables.
# Luego, las templates se renderizan y se devuelven al cliente como respuesta a la petición HTTP.

apicreds = API_CREDENTIALS() # Cargamos las credenciales de la API de Firebase

class View():

    def __init__(self): 
        pass


    # Esta función se va a usar para renderizar la template index.html
    def get_index_view(self, request: Request): 
        return templates.TemplateResponse("main/index.html", {"request" : request})
    
    # Renderizar la template login.html
    def get_login_view(self, request: Request):
        return templates.TemplateResponse("auth/login.html", {"request": request, "API_CREDENTIALS" : apicreds})

    # Renderizar la template profile.html
    # Necesita un user_info completo, no se contempla otro caso.
    def get_perfil_view(self, request: Request, user_info):
        return templates.TemplateResponse("user/profile.html", {"request": request, "user": user_info, "API_CREDENTIALS" : apicreds})
    
    # Renderizar la template register.html
    def get_register_view(self, request: Request):
        return templates.TemplateResponse("auth/register.html", {"request": request, "API_CREDENTIALS" : apicreds})
    
    # Renderizar la template faqs.html
    def get_faqs_view(self, request: Request, faqs):
        return templates.TemplateResponse("main/faqs.html", {
            "request": request,
            "faqs": faqs
        })

    # Renderizar la template about.html
    def get_about_view(self, request: Request):
        return templates.TemplateResponse("main/about.html", {"request" : request})
    

    

    # Esta función se va a usar para renderizar la template songs.html
    def get_songs_view(self, request: Request, songs):
        songs_list = json.loads(songs)
        # print(songs_list)
        # Renderizar la template con los parametros adecuados y devolverla al cliente.
        return templates.TemplateResponse("songs.html", {"request" :request, "songs" : songs_list})


    def get_contact_view(self, request : Request, success: int = 0): 
        return templates.TemplateResponse("main/contact.html", {"request" : request, "success" : success})
