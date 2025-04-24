# Imports estándar de Python
import base64
import json
import uuid
from datetime import datetime
from pathlib import Path

# Imports de terceros
import firebase_admin
import requests
from fastapi import FastAPI, Request, Response, Form, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from firebase_admin import auth, credentials

# Imports locales del proyecto
from model.dto.albumDTO import AlbumDTO
from model.dto.carritoDTO import ArticuloCestaDTO, CarritoDTO
from model.dto.songDTO import SongDTO
from model.dto.contactoDTO import ContactoDTO
from model.dto.usuarioDTO import UsuarioDTO
from model.dto.reseñasDTO import ReseñaDTO
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

# Inicialización de la vista y del modelo
view = View()
model = Model()

listSongs = {}

# Almacenamiento en memoria para sesiones
sessions = {}


# ===============================================================================
# =========================== DEFINICIÓN DE RUTAS ===============================
# ===============================================================================

# ------------------------------------------------------------------ #
# ----------------------------- INDEX ------------------------------ #
# ------------------------------------------------------------------ #

# Ruta para cargar la vista index
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
        decoded_token = auth.verify_id_token(token, None, False, 3)
        # Identificador único del usuario otorgado por Firebase que podemos usar como identificador del usuario en nuestra base de datos
        user_id = decoded_token["uid"]
        user_email = decoded_token["email"]
        print(PCTRL, "User login:")
        print(PCTRL, "\tUser email: ", user_email)
        print(PCTRL, "\tUser user_id: ", user_id)
        print(PCTRL, "\tUser provider: ", provider)

        #Comprobar que el usuario existe en la base de datos
        usuario_db = model.get_usuario(user_id)

        if not usuario_db:
            # Eliminar al usuario de Firebase Auth
            auth.delete_user(user_id)
            print(PCTRL_WARN, "User is logged into Firebase, but not registered in database! Logon failed")
            return {"success": False, "error": "User is not registered in database"}

        # Verificar si el email ha cambiado en Firebase
        if usuario_db["email"] != user_email:
            print(PCTRL, "Firebase email and MongoDB email differ. Updating MongoDB...")
            usuario_dto = UsuarioDTO()
            usuario_dto.load_from_dict(usuario_db)
            usuario_dto.set_email(user_email)
            success = model.update_usuario(usuario_dto)
            print(PCTRL, "Email updated in MongoDB" if success else f"{PCTRL_WARN} Failed to update email in MongoDB")


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
        decoded_token = auth.verify_id_token(token, None, False, 3)
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
            user.set_imagen("/static/img/utils/default_user.jpeg")  # Imagen por defecto para usuarios registrados con credenciales clásicas
        else:
            # Descargar la imagen de Google, la convierte a base64 y la guarda en el campo imagen del usuario
            user.set_imagen("data:image/jpeg;base64," + base64.b64encode(requests.get(decoded_token["picture"]).content).decode("utf-8"))

        user.set_url("")
        user.set_esArtista(bool(data.get("esArtista", False)))
        user.set_studio_albumes([])  # Inicializamos el campo studio_albumes como una lista vacía
        user.set_studio_canciones([])  # Inicializamos el campo studio_canciones como una lista vacía
        user.set_biblioteca([])  # Inicializamos el campo biblioteca como una lista vacía

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

        print(PCTRL, "User account deleted successfully")
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
        return res  # Error: usuario no autorizado

    # res es un dict con los datos del usuario, incluyendo 'biblioteca'
    biblioteca_ids = res.get("biblioteca", [])

    # Obtener las canciones completas a partir de los IDs
    biblioteca_completa = []
    for song_id in biblioteca_ids:
        cancion = model.get_song(song_id)
        if cancion:
            biblioteca_completa.append(cancion)

    # Obtener listas de reproducción con canciones completas
    listas_completas = []
    for lista in res.get("listas_reproduccion", []):
        canciones_de_lista = []
        for song_id in lista.get("canciones", []):
            cancion = model.get_song(song_id)
            if cancion:
                canciones_de_lista.append(cancion)
        listas_completas.append({
            "nombre": lista.get("nombre", "Sin nombre"),
            "songs": canciones_de_lista
        })

    # Pasar también las canciones al renderizado de la vista
    return view.get_perfil_view(request, res, biblioteca_completa, listas_completas)

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
    
