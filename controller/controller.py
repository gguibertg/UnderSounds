# Imports estándar de Python
import os
import base64
from datetime import datetime, timedelta
from pathlib import Path
import os

# Imports de terceros
import firebase_admin
import requests
from fastapi import FastAPI, Request, Response, Form, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from firebase_admin import auth, credentials
from datetime import datetime

# Imports locales del proyecto
from model.dto.albumDTO import AlbumDTO
from model.dto.carritoDTO import ArticuloCestaDTO, CarritoDTO
from model.dto.sesionDTO import SesionDTO
from model.dto.songDTO import SongDTO
from model.dto.contactoDTO import ContactoDTO
from model.dto.usuarioDTO import UsuarioDTO, UsuariosDTO
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
    print("\033[91mERROR: No se encuentra el archivo credentials.jsond!\033[0m")
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

# Almacenamiento caché en memoria para sesiones
sessions : dict[dict] = {}

# Descargamos todas las sesiones de la base de datos al inicio y las guardamos en la caché en memoria,
# descartando aquellas que estén caducadas por el camino y también eliminandolas de la base de datos.
# Esto invalida la necesidad de tener que comprobar en el método auxiliar verifySessionAndGetUserInfo(request)
# si hay una sesión en mongo que poder descargar. Aún así, lo mantenemos por si acaso queremos quitar el descargar todo de la base de datos al inicio.
for sesion in model.get_all_sesiones():
    if sesion["caducidad"] < datetime.now():
        # Si ha caducado, la eliminamos de la base de datos y de la caché en memoria
        model.delete_sesion(sesion["id"])
        print(PCTRL, "La sesión", sesion["id"], "ha caducado y ha sido eliminada de la base de datos")
    else:
        # Si no ha caducado, la añadimos a la caché en memoria
        sessions[sesion["id"]] = sesion

# ===============================================================================
# =========================== DEFINICIÓN DE RUTAS ===============================
# ===============================================================================

# ------------------------------------------------------------------ #
# ----------------------------- INDEX ------------------------------ #
# ------------------------------------------------------------------ #

# Ruta para cargar la vista indexº
@app.get("/")
async def index(request: Request): 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        tipoUsuario = False # Guest
    else:
       tipoUsuario = True # Miembro (User)

    genres_json = model.get_generos()
    song_json = model.get_songs()
    artistas_json = model.get_artistas()
    albums_json = model.get_albums()
    return view.get_index_view(request, song_json, genres_json, artistas_json, albums_json, tipoUsuario)

