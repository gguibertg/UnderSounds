import os
import uuid
import firebase_admin
from datetime import datetime
from fastapi import FastAPI, Request, Response, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from view.view import View
from model.model import Model
from pathlib import Path
from firebase_admin import credentials
from model.dto.songDTO import SongDTO

# Variable para el color + modulo de la consola
PCTRL = "\033[96mCTRL\033[0m:\t "
PCTRL_WARN = "\033[96mCTRL\033[0m|\033[93mWARN\033[0m:\t "



# ===============================================================================
# ========================= INICIALIZACIÓN DE LA APP ============================
# ===============================================================================

# Inicializamos la app
app = FastAPI()

# Inicializar Firebase
if not Path("credentials.json").is_file():
    print("\033[91mERROR: credentials.json file not found!\033[0m")
    exit(1)
    
# Cargamos las credenciales de Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# Montamos directorios estáticos para servir archivos CSS, JS, imágenes, etc.
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)
app.mount(
    "/includes",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "view/templates/includes"),
    name="static",
)

# Inicializamos el controlador y el modelo
view = View()
model = Model()

# Almacenamiento en memoria para sesiones
listSongs = {}

# ===============================================================================
# =========================== DEFINICIÓN DE RUTAS ===============================
# ===============================================================================

# Con el decorador @app.get() le decimos a FastAPI que esta función se va a usar para manejar las peticiones GET a la ruta X.
# En este caso, la ruta es la raíz de la app ("/").
# La función index se va a usar para renderizar la template index.html.
@app.get("/")
def index(request: Request): 
    return view.get_index_view(request)

# ----------------------------- Ver Cancion ------------------------------ #

# Ruta para cargar vista login
@app.get("/upload_song")
def song_post(request: Request):
    return view.get_upload_song_view(request)

# Ruta para procesar la petición de login
#@app.post("/song/upload_song")
#async def song_post(request: Request):

    # Registrar la cancion en la base de datos
#   data = await request.json()

#    song = SongDTO()
#    song.set_title(data["title"])
#    song.set_artist(data["artist"])
#    song.set_collaborators(data["collaborators"])
#    song.set_price(data["price"])
#    song.set_album(data["album"])
#    song.set_description(data["description"])
#    song.set_genres(data["genres"])
#    song.set_portada(data["portada"])
#    song.set_date(datetime.now())
#    song.set_likes(0)
#    song.set_review_list([])
#    song.set_views(0)

#    song_id = model.add_song(song)
   
#    if song_id is not None:
#        print(PCTRL, "Song registered in database")
#    else:
#        print(PCTRL_WARN, "Song registration failed in database!")
#        return {"success": False, "error": "Song registration failed"}
    
@app.get("/songs")
def get_songs(request: Request):
    songs_json = model.get_songs()
    return view.get_songs_view(request, songs_json)

#@app.get("/song")
#async def get_song(request: Request):
     # Comprobamos si el usuario tiene una sesión activa
#    data = await request.json()
#    song_id = data["id"]

#    if not song_id:
#        return Response("No autorizado", status_code=401)
    
    # Accedemos a los datos del usuario en la base de datos
#    song_info = model.get_song(song_id)

#    if not song_info:
#        print(PCTRL_WARN, "Song does not exist")
#        return Response("No autorizado", status_code=403)

#    print(song_info)
#    return view.get_song_view(request, song_info)

    
#@app.get("/song/edit_edit")
#async def edit_song_post(request: Request):
    
    # Obtenemos los datos de usuario de la base de datos y creamos un nuevo objeto UsuarioDTO, utilizando los datos recibidos en el request
#    data = await request.json()
#    song_id = data["id"]

#    if not song_id:
#        print(PCTRL_WARN, "Song ID not provided in request")
#        return Response("No autorizado", status_code=400)

#    song_info = model.get_song(song_id)

#    if not song_info:
#        print(PCTRL_WARN, "Song does not exist")
#        return Response("No autorizado", status_code=403)

#    print(song_info)
#    return view.get_edit_song_view(request, song_info)

#@app.post("/song/edit_edit")
#async def edit_song_post(request: Request):
    # Registrar la cancion en la base de datos
#    data = await request.json()

#    song = SongDTO()
#    song.set_title(data["title"])
#    song.set_artist(data["artist"])
#    song.set_collaborators(data["collaborators"])
#    song.set_price(data["price"])
#    song.set_album(data["album"])
#    song.set_description(data["description"])
#    song.set_genres(data["genres"])
#    song.set_portada(data["portada"])
#    song.set_date(data["date"])
#    song.set_duration(data["duration"])
#    song.set_likes(data["likes"])
#    song.set_review_list(data["review_list"])
#    song.set_views(data["views"])

#    song_id = model.update_song(song)
#    if song_id is not None:
#        print(PCTRL, "Song registered in database")
#    else:
#        print(PCTRL_WARN, "Song registration failed in database!")
#        return {"success": False, "error": "Song registration failed"}