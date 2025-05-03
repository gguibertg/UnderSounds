from fastapi.templating import Jinja2Templates
from fastapi import Request
from API_KEYS import API_CREDENTIALS

templates = Jinja2Templates(directory="view/templates") # Esta ruta es la que se va a usar para renderizar las plantillas
apicreds = API_CREDENTIALS() # Cargamos las credenciales de la API de Firebase

class View():

    def __init__(self): 
        pass

    # Esta función se va a usar para renderizar la template index.html
    def get_index_view(self, request: Request, songs, genres, artistas, albums, tipoUsuario: bool): 
        return templates.TemplateResponse("main/index.html", {"request" :request, "songs" : songs, "genres": genres, "artistas": artistas, "albums": albums, "tipoUsuario": tipoUsuario})
    # Esta función se va a usar para renderizar la template songs.html
    def get_upload_song_view(self, request: Request):
        return templates.TemplateResponse("music/upload-song.html", {"request": request})
    
    def get_songs_view(self, request: Request, songs):
        return templates.TemplateResponse("main/index.html", {"request" :request, "songs" : songs})
    
    def get_song_view(self, request: Request, song_info : dict, tipoUsuario: int, user, isLiked: bool, inCarrito: bool):
        return templates.TemplateResponse("music/song.html", {"request": request, "song": song_info, "tipoUsuario": tipoUsuario, "usuario": user, "isLiked": isLiked, "inCarrito": inCarrito})

    def get_edit_song_view(self, request: Request, song_info):
        return templates.TemplateResponse("music/song-edit.html", {"request": request, "song": song_info})
    
    # Renderizar la template login.html
    def get_login_view(self, request: Request):
        return templates.TemplateResponse("auth/login.html", {"request": request, "API_CREDENTIALS" : apicreds })

    # Renderizar la template logut.html
    def get_logout_view(self, request: Request):
        return templates.TemplateResponse("auth/logout.html", {"request": request, "API_CREDENTIALS" : apicreds })

    # Renderizar la template profile.html
    # Necesita un user_info completo, no se contempla otro caso.
    def get_perfil_view(self, request: Request, usuario_data, canciones_biblioteca, listas_completas):
        return templates.TemplateResponse("user/profile.html", {
            "request": request,
            "user": usuario_data,
            "canciones_biblioteca": canciones_biblioteca,
            "listas_completas": listas_completas,
            "API_CREDENTIALS" : apicreds
        })
    
    # Renderizar la template register.html
    def get_register_view(self, request: Request):
        return templates.TemplateResponse("auth/register.html", {"request": request, "API_CREDENTIALS" : apicreds })
    
    # Renderizar la template faqs.html
    def get_faqs_view(self, request: Request, faqs):
        return templates.TemplateResponse("main/faqs.html", {"request": request, "faqs": faqs })
    
    # Renderizar la template album-edit.html
    def get_album_edit_view(self, request: Request, album_info : dict, songs: list[dict]):
        return templates.TemplateResponse("music/album-edit.html", {"request": request, "album": album_info, "songs": songs})

    # Renderizar la template upload-album.html
    def get_upload_album_view(self, request: Request, songs: list[dict]):
        return templates.TemplateResponse("music/upload-album.html", {"request": request , "songs": songs}) 
    
    # Renderizar la template album.html
    def get_album_view(self, request: Request, album_info : dict, tipoUsuario : int, isLiked: bool, inCarrito: bool, tiempo_formateado: str):
        return templates.TemplateResponse("music/album.html", {"request": request, "album": album_info, "tipoUsuario": tipoUsuario, "isLiked": isLiked, "inCarrito": inCarrito, "duracion_total": tiempo_formateado})
    
    # Renderizar la template header.html
    def get_header_view(self, request: Request, user_info : dict):
        return templates.TemplateResponse("includes/header.html", {"request": request, "user": user_info})
    
    # Renderizar la template footer.html
    def get_footer_view(self, request: Request, user_info : dict):
        return templates.TemplateResponse("includes/footer.html", {"request": request, "user": user_info})

    # Renderizar la template about.html
    def get_about_view(self, request: Request):
        return templates.TemplateResponse("main/about.html", {"request" : request})

    # Renderizar la template contact.html
    def get_contact_view(self, request : Request): 
        return templates.TemplateResponse("main/contact.html", {"request" : request})
        
    # Renderizar la template carrito.html
    def get_carrito_view(self, request: Request, carrito : dict):
        return templates.TemplateResponse("shop/cart.html", {"request": request, "carrito": carrito})

    # Renderizar la template prepaid.html
    def get_prepaid_view(self, request: Request, carrito : dict):
        return templates.TemplateResponse("shop/prepaid.html", {"request": request, "carrito": carrito})
    
    # Renderizar la template tpv.html
    def get_tpv_view(self, request: Request):
        return templates.TemplateResponse("shop/tpv.html", {"request": request})
    
    # Renderizar la template studio.html
    def get_studio_view(self, request: Request, songs: list[dict], albums: list[dict], user: dict):
        return templates.TemplateResponse("user/studio.html", {"request": request, "songs": songs, "albums": albums, "user" : user})
    
    # Renderizar la template artista.html
    def get_artista_view(self, request: Request, artista: dict, singles: list[dict], albums: list[dict], songs: list[dict], tipoUsuario: int):
        return templates.TemplateResponse("shop/artista.html", {"request": request, "artista" : artista, "singles" : singles, "albums" : albums, "songs" : songs, "tipoUsuario" : tipoUsuario})    
    
    # Esta función se va a usar para renderizar la template index.html
    def get_play_view(self, request: Request): 
        return templates.TemplateResponse("includes/radio.html", {"request" : request})

    # Renderizar la template purchased.html
    def get_purchased_view(self, request: Request, user, songs):
        return templates.TemplateResponse("shop/purchased.html", {"request": request, "usuario": user, "songs": songs})
    
    # Renderizar la template search.html
    def get_search_view(self, request: Request, all_items : list[dict]):
        return templates.TemplateResponse("main/search.html", {"request": request, "items": all_items})