# Endpoint para obtener listado de canciones por genero
@app.get("/songs/genre")
async def get_song_list_by_genre(request: Request):
    genre_id = request.query_params.get("id")
    
    if not genre_id:
        return JSONResponse(content={"error": "Falta el parámetro 'id'"}, status_code=400)

    try:
        canciones = model.get_songs_by_genre(genre_id)

        # 🔥 Aquí conviertes todos los datetime a strings
        canciones = convert_datetime(canciones)

        if canciones:
            print(PCTRL, "Canciones filtradas por el género: ", genre_id)
            return JSONResponse(content=canciones, status_code=200)
        else:
            print(PCTRL_WARN, "No existen canciones para ese género")
            return JSONResponse(content=[], status_code=200)
    except Exception as e:
        print(PCTRL_WARN, "Error al obtener canciones:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ------------------------------------------------------------------ #
# ----------------------------- LOGIN ------------------------------ #
# ------------------------------------------------------------------ #

# Ruta para cargar vista login
@app.get("/login")
def login(request: Request):
    return view.get_login_view(request)

# Ruta para procesar la petición de login
@app.post("/login")
async def login_post(data: dict, request : Request, provider: str):
    token = data.get("token")
    try:
        # Si el usuario está logeado, es decir, tiene un cookie de sesión válido + sesión en el backend, entonces no debería poder logearse de nuevo (¡la anterior sesión se quedaría fantasma!).
        # Sin embargo, si la sesión en el backend ha caducado (o no existe), entonces el usuario debería poder logearse de nuevo.
        # Verificamos si el usuario tiene una sesión activa y existe en la base de datos.
        res = verifySessionAndGetUserInfo(request)
        if not isinstance(res, Response):
            # Si el usuario tiene una sesión activa, échalo.
            return JSONResponse(content={"error": "El usuario ya tiene una sesión activa válida"}, status_code=400)
        # Llegados a este punto, o el usuario no tiene una sesión activa, o la sesión ha caducado (o no existe en el backend)
        # y verifySessionAndGetUserInfo() se ha encargado de eliminarla de la caché en memoria y de la base de datos.
        # Así entonces, podemos crear sin preocupaciones otro cookie y SesionDTO sin miedo a llenar la base de datos de sesiones basura.

        # Verificamos el token de Firebase dado por el usuario
        decoded_token = auth.verify_id_token(token, None, False, 3)
        # Identificador único del usuario otorgado por Firebase que podemos usar como identificador del usuario en nuestra base de datos
        user_id = decoded_token["uid"]
        user_email = decoded_token["email"]
        print(PCTRL, "User login:")
        print(PCTRL, "\tUser email: ", user_email)
        print(PCTRL, "\tUser user_id: ", user_id)
        print(PCTRL, "\tUser provider: ", provider)

        # Comprobar que el usuario existe en la base de datos
        usuario_db = model.get_usuario(user_id)

        if not usuario_db:
            # Eliminar al usuario de Firebase Auth
            auth.delete_user(user_id)
            print(PCTRL_WARN, "El usuario inició sesión en Firebase, pero no está registrado en la base de datos. Error al iniciar sesión.")
            return JSONResponse(content={"error": "El usuario no está registrado en la base de datos"}, status_code=400)

        # Verificar si el email ha cambiado en Firebase
        if usuario_db["email"] != user_email:
            print(PCTRL, "El correo electrónico de Firebase y el de MongoDB son diferentes. Actualizando MongoDB...")
            usuario_dto = UsuarioDTO()
            usuario_dto.load_from_dict(usuario_db)
            usuario_dto.set_email(user_email)
            success = model.update_usuario(usuario_dto)
            print(PCTRL, "Email actualizado en MongoDB" if success else f"{PCTRL_WARN} Fallo al actualizar el email en MongoDB")

        # Creamos una sesión para el usuario y la subimos a la base de datos
        session_obj = SesionDTO()
        session_obj.set_name(user_email)
        session_obj.set_user_id(user_id)
        session_obj.set_type(provider)
        delta = timedelta(hours=12) # Hoy + 12 horas
        session_obj.set_caducidad(datetime.now() + delta)
        session_id = model.add_sesion(session_obj)
        if session_id is None:
            print(PCTRL_WARN, "Error al crear la sesión en la base de datos")
            return JSONResponse(content={"error": "Error al crear la sesión"}, status_code=500)
        # Añadimos la sesión a la caché en memoria
        sessions[session_id] = session_obj.to_dict()

        # Creamos una instancia de JSONResponse
        resp = JSONResponse(content={"success": True}, status_code=200)
        # Le añadimos la cookie
        resp.set_cookie(key="session_id", value=session_id, httponly=True, max_age=delta.total_seconds())
        print(PCTRL, "Inicio de sesión exitoso para", user_email)
        return resp

    except Exception as e:
        print(PCTRL_WARN, "El inicio de sesión falló debido a:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para procesar la petición de login con credenciales clásicas
@app.post("/login-credentials")
async def login_credentials(data: dict, request: Request):
    return await login_post(data, request, "credentials")

# Ruta para procesar la petición de login con credenciales de Google
@app.post("/login-google")
async def login_google(data: dict, request: Request):
    return await login_post(data, request, "google")

# Ruta para procesar la petición de logout
@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    print(PCTRL, "La sesión de usuario", session_id, "se está cerrando")
    # Eliminar de la base de datos
    if not model.delete_sesion(session_id):
        print(PCTRL_WARN, "Error al eliminar la sesión de la base de datos - omitiendo")
    # Eliminar de la caché en memoria 
    if session_id in sessions:
        del sessions[session_id]

    # Creamos una instancia de JSONResponse
    resp = JSONResponse(content={"success": True}, status_code=200)
    # Le eliminamos la cookie
    resp.delete_cookie("session_id")
    print(PCTRL, "La sesión del usuario", session_id, "ha sido destruida")
    return resp

# Hack para que el header pueda acceder al script de logout correctamente
@app.get("/logout")
async def get_logout(request: Request):
    # Verificar si el usuario tiene una sesión activa y el usuario existe
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res   
    return view.get_logout_view(request)


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

        # Registrar usuario en la base de datos
        # Verificar si el usuario ya está registrado en la base de datos
        if model.get_usuario(user_id):
            print(PCTRL, "El usuario ya está registrado en la base de datos")
            return JSONResponse(content={"error": "Usuario ya registrado"}, status_code=400)

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
        user.set_fechaIngreso(datetime.now())  # Fecha de creación del usuario
        user.set_esVisible(True)  # Por defecto, el usuario es visible
        user.set_emailVisible(False) # Por defecto, el email no es visible
        user.set_studio_albumes([])  # Inicializamos el campo studio_albumes como una lista vacía
        user.set_studio_canciones([])  # Inicializamos el campo studio_canciones como una lista vacía
        user.set_id_likes([])  # Inicializamos el campo id_likes como una lista vacía
        user.set_biblioteca([])  # Inicializamos el campo biblioteca como una lista vacía

        # Añadir el usuario a la base de datos
        if model.add_usuario(user):
            print(PCTRL, "El usuario ya está registrado en la base de datos")
        else:
            print(PCTRL_WARN, "¡Error en el registro del usuario en la base de datos!")
            return JSONResponse(content={"error": "Error en el registro del usuario"}, status_code=500)
        
        # Creamos una sesión para el usuario y la subimos a la base de datos
        session_obj = SesionDTO()
        session_obj.set_name(user_email)
        session_obj.set_user_id(user_id)
        session_obj.set_type(provider)
        delta = timedelta(hours=12) # Hoy + 12 horas
        session_obj.set_caducidad(datetime.now() + delta)
        session_id = model.add_sesion(session_obj)
        if session_id is None:
            print(PCTRL_WARN, "Error al crear la sesión en la base de datos")
            return JSONResponse(content={"error": "Error al crear la sesión"}, status_code=500)
        # Añadimos la sesión a la caché en memoria
        sessions[session_id] = session_obj.to_dict()

        # Creamos una instancia de JSONResponse
        resp = JSONResponse(content={"success": True}, status_code=200)
        # Le añadimos la cookie
        resp.set_cookie(key="session_id", value=session_id, httponly=True, expires=delta.total_seconds())
        print(PCTRL, "Registro (e inicio de sesión) exitoso para", user_email)
        return resp
        
    except Exception as e:
        print(PCTRL_WARN, "El registro del usuario falló debido a:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)  # Si es un Response, devolvemos el error  

    print(PCTRL, "El usuario", res["email"], "solicitó la eliminación de la cuenta") 

    try:
        # Eliminar al usuario de Firebase Auth
        auth.delete_user(res["id"])
        print(PCTRL, "El usuario", res["email"], "eliminado de Firebase Auth")

        # Eliminar cada una de las canciones en studio_canciones de la base de datos
        for song_id in res["studio_canciones"]:
            if model.delete_song(song_id):
                print(PCTRL, "La cancion", song_id, "borrada de la base de datos")
            else:
                print(PCTRL_WARN, "La cancion", song_id, "no ha sido borrada de la base de datos! - skipping")
        
        # Eliminar cada uno de los albumes en studio_albumes de la base de datos
        for album_id in res["studio_albumes"]:
            if model.delete_album(album_id):
                print(PCTRL, "El álbum", album_id, "borrado de la base de datos")
            else:
                print(PCTRL_WARN, "El álbum", album_id, "no ha sido borrado de la base de datos! - skipping")

        # Eliminar al usuario de la base de datos
        if model.delete_usuario(res["id"]):
            print(PCTRL, "El usuario con email:", res["email"], "borrado de la base de datos")
        else:
            print(PCTRL_WARN, "El usuario con email:", res["email"], "no ha sido borrado de la base de datos! - skipping")

        # Eliminar la sesión del usuario
        session_id = request.cookies.get("session_id")
        # Eliminar de la base de datos
        if not model.delete_sesion(session_id):
            print(PCTRL_WARN, "Error al eliminar la sesión de la base de datos - omitiendo")
        # Eliminar de la caché en memoria 
        if session_id in sessions:
            del sessions[session_id]
        # Creamos una instancia de JSONResponse
        resp = JSONResponse(content={"success": True, "message": "La cuenta del usuario fue eliminada exitosamente"}, status_code=200)
        # Le eliminamos la cookie
        resp.delete_cookie("session_id")
        print(PCTRL, "La sesión del usuario", session_id, "ha sido destruida")

        print(PCTRL, "La cuenta del usuario fue eliminada exitosamente")
        return resp
    
    except Exception as e:
        print(PCTRL, "Error deleting user:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


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
    # Verificar si el usuario tiene una sesión activa y existe en la base de datos
    user_info = verifySessionAndGetUserInfo(request)
    if isinstance(user_info, Response):
        return user_info
    
    # Obtenemos los datos de usuario a actualizar desde la request.
    data = await request.json()

    # Validar que los campos requeridos no estén vacíos y tengan el formato correcto
    required_fields = ["nombre", "email", "imagen"]
    for field in required_fields:
        if field not in data or data[field] is None:
            print(PCTRL_WARN, f"El campo '{field}' fata o está vacío")
            return JSONResponse(content={"error": f"El campo '{field}' es requerido y no puede estar vacío"}, status_code=400)

    # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
    optional_fields = ["url", "bio"]
    for field in optional_fields:
        if field not in data or data[field] is None:
            data[field] = ""

    # Comprobamos si los cambios proporcionados no difieren de los que ya tiene el usuario, en cuyo caso no se haría nada (devuelve un mensaje de éxito)
    if all([
        user_info["nombre"] == data["nombre"],
        user_info["email"] == data["email"],
        user_info["bio"] == data["bio"],
        user_info["imagen"] == data["imagen"],
        user_info["url"] == data["url"]
    ]):
        print(PCTRL, "No hay cambios en el perfil del usuario")
        return JSONResponse(content={"success": True}, status_code=200)

    user = UsuarioDTO()
    user.load_from_dict(user_info)  # Cargamos los datos del usuario desde la base de datos

    user.set_nombre(data["nombre"])
    user.set_email(data["email"])
    user.set_bio(data["bio"])
    user.set_imagen(data["imagen"])
    user.set_url(data["url"])

    # Actualizar el usuario en la base de datos
    if model.update_usuario(user):
        print(PCTRL, "El usuario", user.get_email(), "actualizado en la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "El usuario", user.get_email(), "no ha sido actualizado en la base de datos!")
        return JSONResponse(content={"error": "El usuario no ha sido actualizado en la base de datos"}, status_code=500)
    
# Ruta para crear una nueva lista de reproducción
@app.post("/crear-lista")
async def crear_lista(request: Request, nombre_lista: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.add_lista_usuario(res["id"], nombre_lista)
    return RedirectResponse("/profile", status_code=302)

# Ruta para eliminar una lista de reproducción
@app.post("/remove-lista")
async def remove_lista(request: Request, nombre_lista: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.remove_lista_usuario(res["id"], nombre_lista)
    return RedirectResponse("/profile", status_code=302)

# Ruta para añadir una canción a una lista de reproducción
@app.post("/add-song-to-list")
async def add_song_to_list(request: Request, nombre_lista: str = Form(...), id_cancion: str = Form(...)):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    model.add_cancion_a_lista_usuario(res["id"], nombre_lista, id_cancion)
    return RedirectResponse("/profile", status_code=302)

# Ruta para eliminar una canción de una lista de reproducción
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
        print(PCTRL_WARN, "El usuario no es artista")
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
            print(PCTRL_WARN, "La canción creada por el usuario", song_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)

    # Por cada album en studio_albumes, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum creado por el usuario", album_id, "no se encuentra en la base de datos")
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
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Creamos un nuevo objeto AlbumDTO, utilizando los datos recibidos en el request
    data = await request.json()

    # Validar que los campos requeridos no estén vacíos y tengan el formato correcto
    required_fields = ["titulo", "autor", "generos", "portada", "precio"]
    for field in required_fields:
        if field not in data or data[field] is None:
            print(PCTRL_WARN, f"El campo '{field}' falta o está vacío")
            return JSONResponse(content={"error": f"El campo '{field}' es requerido y no puede estar vacío"}, status_code=400)
        
    # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
    optional_fields = ["descripcion", "colaboradores"]
    for field in optional_fields:
        if field not in data or data[field] is None:
            data[field] = ""

    # Validar que el precio sea un número positivo
    if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
        print(PCTRL_WARN, "El precio debe ser un número positivo")
        return JSONResponse(content={"error": "El precio debe ser un número positivo"}, status_code=400)

    # Validar que los géneros sean una lista no vacía
    if not isinstance(data["generos"], list) or not data["generos"]:
        print(PCTRL_WARN, "Los géneros deben ser una lista no vacía")
        return JSONResponse(content={"error": "Los géneros deben ser una lista no vacía"}, status_code=400)

    album = AlbumDTO()
    album.set_titulo(data["titulo"])
    album.set_autor(data["autor"])
    album.set_colaboradores(data["colaboradores"])
    album.set_descripcion(data["descripcion"])
    album.set_fecha(datetime.now()) # La fecha se caclula desde el lado del servidor
    album.set_generos(data["generos"])
    album.set_canciones(data["canciones"])
    album.set_visitas(0)
    album.set_portada(data["portada"])
    album.set_precio(data["precio"])
    album.set_likes(0)
    album.set_visible(data["visible"])
    album.set_historial([])
    # Inicializamos el campo historial como una lista vacía

    # Subir el album a la base de datos
    album_id = model.add_album(album)
    if album_id is not None:
        print(PCTRL, "El álbum", album_id, "subido a la base de datos")
    else:
        print(PCTRL_WARN, "El álbum", album_id, "no ha sido subido a la base de datos!")
        return JSONResponse(content={"error": "Error del sistema"}, status_code=500)

    try:
        # Por cada una de las canciones en el album, actualizamos su campo album con el id del nuevo album
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                raise Exception(f"La canción {song_id} no se encuentra en la base de datos")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)

            song["fechaUltimaModificacion"] = datetime.now() # Actualizamos la fecha de la canción
            song_object.add_historial(song)

            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                raise Exception(f"La canción {song_id} no ha sido actualizada en la base de datos!")

        # Obtenemos los datos de usuario de la base de datos y creamos un nuevo objeto UsuarioDTO
        user = UsuarioDTO()
        user.load_from_dict(res)

        # Añadimos al usuario la nueva referencia al album
        user.add_studio_album(album_id)

        # Actualizamos el usuario en la base de datos
        if model.update_usuario(user):
            print(PCTRL, "El usuario", user.get_email(), "ha sido actualizado en la base de datos!")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            raise Exception("El usuario no ha sido actualizado en la base de datos!")
        
    except Exception as e:
        print(PCTRL_WARN, "Error:", str(e))

        # Intentar destruir el album subido
        model.delete_album(album_id)
        print(PCTRL_WARN, "El álbum", album_id, "ha sido eliminado de la base de datos")

        # Intentar revertir los cambios en las canciones
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")

        # Intentar revertir los cambios en el usuario
        user = UsuarioDTO()
        user.load_from_dict(res)
        user.remove_studio_album(album_id)
        if model.update_usuario(user):
            print(PCTRL, "El usuario", user.get_email(), "ha sido actualizada en la base de datos!")
        else:
            print(PCTRL_WARN, "El usuario", user.get_email(), "no ha sido actualizada en la base de datos!")

        return JSONResponse(content={"error": "Error del sistema"}, status_code=500)

# Ruta para cargar la vista de album
@app.get("/album")
async def get_album(request: Request):
    #Leemos de la request el id del album y recogemos el album de la BD
    if request.query_params.get("id") is not None:
        album_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        album_id = data["id"]

    # Descargamos el album de la base de datos via su ID.
    album_info = model.get_album(album_id)
    if not album_info:
        print(PCTRL_WARN, "El álbum no existe en la base de datos")
        return Response("No autorizado", status_code=403)

    # Obtenemos los datos del usuario y comprobamos que tipo de usuario es
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        tipoUsuario = 0 # Guest
    else:
        if album_id in res["studio_albumes"]:
            tipoUsuario = 3 # Artista (creador)

        elif all(song_id in res["biblioteca"] for song_id in album_info["canciones"]):
            tipoUsuario = 2 # Propietario (User o Artista)

        else:
            tipoUsuario = 1 # Miembro (User)

    # Antes de nada, verificamos si el album es visible o no. Si no lo es, no se puede ver... Excepto si el usuario es el autor del album.
    if not album_info["visible"] and tipoUsuario != 3:
            print(PCTRL_WARN, "El álbum no es visible, solo el autor puede verlo")
            return Response("No autorizado", status_code=403)
        
    # Incrementar el contador de visitas del album, excepto si el usuario es el autor del album.
    if tipoUsuario != 3:
        album_info["visitas"] += 1
        album_object = AlbumDTO()
        album_object.load_from_dict(album_info)
        if not model.update_album(album_object):
            print(PCTRL_WARN, "El álbum", album_id, "no ha sido actualizado en la base de datos!")
            return Response("Error del sistema", status_code=403)
        
    duracion_total = 0

    # Descargamos las canciones del álbum de la base de datos vía su ID en el campo canciones y las insertamos en este album_info
    print(PCTRL, "Comenzando a poblar el álbum con canciones...")
    canciones_out : list[dict] = []
    for cancion_id in album_info["canciones"]:
        cancion = model.get_song(cancion_id)
        duracion_total += cancion["duracion"]
        if not cancion:
            print(PCTRL_WARN, "La canción", cancion_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)    
        
        # Convertimos los generos de cada canción a un string sencillo
        # Primero, descargamos todos los generos, escogemos su nombre, lo añadimos al string, y luego lo metemos en cancion["generosStr"]
        # Esto se hace por cada canción del album.
        print(PCTRL, "Convirtiendo canción genre to str...")
        generosStr = ""
        for genero_id in cancion["generos"]:
            genero = model.get_genero(genero_id)
            if not genero:
                print(PCTRL_WARN, "El género", genero_id ,"no encontrado en la base de datos")
                return Response("Error del sistema", status_code=403)
            generosStr += genero["nombre"] + ", "
        generosStr = generosStr[:-2] # Quitamos la última coma y espacio
        cancion["generosStr"] = generosStr # Añadimos el string a la canción

        canciones_out.append(cancion)

    album_info["canciones"] = canciones_out
    minutos = duracion_total // 60
    segundos = duracion_total % 60
    tiempo_formateado = f"{minutos:02d}:{segundos:02d}"


    # Convertimos los generos del album a un string sencillo
    # Primero, descargamos todos los generos, escogemos su nombre, lo añadimos al string, y luego lo metemos en album_info["generosStr"]
    print(PCTRL, "Convirtiendo album genre to str...")
    generosStr = ""
    for genero_id in album_info["generos"]:
        genero = model.get_genero(genero_id)
        if not genero:
            print(PCTRL_WARN, "El género", genero_id ,"no encontrado en la base de datos")
            return Response("Error del sistema", status_code=403)
        generosStr += genero["nombre"] + ", "
    generosStr = generosStr[:-2] # Quitamos la última coma y espacio
    album_info["generosStr"] = generosStr # Añadimos el string a la canción

    
    # Comprobamos si el usuario le ha dado like a la canción mirando si el id de la canción está en id_likes del usuario.
    isLiked = False
    if tipoUsuario > 0:
        isLiked = album_id in res["id_likes"]
    
    # Comprobarmos finalmente si el usuario (en caso de estar logeado) tiene un carrito activo el cual contiene el álbum.
    inCarrito = False
    if tipoUsuario > 0:
        carrito = model.get_carrito(res["id"]) 
        if carrito:
            for item in carrito["articulos"]:
                if item["id"] == album_id:
                    inCarrito = True
                    break
        else:
            print(PCTRL_WARN, "El carrito no ha sido encontrado en la base de datos! - skipping")

    # Donde tipo Usuario:
    # 0 = Guest
    # 1 = User
    # 2 = Propietario (User o Artista)
    # 3 = Artista (creador)
    return view.get_album_view(request, album_info, tipoUsuario, isLiked, inCarrito, tiempo_formateado) # Devolvemos la vista del album

# Ruta para cargar la vista de álbum-edit
@app.get("/album-edit")
async def get_album_edit(request: Request):
    #Leemos de la request el id del album
    if request.query_params.get("id") is not None:
        album_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        album_id = data["id"]
    if not album_id:
        print(PCTRL_WARN, "El ID del álbum no fue proporcionado en la request")
        return Response("No autorizado", status_code=400)

    # Verificar si el usuario tiene una sesión activa, si es artista y si el album existe, y si le pertenece.
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return Response("No autorizado", status_code=403)
    album_info = model.get_album(album_id)
    if not album_info:
        print(PCTRL_WARN, "El álbum no existe")
        return Response("No autorizado", status_code=403)
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "El álbum no se encuentra en los álbumes del usuario")
        return Response("No autorizado", status_code=403)

    # Ahora popularemos el album reemplazando las IDs (referencias) por los objetos reales
    canciones_out : list[dict] = []
    for cancion_id in album_info["canciones"]:
        cancion = model.get_song(cancion_id)
        if not cancion:
            print(PCTRL_WARN, "La cancion", cancion_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)   
        canciones_out.append(cancion)
    album_info["canciones"] = canciones_out

    for historial in album_info["historial"]:
        canciones_historial: list[dict] = []
        for cancion_id in historial["canciones"]:
            cancion = model.get_song(cancion_id)
            if not cancion:
                print(PCTRL_WARN, "La canción", cancion_id, "no se encuentra en la base de datos")
                return Response("Error del sistema", status_code=403)
            canciones_historial.append(cancion)
        historial["canciones"] = canciones_historial
        

    # Ya tenemos el album preparado. Pero ahora, tenemos que emular basicamente la misma funcionalidad que en upload-album, para que el artista pueda editar el album con nuevas canciones.
    # Así pues, copiamos y pegamos el código de upload-album para obtener las canciones válidas para un album nuevo.

    # Por cada canción en studio_canciones, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)

    # Por cada album en studio_albumes, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum", album_id, "no se encuentra en la base de datos")
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
    #Leemos de la request el id del album
    if request.query_params.get("id") is not None:
        album_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        album_id = data["id"]
    if not album_id:
        print(PCTRL_WARN, "El ID del álbum no fue proporcionado en la request")
        return JSONResponse(content={"error": "El ID del álbum no fue proporcionado"}, status_code=400)

    # Verificar si el usuario tiene una sesión activa, si es artista y si el album existe, y si le pertenece.
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    album_dict = model.get_album(album_id)
    if not album_dict:
        print(PCTRL_WARN, "El álbum no existe")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "El álbum no se encuentra en los álbumes del usuario")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)

    try:
        album = AlbumDTO()
        album.load_from_dict(album_dict)

        # Validar que los campos requeridos no estén vacíos y tengan el formato correcto
        required_fields = ["titulo", "autor", "generos", "portada", "precio"]
        for field in required_fields:
            if field not in data or data[field] is None:
                print(PCTRL_WARN, f"El campo '{field}' falta o está vacío")
                return JSONResponse(content={"error": f"El campo '{field}' es requerido y no puede estar vacío"}, status_code=400)

        # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
        optional_fields = ["descripcion", "colaboradores"]
        for field in optional_fields:
            if field not in data or data[field] is None:
               data[field] = ""

        # Validar que el precio sea un número positivo
        if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
            print(PCTRL_WARN, "El precio debe ser un número positivo")
            return JSONResponse(content={"error": "El precio debe ser un número positivo"}, status_code=400)

        # Validar que los géneros sean una lista no vacía
        if not isinstance(data["generos"], list) or not data["generos"]:
            print(PCTRL_WARN, "Los géneros deben ser una lista no vacía")
            return JSONResponse(content={"error": "Los géneros deben ser una lista no vacía"}, status_code=400)

        # Editamos el album con los nuevos datos recibidos en la request
        album.set_titulo(data["titulo"])
        album.set_autor(data["autor"])
        album.set_colaboradores(data["colaboradores"])
        album.set_descripcion(data["descripcion"])
        #album.set_fecha(datetime.now()) # La fecha no se puede editar.
        album.set_generos(data["generos"])
        album.set_canciones(data["canciones"])
        # album.set_visitas() # La cantidad de visitas no se puede editar.
        album.set_portada(data["portada"])
        album.set_precio(data["precio"])
        # album.set_likes() # La cantidad de likes no se puede editar.
        album.set_visible(data["visible"])

        album_dict["fechaUltimaModificacion"] = datetime.now() # Actualizamos la fecha de la última edición
        album.add_historial(album_dict)
        
        # Por cada una de las canciones en el album, actualizamos su campo album con el id del nuevo album
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                raise Exception(f"La canción {song_id} no se encuentra en la base de datos")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)

            song["fechaUltimaModificacion"] = datetime.now() # Actualizamos la fecha de la última edición
            song_object.add_historial(song)

            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                raise Exception(f"La canción {song_id} no ha sido actualizada en la base de datos!")

        # Actualizamos el album en la base de datos
        if model.update_album(album):
            print(PCTRL, "El álbum", album_id, "actualizado en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            raise Exception(f"El álbum {album_id} no ha sido actualizado en la base de datos!")
    
    except Exception as e:
        # Intentamos revertir los cambios en el album
        album_object = AlbumDTO()
        album_object.load_from_dict(album_dict)
        if model.update_album(album_object):
            print(PCTRL, "El álbum", album_id, "revertido en la base de datos")
        else:
            print(PCTRL_WARN, "El álbum", album_id, "no ha sido revertido en la base de datos!")

        # Intentar revertir los cambios en las canciones
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(None)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")

        # Intentamos asociar las canciones del album antiguo a su album original
        for song_id in album_dict["canciones"]:
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            
            # Actualizamos el campo album de la canción con el id del nuevo album
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")

        print(PCTRL_WARN, "Error al procesar el álbum", album_id, ", ¡la actualización a la base de datos falló!")
        return JSONResponse(content={"error": "Error del sistema"}, status_code=500)

@app.post("/last-version-album")
async def last_version_album_post(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)  
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    try:
        # Recibimos los datos del nuevo song editado, junto con su ID.
        data = await request.json()
        album_id = data["id"]  # ID del song a editar
        # Descargamos el song antiguo de la base de datos via su ID y verificamos que es creación del usuario.
        album_dict = model.get_album(album_id)

        if not album_dict:
            print(PCTRL_WARN, "El álbum no existe")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        
        if album_id not in res["studio_albumes"]:
            print(PCTRL_WARN, "El álbum no se encuentra en los álbumes del usuario")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        
        album = AlbumDTO()
        album.load_from_dict(album_dict)
        
        if album.revert_to_version_by_fecha(data["fechaUltimaModificacion"]):
            print(PCTRL, "El álbum", album_id, "ha sido revertido a la versión", data["fechaUltimaModificacion"])
        else:
            print(PCTRL_WARN, "El álbum", album_id, "no ha sido revertido a la versión", data["fechaUltimaModificacion"])
            return JSONResponse(content={"error": "Álbum no revertido"}, status_code=500)

        album_dict["fechaUltimaModificacion"] = datetime.now()
        album.add_historial(album_dict)
        album.set_fechaUltimaModificacion("")

        if album.get_canciones() is not None:
            for song_id in album_dict["canciones"]:
                song_dict = model.get_song(song_id)
                if not song_dict:
                    print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                    return JSONResponse(content={"error": "El Album de la versión que se quiere recuperar no existe"}, status_code=403)
                
                song_object = SongDTO()
                song_object.load_from_dict(song_dict)
                song_object.set_album(album_id)

                song_dict["fechaUltimaModificacion"] = datetime.now()
                song_object.add_historial(song_dict)

                if not model.update_song(song_object):
                    print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                    return JSONResponse(content={"error": "La canción no ha sido actualizada en la base de datos"}, status_code=500)
                
        
        elif album_dict["canciones"] is not None:
            # Si la canción no tiene un album, lo descargamos y lo actualizamos
            for song_id in album_dict["canciones"]:
                song_dict = model.get_song(song_id)
            
                if not song_dict:
                    print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                    return JSONResponse(content={"error": "La canción de la versión que se quiere recuperar no existe"}, status_code=403)
                
                song_object = SongDTO()
                song_object.load_from_dict(song_dict)
                song_object.set_album(None)

                song_dict["fechaUltimaModificacion"] = datetime.now()
                song_object.add_historial(song_dict)

                if not model.update_song(song_object):
                    print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
                    return JSONResponse(content={"error": "La canción no ha sido actualizada en la base de datos"}, status_code=500)
        
        if model.update_album(album):
            print(PCTRL, "El álbum", album_id, "actualizado en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            print(PCTRL_WARN, "El álbum", album_id, "no ha sido actualizado en la base de datos!")
            return JSONResponse(content={"error": "El álbum no ha sido actualizada en la base de datos"}, status_code=500)
    
    except Exception as e:
        print(PCTRL_WARN, "Error al procesar el álbum", album_id, ", la actualización a la base de datos falló!")
        return JSONResponse(content={"error": "El álbum no ha sido actualizada en la base de datos"}, status_code=500)
    
# Ruta para eliminar un álbum
@app.post("/delete-album")
async def delete_album_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Obtenemos el ID del álbum a eliminar desde la request
    data = await request.json()
    album_id = data.get("id")
    if not album_id:
        print(PCTRL_WARN, "El ID del álbum no fue proporcionado en la request")
        return JSONResponse(content={"error": "El ID del álbum no fue proporcionado"}, status_code=400)
    
    # Verificamos que el álbum existe y pertenece al usuario
    album = model.get_album(album_id)
    if not album:
        print(PCTRL_WARN, "El álbum no existe")
        return JSONResponse(content={"error": "El álbum no existe"}, status_code=404)
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "El álbum no se encuentra en los álbumes del usuario")
        return JSONResponse(content={"error": "El álbum no se encuentra en los álbumes del usuario"}, status_code=403)
    
    # Procedemos a la eliminación del álbum
    # Primero, borramos el campo album de cada una de las canciones que lo componen. Si algo falla, nos da igual.
    for song_id in album["canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no ha sido encontrada en la base de datos! - skipping")
            continue
        
        # Actualizamos el campo album de la canción con el id del nuevo album
        song_object = SongDTO()
        song_object.load_from_dict(song)

        song["fechaUltimaModificacion"] = datetime.now() # Actualizamos la fecha de la canción
        song_object.add_historial(song)

        song_object.set_album(None)
        if not model.update_song(song_object):
            print(PCTRL_WARN, "La canción", song_id, "no ha sido actualizada en la base de datos! - skipping")
            continue

    # Luego, borramos el álbum del studio_albumes del usuario
    user = UsuarioDTO()
    user.load_from_dict(res)
    user.remove_studio_album(album_id)
    if not model.update_usuario(user):
        print(PCTRL_WARN, "El usuario", user.get_email(), "no ha sido actualizado en la base de datos!")
        return JSONResponse(content={"error": "El usuario no ha sido actualizado en la base de datos"}, status_code=500)
    
    # Por último, borramos el álbum de la base de datos
    if model.delete_album(album_id):
        print(PCTRL, "El álbum", album_id, "ha sido eliminado de la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "El álbum", album_id, "no ha sido eliminado de la base de datos")
        return JSONResponse(content={"error": "El álbum no ha sido eliminado de la base de datos"}, status_code=500)
        
# Ruta para darle like a un álbum
@app.post("/like-album")
async def like_album_post(request: Request):
    # Verificar si el usuario tiene una sesión activa
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    # Obtenemos el ID del álbum al que se le va a dar like desde la request
    data = await request.json()
    album_id = data.get("id")
    if not album_id:
        print(PCTRL_WARN, "El ID del álbum no fue proporcionado en la request")
        return JSONResponse(content={"error": "El ID del álbum no fue proporcionado"}, status_code=400)
    
    # Comprobamos que el usuario no le haya dado like al álbum ya.
    # Para ello, comprobamos que el id del álbum no esté en id_likes.
    # Si ya le ha dado like, entonces debemos quitarle el like.
    # Si no, le damos like al álbum.
    user_object = UsuarioDTO()
    user_object.load_from_dict(res)

    if album_id in user_object.get_id_likes():
        user_object.remove_id_like(album_id)
        delta = -1
        message = "Like eliminado"
    else:
        user_object.add_id_like(album_id)
        delta = 1
        message = "Like añadido"

    album = model.get_album(album_id)
    if album:
        album_object = AlbumDTO()
        album_object.load_from_dict(album)
        album_object.set_likes(album_object.get_likes() + delta)
        if not model.update_album(album_object):
            print(PCTRL_WARN, "Error al actualizar el álbum en la base de datos")
            return JSONResponse(content={"error": "Error al actualizar el álbum en la base de datos"}, status_code=500)
    else:
        print(PCTRL_WARN, "El álbum no existe en la base de datos")
        return JSONResponse(content={"error": "El álbum no existe en la base de datos"}, status_code=404)

    if model.update_usuario(user_object):
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "Error al actualizar el usuario en la base de datos")
        return JSONResponse(content={"error": "Error al actualizar el usuario en la base de datos"}, status_code=500)



# ------------------------------------------------------------------ #
# ----------------------------- INCLUDES --------------------------- #
# ------------------------------------------------------------------ #

# Ruta para cargar el header
@app.get("/header")
def header(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return view.get_header_view(request, None) # Si es un Response, devolvemos la vista de guest
    
    return view.get_header_view(request, res)  # Si es un dict, pasamos los datos del usuario

# Ruta para cargar el footer
@app.get("/footer")
def footer(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return view.get_footer_view(request, None)
    
    return view.get_footer_view(request, res)  # Si es un dict, pasamos los datos del usuario


# ------------------------------------------------------------- #
# --------------------------- ABOUT --------------------------- #
# ------------------------------------------------------------- #

# Ruta para cargar la vista de about
@app.get("/about" , description="Muestra información sobre Undersounds")
def about(request: Request):
    return view.get_about_view(request)


# ------------------------------------------------------------ #
# --------------------------- FAQS --------------------------- #
# ------------------------------------------------------------ #

# Ruta para cargar la vista de FAQs
@app.get("/faqs", description="Muestra preguntas frecuentes desde MongoDB")
def get_faqs(request: Request):
    faqs_json = model.get_faqs()
    return view.get_faqs_view(request, faqs_json)


# ------------------------------------------------------------------ #
# ----------------------------- CARRITO ---------------------------- #
# ------------------------------------------------------------------ #

# Ruta para cargar la vista del carrito y añadir artículos al carrito
@app.api_route("/cart", methods=["GET", "POST"], description="Muestra los artículos de tu cesta")
async def get_carrito(request: Request):
    
    # Así se obtendría el usuario, por motivos de prueba, se probará un usuario fijo
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res
    
    form_data = await request.form()
    action = form_data.get("action")  # Por defecto: añadir
    item_id = form_data.get("item_id")
    
    if request.method == "POST":

        carrito_json = model.get_carrito(res["id"])
        if not carrito_json:
            print(PCTRL_WARN, "El carrito no se ha encontrado en la base de datos! - skipping")
            return JSONResponse(content={"error": "El carrito no se ha encontrado en la base de datos"}, status_code=500)
        
        if action == "decrement":
            if not item_id:
                return "Falta el ID del artículo para decrementarlo/eliminarlo", 400 
            # Eliminar el artículo del carrito
            model.deleteArticulo(res["id"], item_id)
        
        elif action == "add":
            
            if model.articulo_existe(carrito_json, item_id):
                print(PCTRL_WARN, "El artículo ya existe en el carrito")

                carrito_json = model.get_carrito(res["id"])
                if not carrito_json:
                    print(PCTRL_WARN, "El carrito no se ha encontrado en la base de datos! - skipping")
                    return JSONResponse(content={"error": "El carrito no se ha encontrado en la base de datos"}, status_code=500)
                    
                return view.get_carrito_view(request, carrito_json)
            
            else:
                articulo = ArticuloCestaDTO()
                articulo.set_id(form_data.get("item_id"))
                articulo.set_nombre(form_data.get("item_name"))
                articulo.set_precio(form_data.get("item_precio"))
                articulo.set_descripcion(form_data.get("item_desc"))
                articulo.set_artista(form_data.get("artist_name"))
                articulo.set_cantidad(1)
                articulo.set_imagen(form_data.get("item_image"))

                # Añadir el artículo al carrito
                model.upsert_articulo(res["id"], articulo)

    carrito_json = model.get_carrito(res["id"])
    if not carrito_json:
        print(PCTRL_WARN, "El carrito no se ha encontrado en la base de datos! - skipping")
        return JSONResponse(content={"error": "El carrito no se ha encontrado en la base de datos"}, status_code=500)
        
    return view.get_carrito_view(request, carrito_json)


# ------------------------------------------------------------------ #
# ----------------------------- PREPAID ---------------------------- #
# ------------------------------------------------------------------ #

# Ruta para cargar la vista de prepaid
@app.get("/prepaid")
def get_prepaid(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    carrito_json = model.get_carrito(res["id"]) 

    return view.get_prepaid_view(request, carrito_json)


# -------------------------------------------------------------- #
# ----------------------------- TPV ---------------------------- #
# -------------------------------------------------------------- #

# Ruta para cargar la vista de tpv
@app.post("/tpv")
def get_tpv(request: Request):

    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res
    
    try:
        user = UsuarioDTO()
        user.load_from_dict(res)

        carrito = model.get_carrito(user.get_id())

        for item in carrito["articulos"]:
            # Comprobamos si es una canción o un álbum
            song = model.get_song(item["id"])
            if song:
                user.add_song_to_biblioteca(song["id"])
            else:
                album = model.get_album(item["id"])
                if album:
                    for song_id in album["canciones"]:
                        user.add_song_to_biblioteca(song_id)

        if model.update_usuario(user):
            print(PCTRL, "El usuario", user.get_nombre(), "actualizado en la base de datos")
        else:
            print(PCTRL_WARN, "El usuario", user.get_nombre(), "no ha sido actualizado en la base de datos!")
            return JSONResponse(content={"error": "El usuario no ha sido actualizado en la base de datos"}, status_code=500)

        if model.vaciar_carrito(res["id"]):
            print(PCTRL, "Carrito vaciado en la base de datos")
        else:
            print(PCTRL_WARN, "Actualización del carrito fallida")
            return JSONResponse(content={"error": "Actualización del carrito fallida"}, status_code=500)
            
    except Exception as e:
        print(PCTRL_WARN, "Error al procesar Tpv, la base de datos falló con el error:", str(e))
        return JSONResponse(content={"error": "Carrito y Usuario no actualizados a base de datos"}, status_code=500)

    return view.get_tpv_view(request)


# ------------------------------------------------------------ #
# --------------------------- PURCHASED ---------------------- #
# ------------------------------------------------------------ #

# Ruta para cargar la vista de purchased
@app.get("/purchased")
def get_purchased(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res

    songs = model.get_songs()

    # Devolvemos la vista de purchased con el carrito
    return view.get_purchased_view(request, res, songs)


# ------------------------------------------------------------ #
# --------------------------- CONTACT ------------------------ #
# ------------------------------------------------------------ #

# Ruta para cargar la vista de contacto
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
        return JSONResponse(content={"error": "Formulario inválido"}, status_code=400)
    
    # Crear objeto ContactoDTO y asignar los valores del formulario
    contacto = ContactoDTO()
    contacto.set_nombre(data.get("name"))
    contacto.set_email(data.get("email"))
    contacto.set_telefono(data.get("telf"))
    contacto.set_mensaje(data.get("msg"))
    
    # Llamar a la función del modelo para guardar el reporte en la base de datos y devolver respuesta
    if model.add_contacto(contacto):
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        return JSONResponse(content={"error": "Error al enviar el formulario"}, status_code=500)


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
        print(PCTRL_WARN, "El usuario no es artista")
        return Response("No autorizado", status_code=403)
    
    return view.get_upload_song_view(request)

# Ruta para procesar la petición de upload-song
@app.post("/upload-song")
async def upload_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401) # Si es un Response, devolvemos el error
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Registrar la cancion en la base de datos
    data = await request.json()

    # Validar que los campos requeridos no estén vacíos y tengan el formato correcto
    required_fields = ["titulo", "artista", "generos", "portada", "precio"]
    for field in required_fields:
        if field not in data or data[field] is None:
            print(PCTRL_WARN, f"El campo '{field}' falta o está vacío")
            return JSONResponse(content={"error": f"El campo '{field}' es requerido y no puede estar vacío"}, status_code=400)
        
    # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
    optional_fields = ["descripcion", "colaboradores"]
    for field in optional_fields:
        if field not in data or data[field] is None:
            data[field] = ""

    # Validar que el precio sea un número positivo
    if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
        print(PCTRL_WARN, "El precio debe ser un número positivo")
        return JSONResponse(content={"error": "El precio debe ser un número positivo"}, status_code=400)

    # Validar que los géneros sean una lista no vacía
    if not isinstance(data["generos"], list) or not data["generos"]:
        print(PCTRL_WARN, "Los géneros deben ser una lista no vacía")
        return JSONResponse(content={"error": "Los géneros deben ser una lista no vacía"}, status_code=400)
    
    if not isinstance(data["pista"], str) or not data["pista"]:
        print(PCTRL_WARN, "La pista debe ser un archivo no vacío")
        return JSONResponse(content={"error": "La pista debe ser un archivo no vacío"}, status_code=400)


    song = SongDTO()
    song.set_titulo(data["titulo"])
    song.set_artista(data["artista"])
    song.set_colaboradores(data["colaboradores"])
    song.set_fecha(datetime.now())
    song.set_fechaUltimaModificacion("")
    song.set_descripcion(data["descripcion"])
    song.set_generos(data["generos"])
    song.set_likes(0)
    song.set_visitas(0)
    song.set_portada(data["portada"])
    song.set_precio(data["precio"])
    song.set_lista_resenas([])
    song.set_visible(data["visible"])
    song.set_pista(data["pista"])
    duracion = data["duracion"]
    song.set_duracion(int(duracion))
    song.set_album(None)  # El album se asigna posteriormente en el editor de albumes
    song.set_historial([])  # Inicializamos el historial como una lista vacía

    try:
        song_id = model.add_song(song)

        if song_id is not None:
            print(PCTRL, "Canción registrada en la base de datos")
        else:
            print(PCTRL_WARN, "Error al registrar la canción en la base de datos")
            return JSONResponse(content={"error": "Error al registrar la canción en la base de datos"}, status_code=500)

        # Convertirmos res en un objeto UsuarioDTO, le añadimos la nueva canción a studio_canciones y lo actualizamos en la base de datos
        user = UsuarioDTO()
        user.load_from_dict(res)
        user.add_studio_cancion(song_id)
        user.add_song_to_biblioteca(song_id)
        if model.update_usuario(user):
            print(PCTRL, "El usuario", user.get_email(), "ha sido actualizado en la base de datos!")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            print(PCTRL_WARN, "El usuario", user.get_email(), "no ha sido actualizado en la base de datos!")
            raise Exception("El usuario no ha sido actualizado en la base de datos")

    except Exception as e:
        print(PCTRL_WARN, "Error al procesar la canción", song_id, ", ¡no se pudo agregar a la base de datos!")
        # Eliminar la canción subida (intentar tanto si se ha subido como si no)
        model.delete_song(song_id)
        return JSONResponse(content={"error": "La canción no se añadió a la base de datos"}, status_code=500)

# Ruta para la subida del archivo mp3
@app.post("/upload-song-file")
async def upload_song_file(request: Request, pista: UploadFile = File(...)):
    # Verificar si el usuario tiene una sesión activa y es artista
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)  # Si es un Response, devolvemos el error
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es un artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)

    # Obtener el nombre del archivo y la ruta de almacenamiento
    filename = pista.filename
    file_path = os.path.join("static", "mp3", filename)

    # Validar el archivo
    if not filename:
        print(PCTRL_WARN, "No se seleccionó ningún archivo")
        return JSONResponse(content={"error": "No se seleccionó ningún archivo"}, status_code=400)

    if pista.content_type not in ["audio/mpeg", "audio/mp3", "audio/wav"]:
        print(PCTRL_WARN, f"Tipo de archivo inválido: {pista.content_type}")
        return JSONResponse(content={"error": "Tipo de archivo inválido. Solo se permiten MP3 y WAV."}, status_code=400)

    file_content = await pista.read()

    # Intentar guardar el archivo
    try:
        # Asegurarse de que la carpeta exista
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Guardar el archivo en el sistema
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Respuesta exitosa
        print(PCTRL, f"Archivo {filename} subido exitosamente a {file_path}")
        return JSONResponse(content={"success": True, "filename": filename}, status_code=200)

    except Exception as e:
        print(PCTRL_WARN, f"Error al subir el archivo {filename}: {str(e)}")
        return JSONResponse(content={"error": "Error al subir el archivo"}, status_code=500)
    
# Ruta para cargar vista song
@app.get("/song")
async def get_song(request: Request):
    # Recuperamos el id de la canción desde la request
    if request.query_params.get("id") is not None:
        song_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        song_id = data["id"]
    if not song_id:
        return Response("Falta el parámetro 'id'", status_code=400)

    # Verificar si el usuario tiene una sesión activa.
    user_db = verifySessionAndGetUserInfo(request)
    
    # Comprobamos que tipo de usuario es
    if isinstance(user_db, Response):
        tipoUsuario = 0 # Guest
    else:
        if song_id in user_db["studio_canciones"]:
            tipoUsuario = 3 # Artista (creador)

        elif song_id in user_db["biblioteca"]:
            tipoUsuario = 2 # Propietario (User o Artista)

        else:
            tipoUsuario = 1 # Miembro (User)

    # Descargamos la canción de la base de datos via su ID y comprobamos si existe.
    song_info = model.get_song(song_id)
    if not song_info:
        print(PCTRL_WARN, "La cancion no existe")
        return Response("No existe", status_code=403)
    
    # Antes de hacer nada, comprobamos si la canción es visible o no. Si no es visible, solo el artista creador puede verla.
    if not song_info["visible"] and tipoUsuario != 3:
            print(PCTRL_WARN, "La canción no es visible, solo el artista creador puede verla")
            return Response("No autorizado", status_code=403)
        
    # Incrementar el contador de visitas de song, excepto si el usuario es el autor de la canción.
    if tipoUsuario != 3:
        song_info["visitas"] += 1
        song_object = SongDTO()
        song_object.load_from_dict(song_info)
        if not model.update_song(song_object):
            print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)

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

    # Descargamos el album asociado a la canción, extraemos su nombre y lo insertamos en el campo albumStr de la canción.
    # Si no tiene album, dejamos albumStr como None.
    if song_info["album"]:
        album = model.get_album(song_info["album"])
        if not album:
            print(PCTRL_WARN, "Album", song_info["album"], "not found in database")
            return Response("Error del sistema", status_code=403)
        song_info["albumStr"] = album["titulo"]
    else:
        song_info["albumStr"] = None

    # Comprobamos si el usuario le ha dado like a la canción mirando si el id de la canción está en id_likes del usuario.
    isLiked = False
    if tipoUsuario > 0:
        isLiked = song_id in user_db["id_likes"]

    # Donde tipo Usuario:
    # 0 = Guest
    # 1 = User
    # 2 = Propietario (User o Artista)
    # 3 = Artista (creador)

    # Comprobarmos finalmente si el usuario (en caso de estar logeado) tiene un carrito activo el cual contiene la canción.
    inCarrito = False
    if tipoUsuario > 0:
        carrito = model.get_carrito(user_db["id"]) 
        if carrito:
            for item in carrito["articulos"]:
                if item["id"] == song_id:
                    inCarrito = True
                    break
        else:
            print(PCTRL_WARN, "El carrito no se ha encontrado en la base de datos! - skipping")
        
    return view.get_song_view(request, song_info, tipoUsuario, user_db, isLiked, inCarrito) # Devolvemos la vista del song

# Ruta para cargar vista edit-song
@app.get("/edit-song")
async def get_edit_song(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return Response("No autorizado", status_code=403)
    
    # Leemos de la request el id de la canción
    if request.query_params.get("id") is not None:
        song_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        song_id = data["id"]

    if not song_id:
        return Response("Falta el parámetro 'id'", status_code=400)

    # Descargamos la canción de la base de datos via su ID y comprobamos si es creación del usuario.
    song_info = model.get_song(song_id)

    for historial in song_info["historial"]:
        if historial["album"]:
            album = model.get_album(historial["album"])
            if not album:
                print(PCTRL_WARN, "El álbum", historial["album"], "no existe")
                historial["albumStr"] = None
            else:
                historial["albumStr"] = album["titulo"]
        else:
            historial["albumStr"] = None

    
    if not song_info:
        print(PCTRL_WARN, "La canción no existe")
        return Response("No autorizado", status_code=403)
    if song_id not in res["studio_canciones"]:
        print(PCTRL_WARN, "La canción no se encuentra en el estudio del usuario")
        return Response("No autorizado", status_code=403)

    return view.get_edit_song_view(request, song_info)

# Ruta para procesar la petición de edit-song
@app.post("/edit-song")
async def edit_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)  
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    try:
        # Recibimos los datos del nuevo song editado, junto con su ID.
        data = await request.json()
        song_id = data["id"]  # ID del song a editar

        # Descargamos el song antiguo de la base de datos via su ID y verificamos que es creación del usuario.
        song_dict = model.get_song(song_id)
        if not song_dict:
            print(PCTRL_WARN, "La canción no existe")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        if song_id not in res["studio_canciones"]:
            print(PCTRL_WARN, "La canción no se encuentra en el estudio del usuario")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        
        # Validar que los campos requeridos no estén vacíos y tengan el formato correcto
        required_fields = ["titulo", "artista", "generos", "portada", "precio"]
        for field in required_fields:
            if field not in data or data[field] is None:
                print(PCTRL_WARN, f"El campo '{field}' falta o está vacío")
                return JSONResponse(content={"error": f"El campo '{field}' es requerido y no puede estar vacío"}, status_code=400)

        # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
        optional_fields = ["descripcion", "colaboradores"]
        for field in optional_fields:
            if field not in data or data[field] is None:
               data[field] = ""

        # Validar que el precio sea un número positivo
        if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
            print(PCTRL_WARN, "El precio debe ser un número positivo")
            return JSONResponse(content={"error": "El precio debe ser un número positivo"}, status_code=400)

        # Validar que los géneros sean una lista no vacía
        if not isinstance(data["generos"], list) or not data["generos"]:
            print(PCTRL_WARN, "Los géneros deben ser una lista no vacía")
            return JSONResponse(content={"error": "Los géneros deben ser una lista no vacía"}, status_code=400)
    
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

        song_dict["fechaUltimaModificacion"] = datetime.now()
        song.add_historial(song_dict)

        # Actualizamos el song en la base de datos
        if model.update_song(song):
            print(PCTRL, "La canción", song_id, "ha sido actualizada en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            return JSONResponse(content={"error": "El álbum no ha sido actualizada en la base de datos"}, status_code=500)
    
    except Exception as e:
        print(PCTRL_WARN, "Error al procesar la canción", song_id, ", la actualización a la base de datos falló!")
        return JSONResponse(content={"error": "Canción no actualizada en la base de datos"}, status_code=500)

# Ruta para procesar la petición de last-version (cargar una versión anterior de la canción)
@app.post("/last-version")
async def last_version_post(request: Request):
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)  
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    try:
        # Recibimos los datos del nuevo song editado, junto con su ID.
        data = await request.json()
        song_id = data["id"]  # ID del song a editar
        # Descargamos el song antiguo de la base de datos via su ID y verificamos que es creación del usuario.
        song_dict = model.get_song(song_id)

        if not song_dict:
            print(PCTRL_WARN, "La canción no existe")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        
        if song_id not in res["studio_canciones"]:
            print(PCTRL_WARN, "La canción no se encuentra en el estudio del usuario")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        
        song = SongDTO()
        song.load_from_dict(song_dict)
        
        if song.revert_to_version_by_fecha(data["fechaUltimaModificacion"]):
            print(PCTRL, "La canción", song_id, "ha sido revertida a la versión", data["fechaUltimaModificacion"])
        else:
            print(PCTRL_WARN, "La canción", song_id, "no ha sido revertida a la versión", data["fechaUltimaModificacion"])
            return JSONResponse(content={"error": "La canción no se ha revertido"}, status_code=500)

        song_dict["fechaUltimaModificacion"] = datetime.now()
        song.add_historial(song_dict)
        song.set_fechaUltimaModificacion("")

        if song.get_album() is not None:
            # Si la canción tiene un album, lo descargamos y lo actualizamos
            album_dict = model.get_album(song.get_album())
            if not album_dict:
                print(PCTRL_WARN, "El álbum", song.get_album(), "no existe")
                return JSONResponse(content={"error": "El Album de la versión que se quiere recuperar no existe"}, status_code=403)
            
            album_object = AlbumDTO()
            album_object.load_from_dict(album_dict)
            album_object.add_cancion(song_id)

            album_dict["fechaUltimaModificacion"] = datetime.now()
            album_object.add_historial(album_dict)

            if not model.update_album(album_object):
                print(PCTRL_WARN, "El álbum", song.get_album(), "no se encuentra en la base de datos")
                return JSONResponse(content={"error": "El álbum no ha sido actualizada en la base de datos"}, status_code=500)
        
        elif song_dict["album"] is not None:
            # Si la canción no tiene un album, lo descargamos y lo actualizamos
            album_dict = model.get_album(song_dict["album"])
            if not album_dict:
                print(PCTRL_WARN, "El álbum", song_dict["album"], "no se encuentra en la base de datos")
                return JSONResponse(content={"error": "El Album de la versión que se quiere recuperar no existe"}, status_code=403)
            
            album_object = AlbumDTO()
            album_object.load_from_dict(album_dict)
            album_object.remove_cancion(song_id)

            album_dict["fechaUltimaModificacion"] = datetime.now()
            album_object.add_historial(album_dict)

            if not model.update_album(album_object):
                print(PCTRL_WARN, "El álbum", song.get_album(), "no se encuentra en la base de datos")
                return JSONResponse(content={"error": "El álbum no ha sido actualizada en la base de datos"}, status_code=500)
        
        if model.update_song(song):
            print(PCTRL, "La canción", song_id, "ha sido actualizada en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            return JSONResponse(content={"error": "Canción no actualizada en la base de datos"}, status_code=500)
    
    except Exception as e:
        print(PCTRL_WARN, "Error al procesar la canción", song_id, ", la actualización a la base de datos falló!")
        return JSONResponse(content={"error": "Canción no actualizada en la base de datos"}, status_code=500)

# Ruta para eliminar una canción
@app.post("/delete-song")
async def delete_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Obtenemos el ID de la canción a eliminar desde la request
    data = await request.json()
    song_id = data.get("id")
    if not song_id:
        print(PCTRL_WARN, "ID de canción no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID de canción no proporcionada"}, status_code=400)
    
    # Verificamos que la canción existe y pertenece al usuario
    song = model.get_song(song_id)
    if not song:
        print(PCTRL_WARN, "La canción no existe")
        return JSONResponse(content={"error": "La canción no existe"}, status_code=404)
    if song_id not in res["studio_canciones"]:
        print(PCTRL_WARN, "La canción no se encuentra en el estudio del usuario")
        return JSONResponse(content={"error": "La canción no se encuentra en el estudio del usuario"}, status_code=403)
    
    # Procedemos a la eliminación de la canción
    # Primero, descargaremos el album al que pertenece la canción, y eliminaremos la canción de su campo canciones.
    # Si no pertenece a ningun album, no haremos nada.
    if song["album"] is not None:
        album = model.get_album(song["album"])
        if not album:
            print(PCTRL_WARN, "El álbum no existe")
            return JSONResponse(content={"error": "El álbum no existe"}, status_code=404)
        album_object = AlbumDTO()
        album_object.load_from_dict(album)
        album["fechaUltimaModificacion"] = datetime.now()
        album_object.add_historial(album)
        album_object.remove_cancion(song_id)

        if not model.update_album(album_object):
            print(PCTRL_WARN, "El álbum", album["id"], "no se encuentra en la base de datos")
            return JSONResponse(content={"error": "El álbum no ha sido actualizada en la base de datos"}, status_code=500)
    
    # Luego, borramos la canción del studio_canciones del usuario
    user = UsuarioDTO()
    user.load_from_dict(res)
    user.remove_studio_cancion(song_id)
    if not model.update_usuario(user):
        print(PCTRL_WARN, "El usuario", user.get_email(), "no ha sido actualizado en la base de datos!")
        return JSONResponse(content={"error": "El usuario no ha sido actualizado en la base de datos"}, status_code=500)
    
    # Borrado en cascada de la canción de las listas de reproducción del usuario
    usuarios = model.get_usuarios_by_song_in_list(song_id)
    for usuario_dict in usuarios:
        usuario_dto = UsuarioDTO()
        usuario_dto.load_from_dict(usuario_dict)

        for lista in usuario_dto.get_listas_reproduccion():
            if song_id in lista.get("canciones", []):
                usuario_dto.remove_song_from_lista_reproduccion(lista.get("nombre"), song_id)
                model.update_usuario(usuario_dto)
                
    # Borrado en cascada de la canción de la biblioteca del usuario
    usuarios = model.get_usuarios_by_song(song_id)
    for usuario_dict in usuarios:
        usuario_dto = UsuarioDTO()
        usuario_dto.load_from_dict(usuario_dict)
        usuario_dto.remove_song_from_biblioteca(song_id)
        model.update_usuario(usuario_dto)
    
    # Ruta completa al archivo .mp3
    mp3_path = os.path.join(os.path.dirname(__file__), "..", "static", "mp3", data.get("pista"))

    # Borrar el archivo si existe
    if os.path.exists(mp3_path):
        os.remove(mp3_path)
        print(PCTRL, "El archivo MP3 ", mp3_path, "ha sido eliminado")
    else:
        print(PCTRL_WARN, "El archivo MP3", mp3_path, "no existe")

    # Por último, borramos la canción de la base de datos
    if model.delete_song(song_id):
        print(PCTRL, "La canción", song_id, "ha sido eliminada de la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "La canción", song_id, "no eliminada de la base de datos")
        return JSONResponse(content={"error": "La canción no se eliminó de la base de datos"}, status_code=500)

# Ruta para darle like a una canción
@app.post("/like-song")
async def like_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    # Obtenemos el ID de la canción a la que se le va a dar like desde la request
    data = await request.json()
    song_id = data.get("id")
    if not song_id:
        print(PCTRL_WARN, "ID de canción no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID de canción no proporcionada"}, status_code=400)
    
    # Comprobamos que el usuario no le haya dado like a la canción ya.
    # Para ello, comprobamos que el id de la canción no esté en id_likes.
    # Si ya le ha dado like, entonces debemos quitarle el like.
    # Si no, le damos like a la canción.
    user_object = UsuarioDTO()
    user_object.load_from_dict(res)

    if song_id in user_object.get_id_likes():
        user_object.remove_id_like(song_id)
        delta = -1
        message = "Like eliminado"
    else:
        user_object.add_id_like(song_id)
        delta = 1
        message = "Like añadido"

    song = model.get_song(song_id)
    if song:
        song_object = SongDTO()
        song_object.load_from_dict(song)
        song_object.set_likes(song_object.get_likes() + delta)
        if not model.update_song(song_object):
            print(PCTRL_WARN, "¡Error al actualizar los likes de las canciones en la base de datos!")
            return JSONResponse(content={"error": "Error al actualizar los likes de las canciones en la base de datos"}, status_code=500)
    else:
        print(PCTRL_WARN, "La canción no se encuentra en la base de datos")
        return JSONResponse(content={"error": "La canción no se encuentra en la base de datos"}, status_code=404)

    if model.update_usuario(user_object):
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "Error al actualizar el usuario en la base de datos!")
        return JSONResponse(content={"error": "Error al actualizar el usuario en la base de datos"}, status_code=500)


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
        print(PCTRL_WARN, "El usuario no es artista")
        return Response("No autorizado", status_code=403)
    
    # Descargamos los albumes y canciones del usuario
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum", album_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)
    
    # Descargamos las canciones del usuario
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
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

    return view.get_studio_view(request, user_songs_objects, user_albums_objects, res)

# Ruta para procesar los ajustes de studio
@app.post("/studio-settings")
async def studio_settings_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Recuperar los campos enablePage, showEmail de la request
    data = await request.json()
    esVisible = data.get("esVisible")
    emailVisible = data.get("emailVisible")
    
    # Convertimos el usuario a objeto, aplicar cambios y volver a subirlo
    user_object = UsuarioDTO()
    user_object.load_from_dict(res)
    user_object.set_esVisible(esVisible)
    user_object.set_emailVisible(emailVisible)
    if model.update_usuario(user_object):
        print(PCTRL, "El usuario", user_object.get_email(), "ha sido actualizado en la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "El usuario", user_object.get_email(), "no ha sido actualizado en la base de datos!")
        return JSONResponse(content={"error": "El usuario no ha sido actualizado en la base de datos"}, status_code=500)


# --------------------------------------------------------------- #
# ---------------------------- ARTISTA -------------------------- #
# --------------------------------------------------------------- #

# DEBUG MERCH
@app.get("/merch")
def get_merch(request: Request):
    return view.get_merch_view(request)

# Ruta para cargar la vista de artista
@app.get("/artista")
async def get_artista(request: Request):
    # Recuperamos el ID del artista (usuario) desde la query
    if request.query_params.get("id") is not None:
        artista_id = request.query_params.get("id") # Developer
    else:
        data = await request.json() # API
        artista_id = data["id"]
    if not artista_id:
        return Response("Falta el parámetro 'id'", status_code=400)
    
    # Descargamos el artista (usuario) de la base de datos
    artista_info = model.get_usuario(artista_id)
    if not artista_info:
        print(PCTRL_WARN, "El artista no existe")
        return Response("No autorizado", status_code=403)
    
    # Antes de nada, comprobamos si el artista es visible o no. Si no es visible, solo el artista creador puede verla.
    res = verifySessionAndGetUserInfo(request)
    if not artista_info["esVisible"]:
        if isinstance(res, Response) or artista_id != res["id"]:
            print(PCTRL_WARN, "El artista no es visible, solo el artista creador puede verlo")
            return Response("No autorizado", status_code=403)
        
    # Descargamos los albumes del artista
    user_albums_objects = []
    for album_id in artista_info["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum", album_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)
        # Solo si el album es visible lo añadimos a la lista
        if album["visible"]:
            user_albums_objects.append(album)

    # Descargamos todas las canciones del artista
    user_songs_objects = []
    for song_id in artista_info["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no se encuentra en la base de datos")
            return Response("Error del sistema", status_code=403)
        # Solo si la canción es visible lo añadimos a la lista
        if song["visible"]:
            user_songs_objects.append(song)

    # Filtramos que canciones son singles y las guardamos en una lista.
    # Los singles son canciones que en su campo album tienen el valor None.
    singles = []
    for song in user_songs_objects:
        if song["album"] is None:
            singles.append(song)


    if isinstance(res, Response):
        tipoUsuario = 0 # Guest
    else:
        if artista_id == res["id"]:
            tipoUsuario = 3 # Artista (creador)
        else:
            tipoUsuario = 1

    # Donde tipo Usuario:
    # 0 = Guest
    # 1 = User
    # x
    # 3 = Artista (creador)
    return view.get_artista_view(request, artista_info, singles, user_albums_objects, user_songs_objects, tipoUsuario)


# ------------------------------------------------------------ #
# --------------------------- Reseña ------------------------- #
# ------------------------------------------------------------ #

# Ruta para añadir una reseña a una canción
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
        reseña.set_usuario(user_db["id"])

        # Guardar en base de datos
        reseña_id = model.add_reseña(reseña)
        if reseña_id:
            print(PCTRL, "Al reseña añadida con ID:", reseña_id)
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
    
# Ruta para eliminar una reseña de una canción
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

            if user_db["id"] != reseña_data["usuario"]:
                return JSONResponse(status_code=500, content={"error": "La reseña no te pertenece."})

            song_dict = model.get_song(song_id)
            song = SongDTO()
            song.load_from_dict(song_dict)
            song.remove_resena(reseña_data)

            if model.update_song(song):
                print(PCTRL, "Reseña eliminada de la canción", song_id )
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo eliminar la reseña de la cancion "})

            if model.delete_reseña(reseña_id):
                return JSONResponse(status_code=200, content={"message": "Reseña eliminada."})
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo eliminar la reseña."})

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

# Ruta para actualizar una reseña de una canción
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
                print(PCTRL, "Reseña editada en la canción", song_id )
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo actualizar la reseña."})

            if model.update_reseña(reseña):
                return JSONResponse(status_code=200, content={"message": "Reseña actualizada."})
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo actualizar la reseña."})

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
        
        
# -------------------------------------------------------------------------- #
# --------------------------- RADIO ---------------------------------------- #
# -------------------------------------------------------------------------- #

# Ruta para cargar la vista de radio      
@app.get("/play", response_class=HTMLResponse)
def play(request: Request):
    return view.get_play_view(request)


# -------------------------------------------------------------------------- #
# --------------------------- SEARCH --------------------------------------- #
# -------------------------------------------------------------------------- #

@app.get("/search")
def get_search(request: Request):

    busqueda = request.query_params.get("busqueda")

    print(PCTRL, "Buscando:", busqueda)

    # detecta si la busqueda es None o vacia
    if not busqueda:
        print(PCTRL, "Busqueda vacia")
        return view.get_search_view(request, {})

    palabras = busqueda.strip().split()

    if all(p.startswith("#") for p in palabras):
        tipo_busqueda = "generos"
        genres = [p.lstrip("#") for p in palabras]

    else:
        primer_caracter = busqueda[0]

        if primer_caracter.isalpha():
            tipo_busqueda = "nombre"
            name = " ".join(palabras)

        elif primer_caracter.startswith("@"):
            tipo_busqueda = "fecha"
            date =  next((p[1:] for p in palabras if p.startswith("@")), None)
        else:
            print(PCTRL, "Busqueda no válida")
            return view.get_search_view(request, {})
    
    all_items = []

    if tipo_busqueda  == "nombre":
        songs = model.get_songs_by_titulo(name)
        artists = model.get_usuarios_by_nombre(name)
        albums = model.get_albums_by_titulo(name)

        for song in songs:
            all_items.append({"tipo": "Canción", "nombre": song["titulo"][:25] + "..." if len(song["titulo"]) > 25 else song["titulo"], "portada": song["portada"], "descripcion": song["descripcion"][:50] + "..." if len(song["descripcion"]) > 50 else song["descripcion"], "url": f"/song?id={song['id']}"})

        for artist in artists:
            all_items.append({"tipo": "Artista", "nombre": artist["nombre"][:25] + "..." if len(artist["nombre"]) > 25 else artist["nombre"], "portada": artist["imagen"], "descripcion": artist["bio"][:50] + "..." if len(artist["bio"]) > 50 else artist["bio"], "url": f"/artista?id={artist['id']}"})
        
        for album in albums:
            all_items.append({"tipo": "Álbum", "nombre": album["titulo"][:25] + "..." if len(album["titulo"]) > 25 else album["titulo"], "portada": album["portada"], "descripcion": album["descripcion"][:50] + "..." if len(album["descripcion"]) > 50 else album["descripcion"], "url": f"/album?id={album['id']}"})

    elif tipo_busqueda == "generos":
        songs = model.get_songs_by_genre(genres)
        albums = model.get_albums_by_genre(genres)
    
        for song in songs:
            all_items.append({"tipo": "Canción", "nombre": song["titulo"][:25] + "..." if len(song["titulo"]) > 25 else song["titulo"], "portada": song["portada"], "descripcion": song["descripcion"][:50] + "..." if len(song["descripcion"]) > 50 else song["descripcion"], "url": f"/song?id={song['id']}"})
        
        for album in albums:
            all_items.append({"tipo": "Álbum", "nombre": album["titulo"][:25] + "..." if len(album["titulo"]) > 25 else album["titulo"], "portada": album["portada"], "descripcion": album["descripcion"][:50] + "..." if len(album["descripcion"]) > 50 else album["descripcion"], "url": f"/album?id={album['id']}"})

    elif tipo_busqueda == "fecha":
        print(PCTRL, "Buscando por fecha:", date)
        songs = model.get_songs_by_fecha(date)
        artists = model.get_usuarios_by_fecha(date)
        albums = model.get_albums_by_fecha(date)

        for song in songs:
            all_items.append({"tipo": "Canción", "nombre": song["titulo"][:25] + "..." if len(song["titulo"]) > 25 else song["titulo"], "portada": song["portada"], "descripcion": song["descripcion"][:50] + "..." if len(song["descripcion"]) > 50 else song["descripcion"], "url": f"/song?id={song['id']}"})

        for artist in artists:
            all_items.append({"tipo": "Artista", "nombre": artist["nombre"], "portada": artist["imagen"], "descripcion": artist["bio"][:50] + "..." if len(artist["bio"]) > 50 else artist["bio"], "url": f"/artista?id={artist['id']}"})

        for album in albums:
            all_items.append({"tipo": "Álbum", "nombre": album["titulo"], "portada": album["portada"], "descripcion": album["descripcion"][:50] + "..." if len(album["descripcion"]) > 50 else album["descripcion"], "url": f"/album?id={album['id']}"})


    # list (dict (nombre, portada, descripcion))
    print(PCTRL, "Busqueda terminada")
    return view.get_search_view(request, all_items)


# -------------------------------------------------------------------------- #
# --------------------------- MÉTODOS AUXILIARES --------------------------- #
# -------------------------------------------------------------------------- #

# Este método automatiza la obtención de datos del usuario a partir de la sesión activa.
#
#   1º Comprueba que exista una sesión activa en memoria (caché) o en la base de datos
#   2º Descarga los datos del usuario enlazados a esa sesión
#   3º Devuelve dos cosas:
#       Si todo es correcto -> Devuelve user_info (dict) con la info del usuario
#       Si no -> Devuelve un Response con el error
#   Además, si la sesión ha caducado, la elimina de la caché, de la base de datos y responde con un Response con el error.
#
# Conveniente para rutas sencillas que solo requieran la info del usuario.
def verifySessionAndGetUserInfo(request : Request):

    # Obtenemos el id de la sesión del usuario desde la cookie
    session_id = request.cookies.get("session_id")
    if not session_id:
        print(PCTRL, "Usuario invitado (sin sesión activa) accediendo a:", request.method, request.url.path)
        return Response("No autorizado", status_code=401)

    # Comprobamos si la sesión está en caché (en memoria)
    if session_id not in sessions:
        # Si la sesión no está en caché, la buscamos en la base de datos
        print(PCTRL, "Un usuario intenta verificarse con una cookie con sesión fuera de caché, descargando sesión...")
        session_data = model.get_sesion(session_id)
        if not session_data:
            sessions[session_id] = "expired" # Añadimos la sesión como invitado a la caché
            print(PCTRL_WARN, "Usuario con cookie no válida (sesión no existe en caché/BD) accediendo a:", request.method, request.url.path + ". Registrada sesión como Invitado.")
            return Response("La sesión ha caducado. Debes iniciar sesión de nuevo.", status_code=401)
        else:
            # Si la sesión existe en la base de datos, la añadimos a la caché

            sessions[session_id] = session_data
    else:
        # Si la sesión está en caché, la obtenemos de ahí
        session_data = sessions[session_id]
    
    # Accedemos a los datos de la sesión del usuario
    if session_data:

        # Comprobamos si la sesión es de tipo expired
        if session_data == "expired":
            print(PCTRL_WARN, "Usuario invitado (con sesión caducada) accediendo a:", request.method, request.url.path)
            return Response("La sesión ha caducado. Debes iniciar sesión de nuevo.", status_code=401)
        
        # Comprobamos si la sesión ha caducado
        if session_data["caducidad"] < datetime.now():
            # Si ha caducado, la eliminamos de la caché y de la base de datos
            del sessions[session_id]
            model.delete_sesion(session_id)
            sessions[session_id] = "expired" # Añadimos la sesión como invitado a la caché
            print(PCTRL_WARN, "Usuario con cookie no válida (sesión caducada) accediendo a:", request.method, request.url.path + ". Su sesión se ha eliminado de la caché/BD y se ha registrado como Invitado.")
            return Response("La sesión ha caducado. Debes iniciar sesión de nuevo.", status_code=401)

        # Descargamos los datos del usuario en la base de datos
        user_id = session_data["user_id"]
        user_info = model.get_usuario(user_id) # Devuelve un dict del UsuarioDTO
        if user_info:
            print(PCTRL, "Usuario", user_info["email"], "solicitó acceso a los datos del usuario a través de:", request.method, request.url.path)
            return user_info
        else:
            print(PCTRL_WARN, "Usuario con id", user_id, "solicitó datos aunque:", request.method, request.url.path, ", but the user_id is not found in database! - Now assuming user is anonymous.")
    else:
        print(PCTRL, "Usuario con cookie válida solicitó datos a través de:", request.method, request.url.path, ", pero la sesión especificada no existe en el backend.")
    
    return Response("No autorizado", status_code=401)

# Valida los campos genéricos de un upload data su data = request.json()
def validate_fields(data) -> JSONResponse | bool:
    # Validar que los campos requeridos no estén vacíos y tengan el formato correcto
    required_fields = ["titulo", "artista", "generos", "portada", "precio"]
    for field in required_fields:
        if field not in data or data[field] is None:
            print(PCTRL_WARN, f"El campo '{field}' falta o está vacío")
            return JSONResponse(content={"error": f"El campo '{field}' es obligatorio y no puede estar vacío"}, status_code=400)
        
    # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
    optional_fields = ["descripcion", "colaboradores"]
    for field in optional_fields:
        if field not in data or data[field] is None:
            data[field] = ""

    # Validar que el precio sea un número positivo
    if not isinstance(data["precio"], (int, float)) or data["precio"] < 0:
        print(PCTRL_WARN, "El precio debe ser un número positivo")
        return JSONResponse(content={"error": "El precio debe ser un número positivo"}, status_code=400)

    # Validar que los géneros sean una lista no vacía
    if not isinstance(data["generos"], list) or not data["generos"]:
        print(PCTRL_WARN, "Los géneros deben ser una lista no vacía")
        return JSONResponse(content={"error": "Los géneros deben ser una lista no vacía"}, status_code=400)
    
    # Validar que el campo 'titulo' no exceda los 30 caracteres
    if len(data["titulo"]) > 30:
        print(PCTRL_WARN, "El campo 'titulo' excede los 30 caracteres")
        return JSONResponse(content={"error": "El titulo no debe exceder los 30 caracteres"}, status_code=400)

    # Validar que el campo 'artista' no exceda los 30 caracteres
    if len(data["artista"]) > 30:
        print(PCTRL_WARN, "El campo 'artista' excede los 30 caracteres")
        return JSONResponse(content={"error": "El artista no debe exceder los 30 caracteres"}, status_code=400)

    # Validar que el campo 'colaboradores' no exceda los 80 caracteres
    if len(data["colaboradores"]) > 80:
        print(PCTRL_WARN, "El campo 'colaboradores' excede los 80 caracteres")
        return JSONResponse(content={"error": "Los colaboradores no deben exceder los 80 caracteres"}, status_code=400)

    # Validar que el campo 'descripcion' no exceda los 500 caracteres
    if len(data["descripción"]) > 500:
        print(PCTRL_WARN, "El campo 'descripcion' excede los 500 caracteres")
        return JSONResponse(content={"error": "La descripción no debe exceder los 500 caracteres"}, status_code=400)
    
    return True # Si todo es correcto, devolvemos True

def validate_album_fields(data) -> JSONResponse | bool:
    return validate_fields(data)

def validate_song_fields(data) -> JSONResponse | bool:
    # Validar que el campo 'pista' tenga un archivo no vacío
    if not isinstance(data["pista"], str) or not data["pista"]:
        print(PCTRL_WARN, "La pista debe ser un archivo no vacío")
        return JSONResponse(content={"error": "La pista debe ser un archivo no vacío"}, status_code=400)

    return validate_fields(data)

def convert_datetime(obj):
    if isinstance(obj, list):
        return [convert_datetime(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj