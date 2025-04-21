from datetime import datetime
# Imports estándar de Python
import uuid
import json
import requests
import base64from pathlib import Path

# Imports de terceros
import firebase_admin
from bson import ObjectId
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from firebase_admin import auth, credentials

# Imports locales del proyecto
from model.dto.carritoDTO import ArticuloCestaDTO, CarritoDTO
from model.dto.usuarioDTO import UsuarioDTO
from model.dto.albumDTO import AlbumDTO
from model.model import Model
from view.view import View


# Variable para el color + modulo de la consola
PCTRL = "\033[96mCTRL\033[0m:\t "
PCTRL_WARN = "\033[96mCTRL\033[0m|\033[93mWARN\033[0m:\t "

# ===============================================================================
# ========================= INICIALIZACIÓN DE LA APP ============================
# ===============================================================================

# Instancia principal de la app
app = FastAPI()

# Inicializar Firebase
if not Path("credentials.json").is_file():
    print("\033[91mERROR: credentials.json file not found!\033[0m")
    exit(1)
    
# Cargamos las credenciales de Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# Montamos directorios estáticos para servir archivos CSS, JS, imágenes, etc.
# Montaje de archivos estáticos
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)

app.mount(
    "/includes",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "view/templates/includes"),
    name="includes",
)

# Inicializamos el controlador y el modelo# Inicialización de la vista y del modelo
view = View()
model = Model()

# Almacenamiento en memoria para sesiones
sessions = {}

# ===============================================================================
# =========================== DEFINICIÓN DE RUTAS ===============================
# ===============================================================================

@app.get("/")
def index(request: Request):
    return view.get_index_view(request)

# En este caso servimos la template songs.html al cliente cuando se hace una petición GET a la ruta "/getsongs".
@app.get("/getsongs", description="Hola esto es una descripcion")
def getsongs(request: Request):
    # Vamos a llamar al Model para que nos devuelva la lista de canciones en formato JSON.
    songs = model.get_songs() # JSON
    # Luego se lo pasamos al View para que lo renderice y lo devuelva al cliente.
    return view.get_songs_view(request,songs)

# ------------------------------------------------------------------ #
# ----------------------------- LOGIN ------------------------------ #
# ------------------------------------------------------------------ #

# Ruta para cargar vista login
@app.get("/login")
def login(request: Request):
    return view.get_login_view(request)

# Ruta para procesar la petición de login
@app.post("/login")
async def login_post(data: dict, response: Response, provider: str):
    token = data.get("token")
    try:

        # Verificamos el token de Firebase dado por el usuario
        decoded_token = auth.verify_id_token(token)
        # Identificador único del usuario otorgado por Firebase que podemos usar como identificador del usuario en nuestra base de datos
        user_id = decoded_token["uid"]
        user_email = decoded_token["email"]
        print(PCTRL, "User login:")
        print(PCTRL, "\tUser email: ", user_email)
        print(PCTRL, "\tUser user_id: ", user_id)
        print(PCTRL, "\tUser provider: ", provider)

        # Comprobar que el usuario existe en la base de datos
        if not model.get_usuario(user_id):
            # Eliminar al usuario de Firebase Auth
            auth.delete_user(user_id)
            print(PCTRL_WARN, "User is logged into Firebase, but not registered in database! Logon failed")
            return {"success": False, "error": "User is not registered in database"}

        # Creamos una sesión para el usuario
        session_id = str(uuid.uuid4())
        #Faltaría asignar vigencia a la sesión
        sessions[session_id] = {"name": user_email, "user_id": user_id, "type": provider}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        print(PCTRL, "User logon successful")
        return {"success": True}
        
    except Exception as e:
        print("User logon failed due to", str(e))
        return {"success": False, "error": str(e)}

# Ruta para procesar la petición de login con credenciales clásicas
@app.post("/login-credentials")
async def login_credentials(data: dict, response: Response):
    return await login_post(data, response, "credentials")

# Ruta para procesar la petición de login con credenciales de Google
@app.post("/login-google")
async def login_google(data: dict, response: Response):
    return await login_post(data, response, "google")

