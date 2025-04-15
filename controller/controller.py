import os
import uuid
import firebase_admin
from datetime import datetime
from fastapi import FastAPI, Request, Response, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydub.utils import mediainfo
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
@app.get("/song/upload_song")
def login(request: Request):
    return view.get_upload_song_view(request)

# Ruta para procesar la petición de login
@app.post("/song/upload_song")
async def song_post(response: Response, request: Request, title: str = Form(...), author: str = Form(...), genres: str = Form(...), collaborators: str = Form(...), price: str = Form(...), album: str = Form(...), description: str = Form(...), cover_upload: str = Form(...), file: UploadFile = File(...)):
    
    try:
         # Guardar el archivo de la canción en el servidor
        file_location = f"uploads/{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)  # Crear el directorio si no existe
        with open(file_location, "wb") as f:
            f.write(await file.read())

        info = mediainfo(file)
        # Asignar la ruta del archivo a la canción (opcional dependiendo de tu modelo)
        song.set_file_location(file_location)
        
        song_id = str(uuid.uuid4())

        # Registrar la cancion en la base de datos
        song = SongDTO()
        song.set_id(song_id)
        song.set_title(title)
        song.set_artist(author)
        song.set_collaborators(collaborators)
        song.set_price(price)
        song.set_album(album)
        song.set_description(description)
        song.set_genres(genres)
        song.set_portada(cover_upload)
        song.set_date(datetime.now())
        song.set_duration(float(info['duration']))
        song.set_likes("")
        song.set_review_list("")
        song.set_views("")

        # Añadir el usuario a la base de datos
        if model.add_song(song):
            print(PCTRL, "Song registered in database")
        else:
            print(PCTRL_WARN, "Song registration failed in database!")
            return {"success": False, "error": "Song registration failed"}
    

        # Creamos una sesión para el usuario (login)
        cancion_id = str(uuid.uuid4())
        #Faltaría asignar vigencia a la sesión
        listSongs[cancion_id] = {"title": title, "song_id": song_id, "artist": author, "collaborators": collaborators, "price": price, 
                                 "description": description, "genres": song.set_genres, "portada": cover_upload, 
                                 "date": song.set_date, "duration": song.set_duration, "likes": song.set_likes, 
                                 "review_list": song.set_review_list, "views": song.set_views}
        response.set_cookie(key="cancion_id", value=cancion_id, httponly=True)
        print(PCTRL, "Song upload successful")
        return {"success": True}
        
    except Exception as e:
        print("Song upload failed due to", str(e))
        return {"success": False, "error": str(e)}
    
@app.get("/songs")
def get_songs(request: Request):
    songs_json = model.get_songs()
    return view.get_songs_view(request, songs_json)

@app.get("/song")
async def get_song(request: Request):
     # Comprobamos si el usuario tiene una sesión activa
    order_id = request.cookies.get("order_id")
    if not isSongValid(order_id):
        return Response("No autorizado", status_code=401)
    
    # Accedemos a los datos de la sesión del usuario
    song_data = getSongData(order_id)
    if song_data:
        song_id = song_data["song_id"]
        song_title = song_data["title"]
        print(PCTRL, "Song", song_title, "requested access to profile")

        # Accedemos a los datos del usuario en la base de datos
        song_info = model.get_song(song_id)

        if song_info:
            return view.get_song_view(request, song_info)
        else:
            print(PCTRL_WARN, "Song", song_title, "with id", song_id, "not found in database!")
        
    return Response("No autorizado", status_code=401)

    
@app.get("/song/edit_edit/{song_id}")
async def edit_song_post(request: Request):
    
    cancion_id = request.cookies.get("cancion_id")
    if not isSongValid(cancion_id):
        return Response("No autorizado", status_code=401)
    
    # Obtenemos los datos de usuario de la base de datos y creamos un nuevo objeto UsuarioDTO, utilizando los datos recibidos en el request
    data = await request.json()
    song_title = data["title"]
    song_artist = data["artist"]
    song_collaborators = data["collaborators"]
    song_price = data["price"]
    song_album = data["album"]
    song_description = data["description"]
    song_genres = data["genres"]
    song_portada = data["portada"]

    song_data = getSongData(cancion_id)
    song_id = song_data["song_id"]
    song_info = model.get_song(song_id)

    # Comprobamos si los cambios proporcionados no difieren de los que ya tiene el usuario, en cuyo caso no se haría nada (devuelve un mensaje de éxito)
    if song_info["title"] == song_title and song_info["artist"] == song_artist and song_info["collaborators"] == song_collaborators and song_info["price"] == song_price and song_info["album"] == song_album and song_info["description"] == song_description and song_info["genres"] == song_genres and song_info["portada"] == song_portada:
        print(PCTRL, "No changes to song")
        return {"success": True, "message": "No changes to song"}

    song = SongDTO()
    song.set_id(song_id)
    song.set_title(song_title)
    song.set_artist(song_artist)
    song.set_collaborators(song_collaborators)
    song.set_price(song_price)
    song.set_album(song_album)
    song.set_description(song_description)
    song.set_genres(song_genres)
    song.set_portada(song_portada)
    song.set_date(song_info["date"])
    song.set_duration(song_info["duration"])
    song.set_likes(song_info["likes"])
    song.set_review_list(song_info["review_list"])
    song.set_views(song_info["views"])

    # Actualizar el usuario en la base de datos
    if model.update_song(song):
        print(PCTRL, "Song", song_title, "updated in database")
        return {"success": True, "message": "Song updated successfully"}
    else:
        print(PCTRL_WARN, "Song", song_title, "not updated in database!")
        return {"success": False, "error": "User not updated in database"}

# --------------------------- MÉTODOS AUXILIARES --------------------------- #
def isSongValid(cancion_id : str) -> bool:
    return cancion_id and cancion_id in listSongs and model.get_song(listSongs[cancion_id]["song_id"])

# Un session contiene un name, user_id y el tipo de login (google o credentials)
def getSongData(cancion_id: str) -> str:
    if cancion_id in listSongs:
        return listSongs[cancion_id]
    return None
    