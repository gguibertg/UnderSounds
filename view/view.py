from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="view/templates") # Esta ruta es la que se va a usar para renderizar las plantillas

class View():

    def __init__(self): 
        pass

    def get_index_view(self, request: Request): 
        return templates.TemplateResponse("main/index.html", {"request" : request})
    
    # Esta función se va a usar para renderizar la template songs.html
    def get_upload_song_view(self, request: Request):
        return templates.TemplateResponse("music/upload-song.html", {"request": request})
    
    def get_songs_view(self, request: Request, songs):
        return templates.TemplateResponse("main/index.html", {"request" :request, "songs" : songs})
    
    def get_song_view(self, request: Request, song_info):
        return templates.TemplateResponse("music/song.html", {"request": request, "song": song_info})

    def get_edit_song_view(self, request: Request, song_info):
        return templates.TemplateResponse("music/song-edit.html", {"request": request, "song": song_info})
    
    # Seguir añadiendo funciones para renderizar las templates que se necesiten...