@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    print(PCTRL, "User session", session_id, "is logging out")
    if session_id in sessions:
        del sessions[session_id]
    print(PCTRL, "User session", session_id, "destroyed")
    response.delete_cookie("session_id")
    return {"success": True}

# --------------------------------------------------------------------- #
# ----------------------------- REGISTER ------------------------------ #
# --------------------------------------------------------------------- #

# Ruta para cargar vista login
@app.get("/register")
def register(request: Request):
    return view.get_register_view(request)

# Ruta para procesar la petición de login
@app.post("/register")
async def register_post(data: dict, response: Response, provider: str):
    token = data.get("token")

    try:
        # Verificamos el token de Firebase dado por el usuario
        decoded_token = auth.verify_id_token(token)
        # Identificador único del usuario otorgado por Firebase que podemos usar como identificador del usuario en nuestra base de datos
        
        if provider == "credentials":
            username = data.get("username")  # Recogemos el campo username del JSON
        else:
            username = decoded_token["name"]  # Recogemos el nombre del token de Google
        
        user_id = decoded_token["uid"]
        user_email = decoded_token["email"]
        print(PCTRL, "User registering:")
        print(PCTRL, "\tUser username: ", username)
        print(PCTRL, "\tUser email: ", user_email)
        print(PCTRL, "\tUser user_id: ", user_id)
        print(PCTRL, "\tUser provider: ", provider)

        # Registrar usuario en la base de datos (simulada)
        # Verificar si el usuario ya está registrado en la base de datos
        if model.get_usuario(user_id):
            print(PCTRL, "User already registered in database")
            return {"success": False, "error": "User already registered"}

        # Registrar al usuario en la base de datos
        user = UsuarioDTO()
        user.set_id(user_id)
        user.set_nombre(username)
        user.set_email(user_email)
        user.set_bio("")
        if provider == "credentials":
            user.set_imagen("/static/img/default_profile.png")  # Imagen por defecto para usuarios registrados con credenciales clásicas
        else:
            # Descargar la imagen de Google, la convierte a base64 y la guarda en el campo imagen del usuario
            user.set_imagen("data:image/jpeg;base64," + base64.b64encode(requests.get(decoded_token["picture"]).content).decode("utf-8"))

        user.set_url("")
        user.set_esArtista(bool(data.get("esArtista", False)))

        # Añadir el usuario a la base de datos
        if model.add_usuario(user):
            print(PCTRL, "User registered in database")
        else:
            print(PCTRL_WARN, "User registration failed in database!")
            return {"success": False, "error": "User registration failed"}
        
        # Creamos una sesión para el usuario (login)
        session_id = str(uuid.uuid4())
        #Faltaría asignar vigencia a la sesión
        sessions[session_id] = {"name": user_email, "user_id": user_id, "type": provider}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        print(PCTRL, "User logon successful")
        return {"success": True}
        
    except Exception as e:
        print("User register failed due to", str(e))
        return {"success": False, "error": str(e)}

# Ruta para procesar la petición de login con credenciales clásicas
@app.post("/register-credentials")
async def register_credentials(data: dict, response: Response):
    return await register_post(data, response, "credentials")

# Ruta para procesar la petición de login con credenciales de Google
@app.post("/register-google")
async def register_google(data: dict, response: Response):
    return await register_post(data, response, "google")

# Ruta para procesar la petición de logout
@app.post("/unregister")
async def deregister(request: Request, response: Response):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  

    print(PCTRL, "User", res["email"], "requested account deletion") 

    try:
        # Eliminar al usuario de Firebase Auth
        auth.delete_user(res["id"])
        print(PCTRL, "User", res["email"], "deleted from Firebase Auth")

        # Eliminar cada una de las canciones en studio_canciones de la base de datos
        for song_id in res["studio_canciones"]:
            if model.delete_song(song_id):
                print(PCTRL, "Song", song_id, "deleted from database")
            else:
                print(PCTRL_WARN, "Song", song_id, "not deleted from database!")
                return {"success": False, "error": "Song not deleted from database"}
        
        # Eliminar cada uno de los albumes en studio_albumes de la base de datos
        for album_id in res["studio_albumes"]:
            if model.delete_album(album_id):
                print(PCTRL, "Album", album_id, "deleted from database")
            else:
                print(PCTRL_WARN, "Album", album_id, "not deleted from database!")
                return {"success": False, "error": "Album not deleted from database"}

        # Eliminar al usuario de la base de datos
        if model.delete_usuario(res["id"]):
            print(PCTRL, "User", res["email"], "deleted from database")
        else:
            print(PCTRL_WARN, "User", res["email"], "not deleted from database!")
            return {"success": False, "error": "User not deleted from database"}

        # Eliminar la sesión del usuario
        session_id = request.cookies.get("session_id")
        del sessions[session_id]
        response.delete_cookie("session_id")
        print(PCTRL, "User session", session_id, "destroyed")

        return {"success": True, "message": "User account deleted successfully"}
    
    except Exception as e:
        print(PCTRL, "Error deleting user:", str(e))
        return {"success": False, "error": str(e)}