@app.post("/crear-lista")
async def crear_lista(request: Request, nombre_lista: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.add_lista_usuario(res["id"], nombre_lista)
    return RedirectResponse("/profile", status_code=302)

@app.post("/remove-lista")
async def remove_lista(request: Request, nombre_lista: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.remove_lista_usuario(res["id"], nombre_lista)
    return RedirectResponse("/profile", status_code=302)

@app.post("/add-song-to-list")
async def add_song_to_list(request: Request, nombre_lista: str = Form(...), id_cancion: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.add_cancion_a_lista_usuario(res["id"], nombre_lista, id_cancion)
    return RedirectResponse("/profile", status_code=302)

@app.post("/remove-song-from-list")
async def remove_song_from_list(request: Request, nombre_lista: str = Form(...), id_cancion: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.remove_cancion_de_lista_usuario(res["id"], nombre_lista, id_cancion)
    return RedirectResponse("/profile", status_code=302)

# ------------------------------------------------------------------- #
# ----------------------------- ALBUM ------------------------------- #
# ------------------------------------------------------------------- #

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
async def upload_album_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return {"success": False, "error": "No autorizado"}  # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return {"success": False, "error": "No autorizado"}
    
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
    album.set_likes(0)
    album.set_visible(data["visible"])

    # Subir el album a la base de datos
    album_id = model.add_album(album)
    if album_id is not None:
        print(PCTRL, "Album", album_id, "uploaded to database")
    else:
        print(PCTRL_WARN, "Album", album_id, "not uploaded to database!")
        return {"success": False, "error": "Error del sistema"}

    try:
        # Por cada una de las canciones en el album, actualizamos su campo album con el id del nuevo album
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Song", song_id, "not found in database")
                raise Exception(f"Song {song_id} not found in database")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Song", song_id, "not updated in database!")
                raise Exception(f"Song {song_id} not updated in database!")

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
        print(PCTRL_WARN, "Error:", str(e))

        # Intentar destruir el album subido
        model.delete_album(album_id)
        print(PCTRL_WARN, "Album", album_id, "deleted from database")

        # Intentar revertir los cambios en las canciones
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Song", song_id, "not found in database")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Song", song_id, "not updated in database!")

        # Intentar revertir los cambios en el usuario
        user = UsuarioDTO()
        user.load_from_dict(res)
        # Eliminar la referencia al album
        user.remove_studio_album(album_id)
        # Actualizar el usuario en la base de datos
        if model.update_usuario(user):
            print(PCTRL, "User", user.get_email(), "updated in database")
        else:
            print(PCTRL_WARN, "User", user.get_email(), "not updated in database!")
            
        return {"success": False, "error": "Error del sistema"}

# Ruta para cargar la vista de album
@app.get("/album")
async def get_album(request: Request):
    #Leemos de la request el id del album y recogemos el album de la BD
    if request.query_params.get("id") is not None:
        album_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        album_id = data["id"]

    # TODO: Album no tiene un parametro visible?? Esto podría dar problemas en el futuro cuando songs contemple la posibilidad de ser visible o no.

    # Descargamos el album de la base de datos via su ID.
    album_info = model.get_album(album_id)
    if not album_info:
        print(PCTRL_WARN, "Album does not exist")
        return Response("No autorizado", status_code=403)
    
    # Descargamos las canciones del album de la base de datos via su ID en el campo canciones y las insertamos en este album_info
    canciones_out : list[dict] = []
    for cancion_id in album_info["canciones"]:
        cancion = model.get_song(cancion_id)
        if not cancion:
            print(PCTRL_WARN, "Cancion", cancion_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        
        # Convertimos los generos de cada canción a un string sencillo
        # Primero, descargamos todos los generos, escogemos su nombre, lo añadimos al string, y luego lo metemos en cancion["generosStr"]
        # Esto se hace por cada canción del album.
        generosStr = ""
        for genero_id in cancion["generos"]:
            genero = model.get_genero(genero_id)
            if not genero:
                print(PCTRL_WARN, "Genero", genero_id ,"not found in database")
                return Response("Error del sistema", status_code=403)
            generosStr += genero["nombre"] + ", "
        generosStr = generosStr[:-2] # Quitamos la última coma y espacio
        cancion["generosStr"] = generosStr # Añadimos el string a la canción

        canciones_out.append(cancion)

    album_info["canciones"] = canciones_out


    # Convertimos los generos del album a un string sencillo
    # Primero, descargamos todos los generos, escogemos su nombre, lo añadimos al string, y luego lo metemos en album_info["generosStr"]
    generosStr = ""
    for genero_id in album_info["generos"]:
        genero = model.get_genero(genero_id)
        if not genero:
            print(PCTRL_WARN, "Genero", genero_id ,"not found in database")
            return Response("Error del sistema", status_code=403)
        generosStr += genero["nombre"] + ", "
    generosStr = generosStr[:-2] # Quitamos la última coma y espacio
    album_info["generosStr"] = generosStr # Añadimos el string a la canción


    # Recuperamos al usuario actualmente logeado y comprobamos si es el autor del album
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        tipoUsuario = 0 # Guest
    else:
        if album_id in res["studio_albumes"]:
            tipoUsuario = 3 # Artista (creador)

        elif all(song["id"] in res["biblioteca"] for song in album_info["canciones"]):
            tipoUsuario = 2 # Propietario (User o Artista)

        else:
            tipoUsuario = 1

    # Donde tipo Usuario:
    # 0 = Guest
    # 1 = User
    # 2 = Propietario (User o Artista)
    # 3 = Artista (creador)
    return view.get_album_view(request, album_info, tipoUsuario) # Devolvemos la vista del album

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
async def album_edit_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return {"success": False, "error": "No autorizado"}  # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return {"success": False, "error": "No autorizado"}
    
    # Recibimos los datos del nuevo album editado, junto con su ID.
    data = await request.json()
    album_id = data["id"]  # ID del album a editar
    if not album_id:
        print(PCTRL_WARN, "Album ID not provided in request")
        return {"success": False, "error": "Album ID not provided"}

    # Descargamos el album antiguo de la base de datos via su ID.
    album_dict = model.get_album(album_id)
    if not album_dict:
        print(PCTRL_WARN, "Album does not exist")
        return {"success": False, "error": "Album does not exist"}
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "Album not found in user albums")
        return {"success": False, "error": "Album not found in user albums"}

    try:
        album = AlbumDTO()
        album.load_from_dict(album_dict)

        # Editamos el album con los nuevos datos recibidos en la request
        album.set_titulo(data["titulo"])
        album.set_autor(data["autor"])
        album.set_colaboradores(data["colaboradores"])
        album.set_descripcion(data["descripcion"])
        # album.set_fecha(datetime.strptime(data["fecha"], "%Y-%m-%d")) # La fecha no se puede editar.
        album.set_generos(data["generos"])
        album.set_canciones(data["canciones"])
        # album.set_visitas() # La cantidad de visitas no se puede editar.
        album.set_portada(data["portada"])
        album.set_precio(data["precio"])
        # album.set_likes() # La cantidad de likes no se puede editar.
        album.set_visible(data["visible"])
        
        # Por cada una de las canciones en el album, actualizamos su campo album con el id del nuevo album
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Song", song_id, "not found in database")
                raise Exception(f"Song {song_id} not found in database")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Song", song_id, "not updated in database!")
                raise Exception(f"Song {song_id} not updated in database!")

        # Actualizamos el album en la base de datos
        if model.update_album(album):
            print(PCTRL, "Album", album_id, "updated in database")
            return {"success": True, "message": "Album updated successfully"}
        else:
            raise Exception(f"Album {album_id} not updated in database!")
    
    except Exception as e:

        # Intentamos revertir los cambios en el album
        album_object = AlbumDTO()
        album_object.load_from_dict(album_dict)
        if model.update_album(album_object):
            print(PCTRL, "Album", album_id, "reverted in database")
        else:
            print(PCTRL_WARN, "Album", album_id, "not reverted in database!")

        # Intentar revertir los cambios en las canciones
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Song", song_id, "not found in database")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(None)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Song", song_id, "not updated in database!")

        # Intentamos asociar las canciones del album antiguo a su album original
        for song_id in album_dict["canciones"]:
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Song", song_id, "not found in database")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Song", song_id, "not updated in database!")

        print(PCTRL_WARN, "Error while processing Album", album_id, ", updating to database failed!")
        return {"success": False, "error": "Error del sistema"}

# Ruta para eliminar un álbum
@app.post("/delete-album")
async def delete_album_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return {"success": False, "error": "No autorizado"}
    if not res["esArtista"]:
        return {"success": False, "error": "No autorizado"}
    
    # Obtenemos el ID del álbum a eliminar desde la request
    data = await request.json()
    album_id = data.get("id")
    if not album_id:
        print(PCTRL_WARN, "Album ID not provided in request")
        return {"success": False, "error": "Album ID not provided"}
    
    # Verificamos que el álbum existe y pertenece al usuario
    album = model.get_album(album_id)
    if not album:
        print(PCTRL_WARN, "Album does not exist")
        return {"success": False, "error": "Album does not exist"}
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "Album not found in user albums")
        return {"success": False, "error": "Album not found in user albums"}
    
    # Procedemos a la eliminación del álbum
    # Primero, borramos el campo album de cada una de las canciones que lo componen. Si algo falla, nos da igual.
    for song_id in album["canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "Song", song_id, "not found in database - skipping")
            continue
        
        # Actualizamos el campo album de la canción con el id del nuevo album
        song_object = SongDTO()
        song_object.load_from_dict(song)
        song_object.set_album(None)
        if not model.update_song(song_object):
            print(PCTRL_WARN, "Song", song_id, "not updated in database! - skipping")
            continue

    # Luego, borramos el álbum del studio_albumes del usuario
    user = UsuarioDTO()
    user.load_from_dict(res)
    user.remove_studio_album(album_id)
    if not model.update_usuario(user):
        print(PCTRL_WARN, "User", user.get_email(), "not updated in database!")
        return {"success": False, "error": "User not updated in database"}
    
    # Por ultimo, borramos el álbum de la base de datos
    if model.delete_album(album_id):
        print(PCTRL, "Album", album_id, "deleted from database")
        return {"success": True, "message": "Album deleted successfully"}
    else:
        print(PCTRL_WARN, "Album", album_id, "not deleted from database!")
        return {"success": False, "error": "Album not deleted from database"}
        

# ------------------------------------------------------------------ #
# ----------------------------- INCLUDES --------------------------- #
# ------------------------------------------------------------------ #

@app.get("/header")
def header(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return view.get_header_view(request, None) # Si es un Response, devolvemos la vista de guest
    
    return view.get_header_view(request, res)  # Si es un dict, pasamos los datos del usuario

@app.get("/footer")
def footer(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return view.get_footer_view(request, None)
    
    return view.get_footer_view(request, res)  # Si es un dict, pasamos los datos del usuario

# ------------------------------------------------------------- #
# --------------------------- ABOUT --------------------------- #
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
# ----------------------------- CARRITO ---------------------------- #
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


# ------------------------------------------------------------------ #
# ----------------------------- PREPAID ---------------------------- #
# ------------------------------------------------------------------ #

@app.get("/prepaid")
def get_prepaid(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    carrito_json = model.get_carrito(res["id"]) 
    tarjeta_json = model.get_tarjeta(res["id"])

    return view.get_contact_view(request, carrito_json, tarjeta_json)


@app.post("/prepaid")
def get_prepaid(request: Request):
    pass


# ------------------------------------------------------------ #
# --------------------------- CONTACT ------------------------ #
# ------------------------------------------------------------ #

@app.get("/contact")
def get_contact(request: Request): 
    return view.get_contact_view(request)

# Responde al endpoint API /contact
@app.post("/contact")
async def contact_post(request: Request):
    # Obtenemos los datos de la query en formato JSON
    data = await request.json()
    
    # Validar que los campos requeridos no estén vacíos
    if not data.get("name") or not data.get("email") or not data.get("telf") or not data.get("msg"):
        return JSONResponse(
            content={"status": "error", "message": "Formulario inválido"},
            status_code=400,
            headers={"Content-Type": "application/json"}
        )
    
    # Crear objeto ContactoDTO y asignar los valores del formulario
    contacto = ContactoDTO()
    contacto.set_nombre(data.get("name"))
    contacto.set_email(data.get("email"))
    contacto.set_telefono(data.get("telf"))
    contacto.set_mensaje(data.get("msg"))
    
    # Llamar a la función del modelo para guardar el reporte en la base de datos y devolver respuesta
    if model.add_contacto(contacto):
        return JSONResponse(
            content={"status": "success", "message": "Formulario enviado correctamente"},
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
    else:
        return JSONResponse(
            content={"status": "error", "message": "Error al enviar el formulario"},
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
    
# ------------------------------------------------------------ #
# ---------------------------- SONG -------------------------- #
# ------------------------------------------------------------ #

# Ruta para cargar vista upload-song
@app.get("/upload-song")
def get_upload_song(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
    return view.get_upload_song_view(request)

# Ruta para procesar la petición de upload-song
@app.post("/upload-song")
async def upload_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
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
    song.set_visible(data["visible"])
    song.set_album(None) # El album se asigna posteriormente en el editor de albumes

    try:
        song_id = model.add_song(song)

        if song_id is not None:
            print(PCTRL, "Song registered in database")
        else:
            print(PCTRL_WARN, "Song registration failed in database!")
            return {"success": False, "error": "Song registration failed"}

        # Convertirmos res en un objeto UsuarioDTO, le añadimos la nueva canción a studio_canciones y lo actualizamos en la base de datos
        user = UsuarioDTO()
        user.load_from_dict(res)
        user.add_studio_cancion(song_id)
        if model.update_usuario(user):
            print(PCTRL, "User", user.get_email(), "updated in database")
            return {"success": True, "message": "Song added successfully"}
        else:
            print(PCTRL_WARN, "User", user.get_email(), "not updated in database!")
            raise Exception("User not updated in database")

    except Exception as e:
        print(PCTRL_WARN, "Error while processing Song", song_id, ", adding to database failed!")
        # Eliminar la canción subida (intentar tanto si se ha subido como si no)
        model.delete_song(song_id)
        return {"success": False, "error": "Song not added to database"}

# Ruta para cargar vista song
@app.get("/song")
async def get_song(request: Request):

    user_db = verifySessionAndGetUserInfo(request)
    if isinstance(user_db, Response):
        return user_db
    
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
    
    # Antes de hacer nada, comprobamos si la canción es visible o no. Si no es visible, solo el artista creador puede verla.
    res = verifySessionAndGetUserInfo(request)
    if not song_info["visible"]:
        if isinstance(res, Response) or song_id not in res["studio_canciones"]:
            print(PCTRL_WARN, "Song is not visible and user is not the creator")
            return Response("No autorizado", status_code=403)

    # Convertimos los generos de la canción a un string sencillo
    # Primero, descargamos todos los generos, escogemos su nombre, lo añadimos al string, y luego lo metemos en song_info["generosStr"]
    generosStr = ""
    for genero_id in song_info["generos"]:
        genero = model.get_genero(genero_id)
        if not genero:
            print(PCTRL_WARN, "Genero", genero_id ,"not found in database")
            return Response("Error del sistema", status_code=403)
        generosStr += genero["nombre"] + ", "
    generosStr = generosStr[:-2] # Quitamos la última coma y espacio
    song_info["generosStr"] = generosStr
    
    # Recuperamos al usuario actualmente logeado y comprobamos si es el autor de la canción
    if isinstance(res, Response):
        tipoUsuario = 0 # Guest
    else:
        if song_id in res["studio_canciones"]:
            tipoUsuario = 3 # Artista (creador)

        elif song_id in res["biblioteca"]:
            tipoUsuario = 2 # Propietario (User o Artista)

        else:
            tipoUsuario = 1

    # Donde tipo Usuario:
    # 0 = Guest
    # 1 = User
    # 2 = Propietario (User o Artista)
    # 3 = Artista (creador)

    user = UsuarioDTO()
    user.load_from_dict(user_db)

    return view.get_song_view(request, song_info, tipoUsuario, user) # Devolvemos la vista del song

# Ruta para cargar vista edit-song
@app.get("/edit-song")
async def get_edit_song(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
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
    if song_id not in res["studio_canciones"]:
        print(PCTRL_WARN, "Song not found in user songs")
        return Response("No autorizado", status_code=403)

    return view.get_edit_song_view(request, song_info)

# Ruta para procesar la petición de edit-song
@app.post("/edit-song")
async def edit_song_post(request: Request):
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
        song_id = data["id"] # ID del album a editar

        # Descargamos el album antiguo de la base de datos via su ID.
        song_dict = model.get_song(song_id)
        if not song_dict:
            print(PCTRL_WARN, "Song does not exist")
            return Response("No autorizado", status_code=403)
        if song_id not in res["studio_canciones"]:
            print(PCTRL_WARN, "Song not found in user songs")
            return Response("No autorizado", status_code=403)
    
        song = SongDTO()
        song.load_from_dict(song_dict)

        song.set_titulo(data["titulo"])
        song.set_artista(data["artista"])
        song.set_colaboradores(data["colaboradores"])
        song.set_descripcion(data["descripcion"])
        song.set_generos(data["generos"])
        song.set_portada(data["portada"])
        song.set_precio(data["precio"])
        song.set_visible(data["visible"])

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

# Ruta para eliminar una canción
@app.post("/delete-song")
async def delete_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return {"success": False, "error": "No autorizado"}
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return {"success": False, "error": "No autorizado"}
    
    # Obtenemos el ID de la canción a eliminar desde la request
    data = await request.json()
    song_id = data.get("id")
    if not song_id:
        print(PCTRL_WARN, "Song ID not provided in request")
        return {"success": False, "error": "Song ID not provided"}
    
    # Verificamos que la canción existe y pertenece al usuario
    song = model.get_song(song_id)
    if not song:
        print(PCTRL_WARN, "Song does not exist")
        return {"success": False, "error": "Song does not exist"}
    if song_id not in res["studio_canciones"]:
        print(PCTRL_WARN, "Song not found in user songs")
        return {"success": False, "error": "Song not found in user songs"}
    
    # Procedemos a la eliminación de la canción
    # Primero, descargaremos el album al que pertenece la canción, y eliminaremos la canción de su campo canciones.
    # Si no pertenece a ningun album, no haremos nada.
    if song["album"] is not None:
        album = model.get_album(song["album"])
        if not album:
            print(PCTRL_WARN, "Album does not exist")
            return {"success": False, "error": "Album does not exist"}
        album_object = AlbumDTO()
        album_object.load_from_dict(album)
        album_object.remove_cancion(song_id)
        if not model.update_album(album_object):
            print(PCTRL_WARN, "Album", album["id"], "not updated in database!")
            return {"success": False, "error": "Album not updated in database"}
    
    # Luego, borramos la canción del studio_canciones del usuario
    user = UsuarioDTO()
    user.load_from_dict(res)
    user.remove_studio_cancion(song_id)
    if not model.update_usuario(user):
        print(PCTRL_WARN, "User", user.get_email(), "not updated in database!")
        return {"success": False, "error": "User not updated in database"}

    # Por último, borramos la canción de la base de datos
    if model.delete_song(song_id):
        print(PCTRL, "Song", song_id, "deleted from database")
        return {"success": True, "message": "Song deleted successfully"}
    else:
        print(PCTRL_WARN, "Song", song_id, "not deleted from database!")
        return {"success": False, "error": "Song not deleted from database"}

# -------------------------------------------------------------- #
# ---------------------------- STUDIO -------------------------- #
# -------------------------------------------------------------- #

# Ruta para cargar la vista de studio
@app.get("/studio")
async def get_studio(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res
    if not res["esArtista"]:
        print(PCTRL_WARN, "User is not an artist")
        return Response("No autorizado", status_code=403)
    
    # Descargamos los albumes y canciones del usuario
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "Album", album_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)
    
    # Descargamos las canciones del usuario
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "Song", song_id, "not found in database")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)
    
    # Buscamos por cada canción descagada si su id está en el campo canciones de algún album.
    # Si es así, reemplazamos el campo album de esa canción por el NOMBRE del album.
    # Si no, lo introducimos en su lugar None
    for song in user_songs_objects:
        found = False
        for album in user_albums_objects:
            if song["id"] in album["canciones"]:
                song["album"] = album["titulo"]
                found = True
                print(PCTRL, "Song", song["titulo"], "found in album", album["titulo"])
                break
        if not found:
            song["album"] = None

    return view.get_studio_view(request, user_songs_objects, user_albums_objects)


# ------------------------------------------------------------ #
# --------------------------- Reseña ------------------------- #
# ------------------------------------------------------------ #

@app.post("/add-review")
async def add_review(request: Request):
    
    try:
        # Verificar si el usuario tiene una sesión activa y es artista 
        user_db = verifySessionAndGetUserInfo(request)
        if isinstance(user_db, Response):
            return user_db # Si es un Response, devolvemos el error  
        
        data_info = await request.json()
        song_id = data_info["song_id"]
        titulo = data_info["titulo"]
        texto = data_info["reseña"]

        # Crear ReseñaDTO
        reseña = ReseñaDTO()
        reseña.set_titulo(titulo)
        reseña.set_reseña(texto)
        reseña.set_usuario(user_db)

        # Guardar en base de datos
        reseña_id = model.add_reseña(reseña)
        if reseña_id:
            print(PCTRL, "Reseña registered in database")
        else:
            print(PCTRL_WARN, "No se pudo guardar la reseña.")

        reseña.set_id(reseña_id)
        
        song_dict = model.get_song(song_id)

        song = SongDTO()
        song.load_from_dict(song_dict)
        song.add_resenas(reseña.reseñadto_to_dict())

        if model.update_song(song):
            return JSONResponse(status_code=200, content={"message": "Reseña añadida correctamente."})
        else:
            return JSONResponse(status_code=500, content={"error": "No se pudo guardar la reseña."})

    except Exception as e:
        print("ERROR add_review:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})
    

@app.post("/delete-review")
async def delete_review(request: Request):
        try:
            # Verificar si el usuario tiene una sesión activa y es artista 
            user_db = verifySessionAndGetUserInfo(request)
            if isinstance(user_db, Response):
                return user_db # Si es un Response, devolvemos el error  
            
            data_info = await request.json()
            song_id = data_info["song_id"]
            reseña_id = data_info["reseña_id"]

            # Obtener la reseña
            reseña_data = model.get_reseña(reseña_id)

            if user_db != reseña_data["usuario"]:
                return JSONResponse(status_code=500, content={"error": "La reseña no te pertenece."})

            song_dict = model.get_song(song_id)
            song = SongDTO()
            song.load_from_dict(song_dict)
            song.remove_resena(reseña_data)

            if model.update_song(song):
                print(PCTRL, "Reseña deleted of song ", song_id )
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo eliminar la reseña de la cancion "})

            if model.delete_reseña(reseña_id):
                return JSONResponse(status_code=200, content={"message": "Reseña eliminada."})
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo eliminar la reseña."})

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/update-review")
async def update_review(request: Request):
        try:
            # Verificar si el usuario tiene una sesión activa y es artista 
            user_db = verifySessionAndGetUserInfo(request)
            if isinstance(user_db, Response):
                return user_db # Si es un Response, devolvemos el error  
            
            data_info = await request.json()
            song_id = data_info["song_id"]
            reseña_id = data_info["reseña_id"]
            titulo = data_info["titulo"]
            texto = data_info["reseña"]

            # Obtener la reseña
            reseña_data = model.get_reseña(reseña_id)

            if user_db != reseña_data["usuario"]:
                return JSONResponse(status_code=500, content={"error": "No se pudo eliminar la reseña."})

            song_dict = model.get_song(song_id)
            song = SongDTO()
            song.load_from_dict(song_dict)

            reseña = ReseñaDTO()
            reseña.load_from_dict(reseña_data)
            reseña.set_titulo(str(titulo))
            reseña.set_reseña(str(texto))
            song.update_resenas(reseña.reseñadto_to_dict())

            if model.update_song(song):
                print(PCTRL, "Reseña update of song", song_id )
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo actualizar la reseña."})

            if model.update_reseña(reseña):
                return JSONResponse(status_code=200, content={"message": "Reseña actualizada."})
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo actualizar la reseña."})

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


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
#
#   1º Comprueba que exista una sesión activa
#   2º Descarga los datos del usuario enlazados a esa sesión
#   3º Devuelve dos cosas:
#       Si todo es correcto -> Devuelve user_info (dict)
#       Si no -> Devuelve un Response con el error y escribe a consola
#
# Conveniente para rutas sencillas que solo requieran la info del usuario.
def verifySessionAndGetUserInfo(request : Request):
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
        user_info = model.get_usuario(user_id) # Devuelve un dict del UsuarioDTO

        if user_info:
            return user_info
        else:
            print(PCTRL_WARN, "User", user_name, "with id", user_id, "not found in database!")
        
    return Response("No autorizado", status_code=401)




# --------------------------- HACKS DE MIERDA - ELIMINAR CUANDO HAYA UNA MEJOR IMPLEMENTACIÓN --------------------------- #
# Guardar sesiones en un archivo JSON al cerrar el servidor y recuperarlas al iniciar.
# Así evitamos perder las sesiones al reiniciar el servidor.
@app.on_event("shutdown")
def shutdown_event():
    with open("sessions.json", "w") as f:
        json.dump(sessions, f)
    print(PCTRL, "Sessions saved to sessions.json")
@app.on_event("startup")
def startup_event():
    if Path("sessions.json").is_file():
        with open("sessions.json", "r") as f:
            global sessions
            sessions = json.load(f)
        print(PCTRL, "Sessions loaded from sessions.json")
    else:
        print(PCTRL_WARN, "No sessions.json file found, starting with empty sessions")


    

