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
@app.get("/upload-song")
def song_post(request: Request):
    return view.get_upload_song_view(request)

# Ruta para procesar la petición de login
@app.post("/upload-song")
async def song_post(request: Request):

# Registrar la cancion en la base de datos
    data = await request.json()

    song = SongDTO()
    song.set_titulo(data["titulo"])
    song.set_artista(data["artista"])
    song.set_colaboradores(data["colaboradores"])
    song.set_fecha(datetime.strptime(data["fecha"], "%Y-%m-%d"))
    song.set_descripcion(data["descripcion"])
    song.set_generos(data["generos"])
    song.set_likes(0)
    song.set_visitas(0)
    song.set_portada(data["portada"])
    song.set_precio(data["precio"])
    song.set_lista_resenas([])
    song.set_visible(True)

    song_id = model.add_song(song)
   
    if song_id is not None:
        print(PCTRL, "Song registered in database")
    else:
        print(PCTRL_WARN, "Song registration failed in database!")
        return {"success": False, "error": "Song registration failed"}
    
@app.get("/songs")
def get_songs(request: Request):
    songs_json = model.get_songs()
    return view.get_songs_view(request, songs_json)

@app.get("/song")
async def get_song(request: Request):
    if request.query_params.get("id") is not None:
        song_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        song_id = data["id"]

    if not song_id:
        return Response("Falta el parámetro 'id'", status_code=400)

    song_info = model.get_song(song_id)

    if not song_info:
        print(PCTRL_WARN, "La cancion no existe")
        return Response("No autorizado", status_code=403)
    
    return view.get_song_view(request, song_info)

    
    
@app.get("/edit-song")
async def edit_song_post(request: Request):
    
    if request.query_params.get("id") is not None:
        song_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        song_id = data["id"]

    if not song_id:
        return Response("Falta el parámetro 'id'", status_code=400)

    song_info = model.get_song(song_id)

    if not song_info:
        print(PCTRL_WARN, "Song does not exist")
        return Response("No autorizado", status_code=403)

    return view.get_edit_song_view(request, song_info)

@app.post("/edit-song")
async def edit_song_post(request: Request):
    try:
        # Recibimos los datos del nuevo album editado, junto con su ID.
        data = await request.json()
        song_id = data["id"] # ID del album a editar

        # Descargamos el album antiguo de la base de datos via su ID.
        song_dict = model.get_song(song_id)
        song = SongDTO()
        song.load_from_dict(song_dict)

        song.set_titulo(data["titulo"])
        song.set_artista(data["artista"])
        song.set_colaboradores(data["colaboradores"])
        song.set_descripcion(data["descripcion"])
        song.set_generos(data["generos"])
        song.set_portada(data["portada"])
        song.set_precio(data["precio"])

        # Actualizamos el album en la base de datos
        if model.update_song(song):
            print(PCTRL, "Song", song_id, "updated in database")
            return {"success": True, "message": "Album updated successfully"}
        else:
            print(PCTRL_WARN, "Song", song_id, "not updated in database!")
            return {"success": False, "error": "Album not updated in database"}
    
    except Exception as e:
        print(PCTRL_WARN, "Error while processing Song", song_id, ", updating to database failed!")
        return {"success": False, "error": "Song not updated in database"}