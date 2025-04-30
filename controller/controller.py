# Imports estándar de Python
import base64
import json
import re
import uuid
from datetime import datetime
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
    return view.get_index_view(request, song_json, genres_json, tipoUsuario)

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
async def login_post(data: dict, response: Response, provider: str):
    token = data.get("token")
    try:

        # Verificamos el token de Firebase dado por el usuario
        decoded_token = auth.verify_id_token(token, None, False, 3)
        # Identificador único del usuario otorgado por Firebase que podemos usar como identificador del usuario en nuestra base de datos
        user_id = decoded_token["uid"]
        user_email = decoded_token["email"]
        print(PCTRL, "Inicio de sesión del usuario:")
        print(PCTRL, "\tCorreo del usuario: ", user_email)
        print(PCTRL, "\tID del usuario: ", user_id)
        print(PCTRL, "\tProveedor del usuario: ", provider)

        # Comprobar que el usuario existe en la base de datos
        usuario_db = model.get_usuario(user_id)

        if not usuario_db:
            # Eliminar al usuario de Firebase Auth
            auth.delete_user(user_id)
            print(PCTRL_WARN, "El usuario está registrado en Firebase, pero no está registrado en la base de datos. Inicio de sesión fallido")
            return JSONResponse(content={"error": "El usuario no está registrado en la base de datos"}, status_code=400)

        # Verificar si el correo electrónico ha cambiado en Firebase
        if usuario_db["email"] != user_email:
            print(PCTRL, "El correo electrónico en Firebase y MongoDB difieren. Actualizando MongoDB...")
            usuario_dto = UsuarioDTO()
            usuario_dto.load_from_dict(usuario_db)
            usuario_dto.set_email(user_email)
            success = model.update_usuario(usuario_dto)
            print(PCTRL, "Correo electrónico actualizado en MongoDB" if success else f"{PCTRL_WARN} Error al actualizar el correo electrónico en MongoDB")

        # Creamos una sesión para el usuario
        session_id = str(uuid.uuid4())
        # Faltaría asignar vigencia a la sesión
        sessions[session_id] = {"name": user_email, "user_id": user_id, "type": provider}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        print(PCTRL, "Inicio de sesión exitoso")
        return { "success" : True }

    except Exception as e:
        print("El inicio de sesión falló debido a", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ruta para procesar la petición de login con credenciales clásicas
@app.post("/login-credentials")
async def login_credentials(data: dict, response: Response):
    return await login_post(data, response, "credentials")

# Ruta para procesar la petición de login con credenciales de Google
@app.post("/login-google")
async def login_google(data: dict, response: Response):
    return await login_post(data, response, "google")

# Ruta para procesar la petición de logout
@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    print(PCTRL, "La sesión del usuario", session_id, "está cerrando sesión")
    if session_id in sessions:
        del sessions[session_id]
    print(PCTRL, "La sesión del usuario", session_id, "ha sido destruida")
    response.delete_cookie("session_id")
    return JSONResponse(content={"success": True}, status_code=200)

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
        print(PCTRL, "Usuario registrándose:")
        print(PCTRL, "\tNombre de usuario: ", username)
        print(PCTRL, "\tCorreo del usuario: ", user_email)
        print(PCTRL, "\tID del usuario: ", user_id)
        print(PCTRL, "\tProveedor del usuario: ", provider)

        # Registrar usuario en la base de datos
        # Verificar si el usuario ya está registrado en la base de datos
        if model.get_usuario(user_id):
            print(PCTRL, "El usuario ya está registrado en la base de datos")
            return JSONResponse(content={"error": "El usuario ya está registrado"}, status_code=400)

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
            print(PCTRL, "Usuario registrado en la base de datos")
        else:
            print(PCTRL_WARN, "¡El registro del usuario falló en la base de datos!")
            return JSONResponse(content={"error": "El registro del usuario falló"}, status_code=500)
        
        # Creamos una sesión para el usuario (login)
        session_id = str(uuid.uuid4())
        #Faltaría asignar vigencia a la sesión
        sessions[session_id] = {"name": user_email, "user_id": user_id, "type": provider}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        print(PCTRL, "Inicio de sesión exitoso")
        return JSONResponse(content={"success": True}, status_code=200)
        
    except Exception as e:
        print("El registro del usuario falló debido a", str(e))
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

    print(PCTRL, "El usuario", res["email"], "solicitó la eliminación de su cuenta") 

    try:
        # Eliminar al usuario de Firebase Auth
        auth.delete_user(res["id"])
        print(PCTRL, "El usuario", res["email"], "fue eliminado de Firebase Auth")

        # Eliminar cada una de las canciones en studio_canciones de la base de datos
        for song_id in res["studio_canciones"]:
            if model.delete_song(song_id):
                print(PCTRL, "La canción", song_id, "fue eliminada de la base de datos")
            else:
                print(PCTRL_WARN, "La canción", song_id, "no fue eliminada de la base de datos - omitiendo")
        
        # Eliminar cada uno de los álbumes en studio_albumes de la base de datos
        for album_id in res["studio_albumes"]:
            if model.delete_album(album_id):
                print(PCTRL, "El álbum", album_id, "fue eliminado de la base de datos")
            else:
                print(PCTRL_WARN, "El álbum", album_id, "no fue eliminado de la base de datos - omitiendo")

        # Eliminar al usuario de la base de datos
        if model.delete_usuario(res["id"]):
            print(PCTRL, "El usuario", res["email"], "fue eliminado de la base de datos")
        else:
            print(PCTRL_WARN, "El usuario", res["email"], "no fue eliminado de la base de datos - omitiendo")

        # Eliminar la sesión del usuario
        session_id = request.cookies.get("session_id")
        del sessions[session_id]
        response.delete_cookie("session_id")
        print(PCTRL, "La sesión del usuario", session_id, "fue destruida")

        print(PCTRL, "La cuenta del usuario fue eliminada exitosamente")
        return JSONResponse(content={"success": True, "message": "La cuenta del usuario fue eliminada exitosamente"}, status_code=200)
    
    except Exception as e:
        print(PCTRL, "Error al eliminar al usuario:", str(e))
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
            print(PCTRL_WARN, f"El campo '{field}' falta o está vacío")
            return JSONResponse(content={"error": f"El campo '{field}' es obligatorio y no puede estar vacío"}, status_code=400)
    
    # Si alguno de los campos opcionales está a None, lo inicializamos a una cadena vacía
    optional_fields = ["url", "bio"]
    for field in optional_fields:
        if field not in data or data[field] is None:
            data[field] = ""

    # Validar que el email tenga el formato correcto
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        print(PCTRL_WARN, "Formato de correo electrónico inválido")
        return JSONResponse(content={"error": "Formato de correo electrónico inválido"}, status_code=400)

    # Validar que el campo nombre no exceda los 30 caracteres
    if len(data["nombre"]) > 30:
        print(PCTRL_WARN, "El nombre excede los 30 caracteres")
        return JSONResponse(content={"error": "El nombre excede los 30 caracteres"}, status_code=400)
    
    # Validar que el campo email no exceda los 50 caracteres
    if len(data["email"]) > 50:
        print(PCTRL_WARN, "El correo electrónico excede los 50 caracteres")
        return JSONResponse(content={"error": "El correo electrónico excede los 50 caracteres"}, status_code=400)
    
    # Validar que el campo bio no exceda los 300 caracteres
    if len(data["bio"]) > 300:
        print(PCTRL_WARN, "La biografía excede los 300 caracteres")
        return JSONResponse(content={"error": "La biografía excede los 300 caracteres"}, status_code=400)
    
    # Validar que el campo url no exceda los 100 caracteres
    if len(data["url"]) > 100:
        print(PCTRL_WARN, "La URL excede los 100 caracteres")
        return JSONResponse(content={"error": "La URL excede los 100 caracteres"}, status_code=400)

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
        print(PCTRL, "Usuario", user.get_email(), "actualizado en la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "Usuario", user.get_email(), "no actualizado en la base de datos")
        return JSONResponse(content={"error": "El usuario no se actualizó en la base de datos"}, status_code=500)
    
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
        print(PCTRL_WARN, "El usuario no es un artista")
        return Response("No autorizado", status_code=403)
    
    # Preparamos para escoger las canciones válidas para un álbum nuevo
    # Para ello, debemos coger todas las canciones creadas por el usuario (campo studio_canciones) y que no pertenezcan a ningún álbum.
    # Para comprobar que no pertenezcan a ningún álbum, debemos descargar todos los álbumes y comprobar en el campo canciones de cada uno de ellos que esa canción no esté.
    # Debemos recordar que tanto studio_canciones como studio_albumes como el campo canciones de un álbum son listas de IDs de strings de canciones, álbumes y canciones respectivamente.
    # Por lo tanto, para cada string encontrado hay que hacer su llamada a model correspondiente para obtener el objeto real y pasarlo a la vista.
    # Excepto en el caso de las canciones de un álbum, ya que solo necesitamos el ID y nada más.
    
    # Por cada canción en studio_canciones, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción creada por el usuario", song_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)

    # Por cada álbum en studio_albumes, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum creado por el usuario", album_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)

    # Comprobar que por cada canción en studio_canciones, no esté en el campo canciones de ningún álbum
    # Cada canción que cumpla esta condición se añadirá a la lista de canciones admitidas para el nuevo álbum
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
        print(PCTRL_WARN, "El usuario no es un artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Creamos un nuevo objeto AlbumDTO, utilizando los datos recibidos en el request
    data = await request.json()

    # Validar campos
    validation_result = validate_album_fields(data)
    if validation_result is not True:
        return validation_result

    album = AlbumDTO()
    album.set_titulo(data["titulo"])
    album.set_autor(data["autor"])
    album.set_colaboradores(data["colaboradores"])
    album.set_descripcion(data["descripcion"])
    album.set_fecha(datetime.now()) # La fecha se calcula desde el lado del servidor
    album.set_generos(data["generos"])
    album.set_canciones(data["canciones"])
    album.set_visitas(0)
    album.set_portada(data["portada"])
    album.set_precio(data["precio"])
    album.set_likes(0)
    album.set_visible(data["visible"])

    # Subir el álbum a la base de datos
    album_id = model.add_album(album)
    if album_id is not None:
        print(PCTRL, "Álbum", album_id, "subido a la base de datos")
    else:
        print(PCTRL_WARN, "Álbum", album_id, "no subido a la base de datos")
        return JSONResponse(content={"error": "Error del sistema"}, status_code=500)

    try:
        # Por cada una de las canciones en el álbum, actualizamos su campo álbum con el id del nuevo álbum
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Canción", song_id, "no encontrada en la base de datos")
                raise Exception(f"Canción {song_id} no encontrada en la base de datos")
            
            # Actualizamos el campo álbum de la canción con el id del nuevo álbum
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Canción", song_id, "no actualizada en la base de datos")
                raise Exception(f"Canción {song_id} no actualizada en la base de datos")

        # Obtenemos los datos de usuario de la base de datos y creamos un nuevo objeto UsuarioDTO
        user = UsuarioDTO()
        user.load_from_dict(res)

        # Añadimos al usuario la nueva referencia al álbum
        user.add_studio_album(album_id)

        # Actualizamos el usuario en la base de datos
        if model.update_usuario(user):
            print(PCTRL, "Usuario", user.get_email(), "actualizado en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            raise Exception("Usuario no actualizado en la base de datos")
        
    except Exception as e:
        print(PCTRL_WARN, "Error:", str(e))

        # Intentar destruir el álbum subido
        model.delete_album(album_id)
        print(PCTRL_WARN, "Álbum", album_id, "eliminado de la base de datos")

        # Intentar revertir los cambios en las canciones
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "Canción", song_id, "no encontrada en la base de datos")
            
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "Canción", song_id, "no actualizada en la base de datos")

        # Intentar revertir los cambios en el usuario
        user = UsuarioDTO()
        user.load_from_dict(res)
        user.remove_studio_album(album_id)
        if model.update_usuario(user):
            print(PCTRL, "Usuario", user.get_email(), "actualizado en la base de datos")
        else:
            print(PCTRL_WARN, "Usuario", user.get_email(), "no actualizado en la base de datos")

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
        print(PCTRL_WARN, "El álbum no existe")
        return Response("No autorizado", status_code=403)

    # Obtenemos los datos del usuario y comprobamos qué tipo de usuario es
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        tipoUsuario = 0 # Invitado
    else:
        if album_id in res["studio_albumes"]:
            tipoUsuario = 3 # Artista (creador)

        elif all(song_id in res["biblioteca"] for song_id in album_info["canciones"]):
            tipoUsuario = 2 # Propietario (Usuario o Artista)

        else:
            tipoUsuario = 1 # Miembro (Usuario)

    # Antes de nada, verificamos si el álbum es visible o no. Si no lo es, no se puede ver... Excepto si el usuario es el autor del álbum.
    if not album_info["visible"] and tipoUsuario != 3:
            print(PCTRL_WARN, "El álbum no es visible y el usuario no es el autor")
            return Response("No autorizado", status_code=403)
        
    # Incrementar el contador de visitas del álbum, excepto si el usuario es el autor del álbum.
    if tipoUsuario != 3:
        album_info["visitas"] += 1
        album_object = AlbumDTO()
        album_object.load_from_dict(album_info)
        if not model.update_album(album_object):
            print(PCTRL_WARN, "El álbum", album_id, "no se actualizó en la base de datos")
            return Response("Error del sistema", status_code=403)

    # Descargamos las canciones del álbum de la base de datos vía su ID en el campo canciones y las insertamos en este album_info
    print(PCTRL, "Comenzando a poblar el álbum con canciones...")
    canciones_out : list[dict] = []
    for cancion_id in album_info["canciones"]:
        cancion = model.get_song(cancion_id)
        if not cancion:
            print(PCTRL_WARN, "La canción", cancion_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        
        # Convertimos los géneros de cada canción a un string sencillo
        # Primero, descargamos todos los géneros, escogemos su nombre, lo añadimos al string, y luego lo metemos en cancion["generosStr"]
        # Esto se hace por cada canción del álbum.
        print(PCTRL, "Convirtiendo los géneros de la canción a string...")
        generosStr = ""
        for genero_id in cancion["generos"]:
            genero = model.get_genero(genero_id)
            if not genero:
                print(PCTRL_WARN, "El género", genero_id ,"no se encontró en la base de datos")
                return Response("Error del sistema", status_code=403)
            generosStr += genero["nombre"] + ", "
        generosStr = generosStr[:-2] # Quitamos la última coma y espacio
        cancion["generosStr"] = generosStr # Añadimos el string a la canción

        canciones_out.append(cancion)

    album_info["canciones"] = canciones_out


    # Convertimos los géneros del álbum a un string sencillo
    # Primero, descargamos todos los géneros, escogemos su nombre, lo añadimos al string, y luego lo metemos en album_info["generosStr"]
    print(PCTRL, "Convirtiendo los géneros del álbum a string...")
    generosStr = ""
    for genero_id in album_info["generos"]:
        genero = model.get_genero(genero_id)
        if not genero:
            print(PCTRL_WARN, "El género", genero_id ,"no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        generosStr += genero["nombre"] + ", "
    generosStr = generosStr[:-2] # Quitamos la última coma y espacio
    album_info["generosStr"] = generosStr # Añadimos el string al álbum

    
    # Comprobamos si el usuario le ha dado like al álbum mirando si el id del álbum está en id_likes del usuario.
    isLiked = False
    if tipoUsuario > 0:
        isLiked = album_id in res["id_likes"]
    
    # Comprobamos finalmente si el usuario (en caso de estar logeado) tiene un carrito activo el cual contiene el álbum.
    inCarrito = False
    if tipoUsuario > 0:
        carrito = model.get_carrito(res["id"]) 
        if carrito:
            for item in carrito["articulos"]:
                if item["id"] == album_id:
                    inCarrito = True
                    break
        else:
            print(PCTRL_WARN, "El carrito no se encontró en la base de datos - omitiendo")

    # Donde tipo Usuario:
    # 0 = Invitado
    # 1 = Usuario
    # 2 = Propietario (Usuario o Artista)
    # 3 = Artista (creador)
    return view.get_album_view(request, album_info, tipoUsuario, isLiked, inCarrito) # Devolvemos la vista del álbum

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
        print(PCTRL_WARN, "ID del álbum no proporcionado en la solicitud")
        return Response("No autorizado", status_code=400)

    # Verificar si el usuario tiene una sesión activa, si es artista y si el álbum existe, y si le pertenece.
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es un artista")
        return Response("No autorizado", status_code=403)
    album_info = model.get_album(album_id)
    if not album_info:
        print(PCTRL_WARN, "El álbum no existe")
        return Response("No autorizado", status_code=403)
    if album_id not in res["studio_albumes"]:
        print(PCTRL_WARN, "El álbum no se encuentra en los álbumes del usuario")
        return Response("No autorizado", status_code=403)

    # Ahora popularemos el álbum reemplazando las IDs (referencias) por los objetos reales
    canciones_out : list[dict] = []
    for cancion_id in album_info["canciones"]:
        cancion = model.get_song(cancion_id)
        if not cancion:
            print(PCTRL_WARN, "La canción", cancion_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)   
        canciones_out.append(cancion)
    album_info["canciones"] = canciones_out

    # Ya tenemos el álbum preparado. Pero ahora, tenemos que emular básicamente la misma funcionalidad que en upload-album, para que el artista pueda editar el álbum con nuevas canciones.
    # Así pues, copiamos y pegamos el código de upload-album para obtener las canciones válidas para un álbum nuevo.

    # Por cada canción en studio_canciones, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)

    # Por cada álbum en studio_albumes, obtenemos el objeto real, enviando un mensaje de error si no existe.
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum", album_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)

    # Comprobar que por cada canción en studio_canciones, no esté en el campo canciones de ningún álbum
    # Cada canción que cumpla esta condición se añadirá a la lista de canciones admitidas para el nuevo álbum
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
        print(PCTRL_WARN, "ID del álbum no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID del álbum no proporcionado"}, status_code=400)

    # Verificar si el usuario tiene una sesión activa, si es artista y si el álbum existe, y si le pertenece.
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es un artista")
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

        # Validar campos
        validation_result = validate_album_fields(data)
        if validation_result is not True:
            return validation_result

        # Editamos el álbum con los nuevos datos recibidos en la solicitud
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
        
        # Por cada una de las canciones en el álbum, actualizamos su campo álbum con el id del nuevo álbum
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos")
                raise Exception(f"La canción {song_id} no se encontró en la base de datos")
            
            # Actualizamos el campo álbum de la canción con el id del nuevo álbum
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se actualizó en la base de datos")
                raise Exception(f"La canción {song_id} no se actualizó en la base de datos")

        # Actualizamos el álbum en la base de datos
        if model.update_album(album):
            print(PCTRL, "Álbum", album_id, "actualizado en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            raise Exception(f"El álbum {album_id} no se actualizó en la base de datos")
    
    except Exception as e:
        # Intentamos revertir los cambios en el álbum
        album_object = AlbumDTO()
        album_object.load_from_dict(album_dict)
        if model.update_album(album_object):
            print(PCTRL, "Álbum", album_id, "revertido en la base de datos")
        else:
            print(PCTRL_WARN, "Álbum", album_id, "no revertido en la base de datos")

        # Intentar revertir los cambios en las canciones
        for song_id in album.get_canciones():
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos")
            
            # Actualizamos el campo álbum de la canción con el id del nuevo álbum
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(None)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se actualizó en la base de datos")

        # Intentamos asociar las canciones del álbum antiguo a su álbum original
        for song_id in album_dict["canciones"]:
            song = model.get_song(song_id)
            if not song:
                print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos")
            
            # Actualizamos el campo álbum de la canción con el id del nuevo álbum
            song_object = SongDTO()
            song_object.load_from_dict(song)
            song_object.set_album(album_id)
            if not model.update_song(song_object):
                print(PCTRL_WARN, "La canción", song_id, "no se actualizó en la base de datos")

        print(PCTRL_WARN, "Error al procesar el álbum", album_id, ", la actualización en la base de datos falló")
        return JSONResponse(content={"error": "Error del sistema"}, status_code=500)

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
        print(PCTRL_WARN, "ID del álbum no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID del álbum no proporcionado"}, status_code=400)
    
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
            print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos - omitiendo")
            continue
        
        # Actualizamos el campo album de la canción con el id del nuevo album
        song_object = SongDTO()
        song_object.load_from_dict(song)
        song_object.set_album(None)
        if not model.update_song(song_object):
            print(PCTRL_WARN, "La canción", song_id, "no se actualizó en la base de datos - omitiendo")
            continue

    # Luego, borramos el álbum del studio_albumes del usuario
    user = UsuarioDTO()
    user.load_from_dict(res)
    user.remove_studio_album(album_id)
    if not model.update_usuario(user):
        print(PCTRL_WARN, "El usuario", user.get_email(), "no se actualizó en la base de datos")
        return JSONResponse(content={"error": "El usuario no se actualizó en la base de datos"}, status_code=500)
    
    # Por último, borramos el álbum de la base de datos
    if model.delete_album(album_id):
        print(PCTRL, "Álbum", album_id, "eliminado de la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "Álbum", album_id, "no eliminado de la base de datos")
        return JSONResponse(content={"error": "El álbum no se eliminó de la base de datos"}, status_code=500)
        
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
        print(PCTRL_WARN, "ID del álbum no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID del álbum no proporcionado"}, status_code=400)
    
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
            print(PCTRL_WARN, "¡Error al actualizar los likes del álbum en la base de datos!")
            return JSONResponse(content={"error": "Error al actualizar el álbum en la base de datos"}, status_code=500)
    else:
        print(PCTRL_WARN, "¡Álbum no encontrado en la base de datos!")
        return JSONResponse(content={"error": "Álbum no encontrado en la base de datos"}, status_code=404)

    if model.update_usuario(user_object):
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "¡Error al actualizar el usuario en la base de datos!")
        return JSONResponse(content={"error": "Error al actualizar el usuario en la base de datos"}, status_code=500)

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
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res
    
    form_data = await request.form()
    action = form_data.get("action")  # Por defecto: añadir
    item_id = form_data.get("item_id")
    
    if request.method == "POST":

        carrito_json = model.get_carrito(res["id"])
        if not carrito_json:
            print(PCTRL_WARN, "¡Carrito no encontrado en la base de datos! - omitiendo")
            return JSONResponse(content={"error": "Carrito no encontrado en la base de datos"}, status_code=500)
        
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
                    print(PCTRL_WARN, "¡Carrito no encontrado en la base de datos! - omitiendo")
                    return JSONResponse(content={"error": "Carrito no encontrado en la base de datos"}, status_code=500)
                    
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
        print(PCTRL_WARN, "¡Carrito no encontrado en la base de datos! - omitiendo")
        return JSONResponse(content={"error": "Carrito no encontrado en la base de datos"}, status_code=500)
        
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

    return view.get_prepaid_view(request, carrito_json)


# -------------------------------------------------------------- #
# ----------------------------- TPV ---------------------------- #
# -------------------------------------------------------------- #

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
            print(PCTRL, "Usuario", user.get_nombre(), "actualizado en la base de datos")
        else:
            print(PCTRL_WARN, "Usuario", user.get_nombre(), "no actualizado en la base de datos!")
            return JSONResponse(content={"error": "El usuario no se actualizó en la base de datos"}, status_code=500)

        if model.vaciar_carrito(res["id"]):
            print(PCTRL, "Carrito vaciado en la base de datos")
        else:
            print(PCTRL_WARN, "Actualización del carrito fallida")
            return JSONResponse(content={"error": "La actualización del carrito falló"}, status_code=500)
            
    except Exception as e:
        print(PCTRL_WARN, "Error al procesar el TPV, la base de datos falló con el error:", str(e))
        return JSONResponse(content={"error": "El carrito y el usuario no se actualizaron en la base de datos"}, status_code=500)

    return view.get_tpv_view(request)

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
    
    # Validar que el nombre, el email y teléfono no excedan los 50 caracteres
    if len(data.get("name")) > 50 or len(data.get("email")) > 50 or len(data.get("telf")) > 50:
        return JSONResponse(content={"error": "Formulario inválido"}, status_code=400)

    # Validar que el mensaje no exceda los 300 caracteres
    if len(data.get("msg")) > 300:
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
        print(PCTRL_WARN, "El usuario no es un artista")
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
        print(PCTRL_WARN, "El usuario no es un artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Registrar la canción en la base de datos
    data = await request.json()

    # Validar los campos de la canción
    validation_result = validate_song_fields(data)
    if validation_result is not True:
        return validation_result

    song = SongDTO()
    song.set_titulo(data["titulo"])
    song.set_artista(data["artista"])
    song.set_colaboradores(data["colaboradores"])
    song.set_fecha(datetime.now())
    song.set_descripcion(data["descripcion"])
    song.set_generos(data["generos"])
    song.set_likes(0)
    song.set_visitas(0)
    song.set_portada(data["portada"])
    song.set_precio(data["precio"])
    song.set_lista_resenas([])
    song.set_visible(data["visible"])
    song.set_album(None) 
    song.set_pista(data["pista"])
    duracion = data["duracion"]
    minutos = duracion / 60
    segundos = duracion % 60
    tiempo = f"{int(minutos):02d}:{int(segundos):02d}"
    song.set_duracion(tiempo)

    try:
        song_id = model.add_song(song)

        if song_id is not None:
            print(PCTRL, "Canción registrada en la base de datos")
        else:
            print(PCTRL_WARN, "¡El registro de la canción falló en la base de datos!")
            return JSONResponse(content={"error": "El registro de la canción falló"}, status_code=500)

        # Convertimos res en un objeto UsuarioDTO, le añadimos la nueva canción a studio_canciones y lo actualizamos en la base de datos
        user = UsuarioDTO()
        user.load_from_dict(res)
        user.add_studio_cancion(song_id)
        user.add_song_to_biblioteca(song_id)
        if model.update_usuario(user):
            print(PCTRL, "Usuario", user.get_email(), "actualizado en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            print(PCTRL_WARN, "¡Usuario", user.get_email(), "no actualizado en la base de datos!")
            raise Exception("Usuario no actualizado en la base de datos")

    except Exception as e:
        print(PCTRL_WARN, "Error al procesar la canción", song_id, ", ¡falló al añadirla a la base de datos!")
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
    
    # Comprobamos qué tipo de usuario es
    if isinstance(user_db, Response):
        tipoUsuario = 0 # Invitado
    else:
        if song_id in user_db["studio_canciones"]:
            tipoUsuario = 3 # Artista (creador)

        elif song_id in user_db["biblioteca"]:
            tipoUsuario = 2 # Propietario (Usuario o Artista)

        else:
            tipoUsuario = 1 # Miembro (Usuario)

    # Descargamos la canción de la base de datos vía su ID y comprobamos si existe.
    song_info = model.get_song(song_id)
    if not song_info:
        print(PCTRL_WARN, "La canción no existe")
        return Response("No existe", status_code=403)
    
    # Antes de hacer nada, comprobamos si la canción es visible o no. Si no es visible, solo el artista creador puede verla.
    if not song_info["visible"] and tipoUsuario != 3:
            print(PCTRL_WARN, "La canción no es visible y el usuario no es el creador")
            return Response("No autorizado", status_code=403)
        
    # Incrementar el contador de visitas de la canción, excepto si el usuario es el autor de la canción.
    if tipoUsuario != 3:
        song_info["visitas"] += 1
        song_object = SongDTO()
        song_object.load_from_dict(song_info)
        if not model.update_song(song_object):
            print(PCTRL_WARN, "La canción", song_id, "no se actualizó en la base de datos")
            return Response("Error del sistema", status_code=403)

    # Convertimos los géneros de la canción a un string sencillo
    # Primero, descargamos todos los géneros, escogemos su nombre, lo añadimos al string, y luego lo metemos en song_info["generosStr"]
    generosStr = ""
    for genero_id in song_info["generos"]:
        genero = model.get_genero(genero_id)
        if not genero:
            print(PCTRL_WARN, "El género", genero_id ,"no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        generosStr += genero["nombre"] + ", "
    generosStr = generosStr[:-2] # Quitamos la última coma y espacio
    song_info["generosStr"] = generosStr

    # Descargamos el álbum asociado a la canción, extraemos su nombre y lo insertamos en el campo albumStr de la canción.
    # Si no tiene álbum, dejamos albumStr como None.
    if song_info["album"]:
        album = model.get_album(song_info["album"])
        if not album:
            print(PCTRL_WARN, "El álbum", song_info["album"], "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        song_info["albumStr"] = album["titulo"]
    else:
        song_info["albumStr"] = None

    # Comprobamos si el usuario le ha dado like a la canción mirando si el id de la canción está en id_likes del usuario.
    isLiked = False
    if tipoUsuario > 0:
        isLiked = song_id in user_db["id_likes"]

    # Donde tipo Usuario:
    # 0 = Invitado
    # 1 = Usuario
    # 2 = Propietario (Usuario o Artista)
    # 3 = Artista (creador)

    # Comprobamos finalmente si el usuario (en caso de estar logeado) tiene un carrito activo el cual contiene la canción.
    inCarrito = False
    if tipoUsuario > 0:
        carrito = model.get_carrito(user_db["id"]) 
        if carrito:
            for item in carrito["articulos"]:
                if item["id"] == song_id:
                    inCarrito = True
                    break
        else:
            print(PCTRL_WARN, "El carrito no se encontró en la base de datos - omitiendo")
        
    return view.get_song_view(request, song_info, tipoUsuario, user_db, isLiked, inCarrito) # Devolvemos la vista de la canción

# Ruta para cargar vista edit-song
@app.get("/edit-song")
async def get_edit_song(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return res # Si es un Response, devolvemos el error  
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es un artista")
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
    if not song_info:
        print(PCTRL_WARN, "La canción no existe")
        return Response("No autorizado", status_code=403)
    if song_id not in res["studio_canciones"]:
        print(PCTRL_WARN, "La canción no se encuentra en las canciones del usuario")
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
        print(PCTRL_WARN, "El usuario no es un artista")
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
            print(PCTRL_WARN, "La canción no se encuentra en las canciones del usuario")
            return JSONResponse(content={"error": "No autorizado"}, status_code=403)
        
        # Validación de los campos de la canción
        validation_result = validate_song_fields(data)
        if validation_result is not True:
            return validation_result
    
        song = SongDTO()
        song.load_from_dict(song_dict)

        song.set_titulo(data["titulo"])
        song.set_artista(data["artista"])
        song.set_colaboradores(data["colaboradores"])
        #song.set_fecha(datetime.now()) # La fecha no se puede editar.
        song.set_descripcion(data["descripcion"])
        song.set_generos(data["generos"])
        song.set_portada(data["portada"])
        song.set_precio(data["precio"])
        song.set_visible(data["visible"])

        # Actualizamos el song en la base de datos
        if model.update_song(song):
            print(PCTRL, "Canción", song_id, "actualizada en la base de datos")
            return JSONResponse(content={"success": True}, status_code=200)
        else:
            print(PCTRL_WARN, "Canción", song_id, "no actualizada en la base de datos")
            return JSONResponse(content={"error": "La canción no se actualizó en la base de datos"}, status_code=500)
    
    except Exception as e:
        print(PCTRL_WARN, "Error al procesar la canción", song_id, ", la actualización en la base de datos falló")
        return JSONResponse(content={"error": "La canción no se actualizó en la base de datos"}, status_code=500)

# Ruta para eliminar una canción
@app.post("/delete-song")
async def delete_song_post(request: Request):
    # Verificar si el usuario tiene una sesión activa y es artista 
    res = verifySessionAndGetUserInfo(request)
    if isinstance(res, Response):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    if not res["esArtista"]:
        print(PCTRL_WARN, "El usuario no es un artista")
        return JSONResponse(content={"error": "No autorizado"}, status_code=403)
    
    # Obtenemos el ID de la canción a eliminar desde la request
    data = await request.json()
    song_id = data.get("id")
    if not song_id:
        print(PCTRL_WARN, "ID de la canción no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID de la canción no proporcionado"}, status_code=400)
    
    # Verificamos que la canción existe y pertenece al usuario
    song = model.get_song(song_id)
    if not song:
        print(PCTRL_WARN, "La canción no existe")
        return JSONResponse(content={"error": "La canción no existe"}, status_code=404)
    if song_id not in res["studio_canciones"]:
        print(PCTRL_WARN, "La canción no se encuentra en las canciones del usuario")
        return JSONResponse(content={"error": "La canción no se encuentra en las canciones del usuario"}, status_code=403)
    
    # Procedemos a la eliminación de la canción
    # Primero, descargaremos el álbum al que pertenece la canción, y eliminaremos la canción de su campo canciones.
    # Si no pertenece a ningún álbum, no haremos nada.
    if song["album"] is not None:
        album = model.get_album(song["album"])
        if not album:
            print(PCTRL_WARN, "El álbum no existe")
            return JSONResponse(content={"error": "El álbum no existe"}, status_code=404)
        album_object = AlbumDTO()
        album_object.load_from_dict(album)
        album_object.remove_cancion(song_id)
        if not model.update_album(album_object):
            print(PCTRL_WARN, "El álbum", album["id"], "no se actualizó en la base de datos")
            return JSONResponse(content={"error": "El álbum no se actualizó en la base de datos"}, status_code=500)
    
    # Luego, borramos la canción del studio_canciones del usuario
    user = UsuarioDTO()
    user.load_from_dict(res)
    user.remove_studio_cancion(song_id)
    if not model.update_usuario(user):
        print(PCTRL_WARN, "El usuario", user.get_email(), "no se actualizó en la base de datos")
        return JSONResponse(content={"error": "El usuario no se actualizó en la base de datos"}, status_code=500)
    
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
        print(PCTRL, "Archivo MP3 eliminado:", mp3_path)
    else:
        print(PCTRL_WARN, "Archivo MP3 no encontrado:", mp3_path)

    # Por último, borramos la canción de la base de datos
    if model.delete_song(song_id):
        print(PCTRL, "Canción", song_id, "eliminada de la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "Canción", song_id, "no eliminada de la base de datos")
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
        print(PCTRL_WARN, "ID de la canción no proporcionado en la solicitud")
        return JSONResponse(content={"error": "ID de la canción no proporcionado"}, status_code=400)
    
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
            print(PCTRL_WARN, "¡Error al actualizar los likes de la canción en la base de datos!")
            return JSONResponse(content={"error": "Error al actualizar la canción en la base de datos"}, status_code=500)
    else:
        print(PCTRL_WARN, "¡Canción no encontrada en la base de datos!")
        return JSONResponse(content={"error": "Canción no encontrada en la base de datos"}, status_code=404)

    if model.update_usuario(user_object):
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "¡Error al actualizar el usuario en la base de datos!")
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
        print(PCTRL_WARN, "El usuario no es un artista")
        return Response("No autorizado", status_code=403)
    
    # Descargamos los álbumes y canciones del usuario
    user_albums_objects = []
    for album_id in res["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum", album_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_albums_objects.append(album)
    
    # Descargamos las canciones del usuario
    user_songs_objects = []
    for song_id in res["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        user_songs_objects.append(song)
    
    # Buscamos por cada canción descargada si su id está en el campo canciones de algún álbum.
    # Si es así, reemplazamos el campo álbum de esa canción por el NOMBRE del álbum.
    # Si no, lo introducimos en su lugar None
    for song in user_songs_objects:
        found = False
        for album in user_albums_objects:
            if song["id"] in album["canciones"]:
                song["album"] = album["titulo"]
                found = True
                print(PCTRL, "La canción", song["titulo"], "se encontró en el álbum", album["titulo"])
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
        print(PCTRL_WARN, "El usuario no es un artista")
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
        print(PCTRL, "Usuario", user_object.get_email(), "actualizado en la base de datos")
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        print(PCTRL_WARN, "Usuario", user_object.get_email(), "no actualizado en la base de datos")
        return JSONResponse(content={"error": "El usuario no se actualizó en la base de datos"}, status_code=500)

# --------------------------------------------------------------- #
# ---------------------------- ARTISTA -------------------------- #
# --------------------------------------------------------------- #

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
            print(PCTRL_WARN, "El artista no es visible y el usuario no es el creador")
            return Response("No autorizado", status_code=403)
        
    # Descargamos los álbumes del artista
    user_albums_objects = []
    for album_id in artista_info["studio_albumes"]:
        album = model.get_album(album_id)
        if not album:
            print(PCTRL_WARN, "El álbum", album_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        # Solo si el álbum es visible lo añadimos a la lista
        if album["visible"]:
            user_albums_objects.append(album)

    # Descargamos todas las canciones del artista
    user_songs_objects = []
    for song_id in artista_info["studio_canciones"]:
        song = model.get_song(song_id)
        if not song:
            print(PCTRL_WARN, "La canción", song_id, "no se encontró en la base de datos")
            return Response("Error del sistema", status_code=403)
        # Solo si la canción es visible lo añadimos a la lista
        if song["visible"]:
            user_songs_objects.append(song)

    # Filtramos qué canciones son singles y las guardamos en una lista.
    # Los singles son canciones que en su campo álbum tienen el valor None.
    singles = []
    for song in user_songs_objects:
        if song["album"] is None:
            singles.append(song)


    if isinstance(res, Response):
        tipoUsuario = 0 # Invitado
    else:
        if artista_id == res["id"]:
            tipoUsuario = 3 # Artista (creador)
        else:
            tipoUsuario = 1

    # Donde tipo Usuario:
    # 0 = Invitado
    # 1 = Usuario
    # x
    # 3 = Artista (creador)
    return view.get_artista_view(request, artista_info, singles, user_albums_objects, user_songs_objects, tipoUsuario)

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
            print(PCTRL, "Reseña registrada en la base de datos")
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
        print(PCTRL_WARN, "ERROR al añadir reseña:", e)
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
                print(PCTRL, "Reseña eliminada de la canción", song_id)
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo eliminar la reseña de la canción."})

            if model.delete_reseña(reseña_id):
                return JSONResponse(status_code=200, content={"message": "Reseña eliminada correctamente."})
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
                return JSONResponse(status_code=500, content={"error": "No puedes actualizar una reseña que no te pertenece."})

            song_dict = model.get_song(song_id)
            song = SongDTO()
            song.load_from_dict(song_dict)

            reseña = ReseñaDTO()
            reseña.load_from_dict(reseña_data)
            reseña.set_titulo(str(titulo))
            reseña.set_reseña(str(texto))
            song.update_resenas(reseña.reseñadto_to_dict())

            if model.update_song(song):
                print(PCTRL, "Reseña actualizada en la canción", song_id)
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo actualizar la reseña en la canción."})

            if model.update_reseña(reseña):
                return JSONResponse(status_code=200, content={"message": "Reseña actualizada correctamente."})
            else:
                return JSONResponse(status_code=500, content={"error": "No se pudo actualizar la reseña."})

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
        
        
# -------------------------------------------------------------------------- #
# --------------------------- RADIO ---------------------------------------- #
# -------------------------------------------------------------------------- #
        
@app.get("/play", response_class=HTMLResponse)
def play(request: Request):
    return view.get_play_view(request)

# -------------------------------------------------------------------------- #
# --------------------------- SEARCH --------------------------------------- #
# -------------------------------------------------------------------------- #

@app.get("/search")
def get_search(request: Request):
    return view.get_search_view(request, {})

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
            all_items.append({"tipo": "Artista", "nombre": artist["nombre"][:25] + "..." if len(artist["nombre"]) > 25 else artist["nombre"], "portada": artist["imagen"], "descripcion": artist["bio"][:50] + "..." if len(artist["bio"]) > 50 else artist["bio"], "url": f"/artista?id={artist['id']}"})

        for album in albums:
            all_items.append({"tipo": "Álbum", "nombre": album["titulo"][:25] + "..." if len(album["titulo"]) > 25 else album["titulo"], "portada": album["portada"], "descripcion": album["descripcion"][:50] + "..." if len(album["descripcion"]) > 50 else album["descripcion"], "url": f"/album?id={album['id']}"})


    # list (dict (nombre, portada, descripcion))
    print(PCTRL, "Busqueda terminada")
    return view.get_search_view(request, all_items)


# -------------------------------------------------------------------------- #
# --------------------------- MÉTODOS AUXILIARES --------------------------- #
# -------------------------------------------------------------------------- #

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
    if not (session_id and session_id in sessions):
        print(PCTRL, "Usuario anónimo solicitó datos a través de:", request.method, request.url.path)
        return Response("No autorizado", status_code=401)
    
    # Accedemos a los datos de la sesión del usuario
    session_data = getSessionData(session_id)
    if session_data:
        user_id = session_data["user_id"]
        # Accedemos a los datos del usuario en la base de datos
        user_info = model.get_usuario(user_id) # Devuelve un dict del UsuarioDTO

        if user_info:
            print(PCTRL, "El usuario", user_info["email"], "solicitó acceso a los datos del usuario a través de:", request.method, request.url.path)
            return user_info
        else:
            print(PCTRL_WARN, "El usuario con id", user_id, "solicitó datos a través de:", request.method, request.url.path, ", pero el user_id no se encuentra en la base de datos. Asumiendo ahora que el usuario es anónimo.")
    else:
        print(PCTRL, "Usuario anónimo solicitó datos a través de:", request.method, request.url.path, ", pero la sesión especificada no existe en el backend.")

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
        print(PCTRL_WARN, "Pista must be a non-empty file")
        return JSONResponse(content={"error": "La pista debe ser un archivo no vacío"}, status_code=400)

    return validate_fields(data)





from datetime import datetime
# TODO: Esta función probablemente es innecesaria si se optimiza en donde se usa, pero la dejo por si acaso
def convert_datetime(obj):
    if isinstance(obj, list):
        return [convert_datetime(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

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