# ------------------------------------------------------------------- #
# ----------------------------- PERFIL ------------------------------ #
# ------------------------------------------------------------------- #

# Ruta para cargar la vista de perfil
@app.get("/profile")
async def get_profile(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error
    
    return view.get_perfil_view(request, res)  # Si es un dict, pasamos los datos del usuario


# Ruta para actualizar el perfil del usuario
@app.post("/update-profile")
async def update_profile(request: Request, response: Response):
    # Verificar si el usuario tiene una sesión activa
    session_id = request.cookies.get("session_id")
    if not isUserSessionValid(session_id):
        return Response("No autorizado", status_code=401)
    
    # Obtenemos los datos de usuario de la base de datos y creamos un nuevo objeto UsuarioDTO, utilizando los datos recibidos en el request
    data = await request.json()
    user_name = data["nombre"]
    user_email = data["email"]
    user_url = data["url"]
    user_bio = data["bio"]
    user_imagen = data["imagen"]

    session_data = getSessionData(session_id)
    user_id = session_data["user_id"]
    user_info = model.get_usuario(user_id)

    # Comprobamos si los cambios proporcionados no difieren de los que ya tiene el usuario, en cuyo caso no se haría nada (devuelve un mensaje de éxito)
    if user_info["nombre"] == user_name and user_info["email"] == user_email and user_info["bio"] == user_bio and user_info["imagen"] == user_imagen and user_info["url"] == user_url:
        print(PCTRL, "No changes to user profile")
        return {"success": True, "message": "No changes to user profile"}

    user = UsuarioDTO()
    user.set_id(user_id)
    user.set_nombre(user_name)
    user.set_email(user_email)
    user.set_bio(user_bio)
    user.set_imagen(user_imagen)
    user.set_url(user_url)
    user.set_esArtista(user_info["esArtista"])

    # Actualizar el usuario en la base de datos
    if model.update_usuario(user):
        print(PCTRL, "User", user_name, "updated in database")
        return {"success": True, "message": "User updated successfully"}
    else:
        print(PCTRL_WARN, "User", user_name, "not updated in database!")
        return {"success": False, "error": "User not updated in database"}


# --------------------------- FAQS --------------------------- #

@app.get("/faqs", description="Muestra preguntas frecuentes desde MongoDB")
def get_faqs(request: Request):
    faqs_json = model.get_faqs()
    return view.get_faqs_view(request, faqs_json)



# ----------------------------- ALBUM ------------------------------ #

# Ruta para cargar la vista de upload-album
@app.get("/upload-album")
async def get_upload_album(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
    # Preparamos para escoger las songs validas para un album nuevo
    # Para ello, debemos coger todas las canciones creadas por el usuario (campo studio_canciones) y que no pertenezcan a ningun album.
    # Para comprobar que no pertenezcan a ningun album, debemos descargar todos los albumes y comprobar en el campo canciones de cada uno de ellos que esa cancion no esté.
    # Debemos recordar que tanto studio_canciones como studio_albumes como el campo canciones de un album son listas de IDs de strings de canciones, albumes y canciones respectivamente.
    # Por lo tanto, para cada string encontrado hay que hacer su llamada a model correspondiente para obtener el objeto real y pasarlo a la vista.
    # Excepto en el caso de las canciones de un album, ya que solo necesitamos el ID y nada más.
    
    # Por cada canción en studio_canciones, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "User created Song", song_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)

    # Por cada album en studio_albumes, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "User created Album", album_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)

    # Comprobar que por cada canción en studio_canciones, no esté en el campo canciones de ningun album
    # Cada canción que cumpla esta condición se añadira a la lista de canciones admitidas para el nuevo album
    valid_songs = []        
    for song in user_songs_objects:
        # Comprobar si la canción está en el campo canciones de algún álbum
        found = False
        for album in user_albums_objects:
            if song["id"] in album["canciones"]:
                found = True
                break
        if not found:
            valid_songs.append(song)

    return view.get_upload_album_view(request, valid_songs)


# Ruta para subir un álbum
@app.post("/upload-album")
async def upload_album(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
    # Creamos un nuevo objeto AlbumDTO, utilizando los datos recibidos en el request
    data = await request.json()

    album = AlbumDTO()
    album.set_titulo(data["titulo"])
    album.set_autor(data["autor"])
    album.set_colaboradores(data["colaboradores"])
    album.set_descripcion(data["descripcion"])
    album.set_fecha(datetime.strptime(data["fecha"], "%Y-%m-%d")) # Convertimos el string tipo YYYY-MM-DD a un objeto datetime antes de guardar.
    album.set_generos(data["generos"])
    album.set_canciones(data["canciones"])
    album.set_visitas(0)
    album.set_portada(data["portada"])
    album.set_precio(data["precio"])

    # Subir el album a la base de datos
    album_id = model.add_album(album)
    if album_id is not None:
        print(PCTRL, "Album", album_id, "uploaded to database")
    else:
        print(PCTRL_WARN, "Album", album_id, "not uploaded to database!")
        return {"success": False, "error": "Album not uploaded to database"}

    try: 
        # Obtenemos los datos de usuario de la base de datos y creamos un nuevo objeto UsuarioDTO
        # Ya tenemos estos datos (res), solo necesitamos castearlos.
        user = UsuarioDTO()
        user.load_from_dict(res)

        # Añadimos al usuario la nueva referencia al album
        user.add_studio_album(album_id)

        # Actualizamos el usuario en la base de datos
        if model.update_usuario(user):
            print(PCTRL, "User", user.get_email(), "updated in database")
            return {"success": True, "message": "Album uploaded successfully"}
        else:
            raise Exception("User not updated in database")
        
    except Exception as e:
        print(PCTRL_WARN, "User", user.get_email(), "not updated in database!")

        # Destruir el album subido
        model.delete_album(album_id)
        print(PCTRL_WARN, "Album", album_id, "deleted from database")
        return {"success": False, "error": "User not updated in database"}


# Ruta para cargar la vista de album
@app.get("/album")
async def get_album(request: Request):
    #Leemos de la request el id del album y recogemos el album de la BD
    if request.query_params.get("id") is not None:
        album_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        album_id = data["id"]

    
# Ruta para cargar la vista de álbum-edit
@app.get("/album-edit")
async def get_album_edit(request: Request):
    #Leemos de la request el id del album y recogemos el album de la BD
    if request.query_params.get("id") is not None:
        album_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        album_id = data["id"]
    if not album_id:
        print(PCTRL_WARN, "Album ID not provided in request")
        return Response("No autorizado", status_code=400)

    # Verificar si el usuario tiene una sesión activa, si es artista y si el album existe, y si le pertenece.
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    album_info = model.get_album(album_id)
    if not album_info:
        print(PCTRL_WARN, "Album does not exist")
        return Response("No autorizado", status_code=403)
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "Album not found in user albums")
        return Response("No autorizado", status_code=403)

    # Ahora popularemos el album reemplazando las IDs (referencias) por los objetos reales
    
    #generos_out : list[dict] = []
    #for genero_id in album_info["generos"]:
    #    genero = model.get_genero(genero_id)
    #    if not genero:
    #        print(PCTRL_WARN, "Genero", genero_id ,"not found in database")
    #        return Response("Error del sistema", status_code=403)
    #    generos_out.append(genero["nombre"])
    #album_info["generos"] = generos_out
    #
    # TODO: Al descargar un album ya vienen con IDs de generos que coinciden en nombre, por lo que no es necesario hacer la llamada a la BD para obtener el objeto real.

    canciones_out : list[dict] = []
    for cancion_id in album_info["canciones"]:
        cancion = model.get_song(cancion_id)
        if not cancion:
            print(PCTRL_WARN, "Cancion", cancion_id, "not found in database")
            return Response("Error del sistema", status_code=403)   
        canciones_out.append(cancion)
    album_info["canciones"] = canciones_out

    # Ya tenemos el album preparado. Pero ahora, tenemos que emular basicamente la misma funcionalidad que en upload-album, para que el artista pueda editar el album con nuevas canciones.
    # Así pues, copiamos y pegamos el código de upload-album para obtener las canciones válidas para un album nuevo.

    # Por cada canción en studio_canciones, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "Song", song_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)

    # Por cada album en studio_albumes, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "Album", album_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)

    # Comprobar que por cada canción en studio_canciones, no esté en el campo canciones de ningun album
    # Cada canción que cumpla esta condición se añadira a la lista de canciones admitidas para el nuevo album
    valid_songs = []        
    for song in user_songs_objects:
        # Comprobar si la canción está en el campo canciones de algún álbum
        found = False
        for album in user_albums_objects:
            if song["id"] in album["canciones"]:
                found = True
                break
        if not found:
            valid_songs.append(song)

    # Devolvemos todo
    return view.get_album_edit_view(request, album_info, valid_songs)


# Ruta para subir un álbum
@app.post("/album-edit")
async def upload_album(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
    try:
        # Recibimos los datos del nuevo album editado, junto con su ID.
        data = await request.json()
        album_id = data["id"] # ID del album a editar

        # Descargamos el album antiguo de la base de datos via su ID.
        album_dict = model.get_album(album_id)
        album = AlbumDTO()
        album.load_from_dict(album_dict)

        # Editamos el album con los nuevos datos recibidos en la request
        album.set_titulo(data["titulo"])
        album.set_autor(data["autor"])
        album.set_colaboradores(data["colaboradores"])
        album.set_descripcion(data["descripcion"])
        #album.set_fecha(datetime.strptime(data["fecha"], "%Y-%m-%d")) # La fecha no se puede editar.
        album.set_generos(data["generos"])
        album.set_canciones(data["canciones"])
        #album.set_visitas(0) # La cantidad de visitas no se puede editar.
        album.set_portada(data["portada"])
        album.set_precio(data["precio"])

        # Actualizamos el album en la base de datos
        if model.update_album(album):
            print(PCTRL, "Album", album_id, "updated in database")
            return {"success": True, "message": "Album updated successfully"}
        else:
            print(PCTRL_WARN, "Album", album_id, "not updated in database!")
            return {"success": False, "error": "Album not updated in database"}
    
    except Exception as e:
        print(PCTRL_WARN, "Error while processing Album", album_id, ", updating to database failed!")
        return {"success": False, "error": "Album not updated in database"}





# ------------------------------------------------------------------ #
# ----------------------------- INCLUDES --------------------------- #
# ------------------------------------------------------------------ #

@app.get("/header")
def header(request: Request):
    res = handleAndGetUserDictDBData(request)
    if isinstance(res, Response):
        return view.get_header_view(request, None) # Si es un Response, devolvemos la vista de guest
    
    return view.get_header_view(request, res)  # Si es un dict, pasamos los datos del usuario

# -------------------------------------------------------------------------- #
# --------------------------- MÉTODOS AUXILIARES --------------------------- #
# -------------------------------------------------------------------------- #

def isUserSessionValid(session_id : str) -> bool:
    return session_id and session_id in sessions and model.get_usuario(sessions[session_id]["user_id"])

# Un session contiene un name, user_id y el tipo de login (google o credentials)
def getSessionData(session_id: str) -> str:
    if session_id in sessions:
        return sessions[session_id]
    return None

# Este método automatiza la obtención de datos del usuario a partir de la sesión activa.
# Conveniente para rutas sencillas que solo requieran la info del usuario.
# Si todo es correcto -> Devuelve user_info (dict)
# Si no -> Devuelve un Response y escribe a consola
def handleAndGetUserDictDBData(request : Request):
    # Comprobamos si el usuario tiene una sesión activa
    session_id = request.cookies.get("session_id")
    if not isUserSessionValid(session_id):
        return Response("No autorizado", status_code=401)
    
    # Accedemos a los datos de la sesión del usuario
    session_data = getSessionData(session_id)
    if session_data:
        user_id = session_data["user_id"]
        user_name = session_data["name"]
        print(PCTRL, "User", user_name, "requested access to user data")

        # Accedemos a los datos del usuario en la base de datos
        user_info = model.get_usuario(user_id)

        if user_info:
            return user_info
        else:
            print(PCTRL_WARN, "User", user_name, "with id", user_id, "not found in database!")
        
    return Response("No autorizado", status_code=401)

# ------------------------------------------------------------- #
# --------------------------- About --------------------------- #
# ------------------------------------------------------------- #

@app.get("/about" , description="Muestra información sobre Undersounds")
def about(request: Request):
    return view.get_about_view(request)

# ------------------------------------------------------------ #
# --------------------------- FAQS --------------------------- #
# ------------------------------------------------------------ #

@app.get("/faqs", description="Muestra preguntas frecuentes desde MongoDB")
def get_faqs(request: Request):
    faqs_json = model.get_faqs()
    return view.get_faqs_view(request, faqs_json)

# ------------------------------------------------------------------ #
# ----------------------------- Carrito ---------------------------- #
# ------------------------------------------------------------------ #

@app.api_route("/cart", methods=["GET", "POST"], description="Muestra los artículos de tu cesta")
async def get_carrito(request: Request):
    
    # Así se obtendría el usuario, por motivos de prueba, se probará un usuario fijo
    session_id = request.cookies.get("session_id")
    session_data = getSessionData(session_id)
    user_id = (session_data["user_id"])
    form_data = await request.form()
    action = form_data.get("action")  # Por defecto: añadir
    item_id = form_data.get("item_id")
    
    if request.method == "POST":

        if action == "decrement":
            if not item_id:
                return "Falta el ID del artículo para decrementarlo/eliminarlo", 400 
            # Eliminar el artículo del carrito
            model.carrito.decrementar_articulo_existente(user_id, item_id)
        
        elif action == "add":
            
            articulo = ArticuloCestaDTO()
            articulo.set_id(form_data.get("item_id"))
            articulo.set_nombre(form_data.get("item_name"))
            articulo.set_precio(form_data.get("item_precio"))
            articulo.set_descripcion(form_data.get("item_desc"))
            articulo.set_artista(form_data.get("artist_name"))
            articulo.set_cantidad(1)
            articulo.set_imagen(form_data.get("item_image"))

            # Añadir el artículo al carrito
            model.carrito.upsert_articulo_en_carrito(user_id, articulo)

    # Si la petición es GET, mostrar el carrito
    carrito_json = model.get_carrito(user_id) 
    return view.get_carrito_view(request, carrito_json)

# ------------------------------------------------------------ #
# --------------------------- Contact ------------------------ #
# ------------------------------------------------------------ #

@app.get("/contact", description="Muestra el formulario de contacto")
def index(request: Request, success: int = 0): 
    # success = -1 --> Error al enviar el mensaje
    # success = 0 --> No hay que renderizar nada
    # success = 1 --> Mensaje enviado correctamente
    return view.get_contact_view(request, success)

# Responde al endpoint API /api/contact/send
@app.post("/api/contact/send")
async def index(request: Request):
    form_data = await request.form()
    
    # Validar que los campos requeridos no estén vacíos
    if not form_data.get("name") or not form_data.get("email") or not form_data.get("telf") or not form_data.get("msg") or not form_data.get("terms"):
        return JSONResponse(
            content={"status": "error", "message": "Formulario inválido"},
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
    
    # Llamar a la función del modelo para guardar el reporte en la base de datos
    success = model.save_contact_msg(
        name=form_data.get("name"),
        email=form_data.get("email"),
        telf=form_data.get("telf"),
        msg=form_data.get("msg")
    )
    
    # Devolver la respuesta al cliente
    if success:
        return JSONResponse(
            content={"status": "ok", "message": "Mensaje enviado correctamente"},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    else:
        return JSONResponse(
            content={"status": "error", "message": "Error al enviar el mensaje"},
            status_code=500,
            headers={"Content-Type": "application/json"}
        )