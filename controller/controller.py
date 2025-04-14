import uuid

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from view.view import View
from model.model import Model
from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials
from model.dto.usuarioDTO import UsuarioDTO

# Variable para el color + modulo de la consola
PCTRL = "\033[96mCTRL\033[0m:\t "
PCTRL_WARN = "\033[96mCTRL\033[0m|\033[93mWARN\033[0m:\t "



# ===============================================================================
# ========================= INICIALIZACIÓN DE LA APP ============================
# ===============================================================================

# Inicializamos la app
from model.dto.faqDTO import FaqDTO, FaqsDTO

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

# ----------------------------- LOGIN ------------------------------ #

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


# ----------------------------- REGISTER ------------------------------ #

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
            user.set_imagen("data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wgARCACqAKoDASIAAhEBAxEB/8QAHAABAAIDAQEBAAAAAAAAAAAAAAYHAgQFAwEI/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEAMQAAABiIAAAAAAAAAAAAAADfkpC1i+RX6TRwwPhnj2uKAAAAAZ2LsTIxyABzOmKV8bipMksS9u8RsAAADu8KxSegAAAV5YfAKc29QAAAALPrCyCdEKJqABHNvI6nN6keKeAAAAAmEUyL7aO8RTzl/kRzRlm0RiTgrSbUseYAAABmdrjSfjmxa9I/S/VaykkLh65JOfGq7NjnAAAAAB6/PMbOs6p092Q75D/s93Cv8Ak2z4lBujzgAAAAABbdb3cfQAAROqf0DSpyAAAAADMsac6u0AAAIjLsCgG5pgAAACURexieAAAAArqBW7UQAB/8QAKhAAAgEEAQMDAgcAAAAAAAAAAgQDAAEFMAYSEyAQERQhNRUiIyQzNFD/2gAIAQEAAQUC/wBwhuN9qykzN4sBOVW47aj49emMK3FRDcb+mYHof1gNyLG4QRsI2G3g6jA4OSRkSlWdmWtnWrnPrwOP7Mfm6sDa7ERQzXIpjkx3Shpwy3yndPKFva9d79pp4tH+XTnQ68Xr4v8A1PN7LRKzjfqHKfbtfFi/Tr4LpZfwyD8aYmivNNWek7eM18am6HfR2F2BmPOw0WdStV8o03WPxnal9OTs9c+qKMpZIZCilSZBpf0OMJKFaEfDJOCktIZSHqw0ZXyZgQ3xj8iUqbkLYeLrcScTzcjk+oDKM8S+yWRncZnvIBRmEhAWNyzXuOUCvxOGiylqlyM5WYOU5dkRlFIBkEjM5sTUpH24fUV5irKITRx78cobbAYw6DGRWoU4BoREfSaMZYn1iUZ3cfV7CXlyFPvq7cav8py30t5X+tZVX4jmzi63TDo5Ir3VNYDczVhtAvoMbGLkF1mdXHYO7kNXKF/Y9XFP49XIftfj/8QAFBEBAAAAAAAAAAAAAAAAAAAAYP/aAAgBAwEBPwFz/8QAFBEBAAAAAAAAAAAAAAAAAAAAYP/aAAgBAgEBPwFz/8QANxAAAgADBAgEBAQHAAAAAAAAAQIAAxESITBBBBATIjEyUXEgI2GBQnKRoRRiscFAQ1BSU4KS/9oACAEBAAY/Av65RhQ43ky2f1yjzHlp94v0g/8AMbmkD3WKhBMH5DFCCD0OqmcOPyr+mIAoqTkID6Ze3+PIRRQAOg8NJq35MOIiy96nlbrFJRWgNb1BixYl2Simtm/64g0iaPMblH9owGlTM8+kPLmcymhhbbVNy1MCZtJFu2akTLqUwkVuQbzYUvSBnuN+2rYU+O3X2wp79lwp/oLWJN+f9sDZFWY50ygEZxpPyHE0hfUHVtjMpKDVray6U8K13pjcEECfMleZqm9W3cQof5i/fWdJ0NtoDzSjFnSZcyS/SkXM57LFnQNFb53j8RpT7bSDn01pIXgl7d8NUS9jwhXTmU1ELNTPiOh1+Yit3EbsmWP9fAXN7cFHUwzuasxqThyKq3Hp6QbSkU9Iqt6HmXrFqS3cZjxW5p7DMwZkz2HTDDISrDgRElZk92VjQgmGSZOdgTywyOKMtxEBkYhhmIImUmKOvGN6Ww7Rwf6Ruyz7mDYspBM9iz+uKroaMpqIDqaMDWsNNm8x1CvE3+Ddlt9I27JQcD/AWUFaXmN91HaN5maLpY943QBqaW4qrChh5TZcD1GOHYb83e9svHtkHmSvuMaXKyrVu2C8v4OK9sV9IPFt1e2DtlG9K/TECrzE0ES5S8FFMEq3A3GJko/CaYYY8ssWvfDl6QM9xsPSPmGHM7j9fF//xAAqEAEAAQMBBwQCAwEAAAAAAAABEQAhMTAQQVFhcYGRILHB0aHwQFDh8f/aAAgBAQABPyH+8TsDcmqE1DOWCB3o4eSEuoOfyP3Ue8/fc0Ggm+54aSmOQhNmbLrBUyCMsPTqKkRAF1oxt8D8nGg5HgID0wF9K71cnnS3+qHg2G6dUmo+CxRvJ0xejsn3P0l0AEthvLc0OUVgosgLABY7Vd2AAKwBz5aQjp8MbvOkAv8ARL32cNj46NIrO8h76QzskOzTnT7n6tCDBxUHAhJRmb9inOnNwnmH+bHFcQ9KAl8jMedDrUCi+5sPl0936mnOmTq0B0X+9rm/+M0WyOVI+6L7KvzVqQbbo+K4olK507RRSPeYPHvpgXJgUy0E6xSO2HuBtOgHlNJShyJURtjjWmTEM4h0gVgJasghLda6gZNQzCuoavkc6gxXe26h6nMfg5eBTAxuPB4abDznIKubGyMVkQPNs8KRk6RuaxYESEpDY2THlTPzAadx433W/wD7FAmBZCfehU+yudW6GQ4NLHjA3NIwOeMbLAb9tCcX6VmX4UaiMXTs/wAApFG+wRS/wqayRdYrNt7q/CIRss6kOVXSpT4h17WF5y3Hz39eYFz3T51ljr+w5oAAQG71gCJI7qg4u876xqwFu9hn8+2jB3FLzefvUOeRBzawYPq0QMk0OJWQuM8Tc+NOGU/CD95acbbHuZPnTBPF/g0yM5ik59P/2gAMAwEAAgADAAAAEPPAAAAAAAAAMAABDDABKAAAABPHPLLDAAAAFPPPPLGAAAAEOPPKLKAAAADPGAPNAAAAFKAMNKIAAAAAEIHJPAAAAAAADPPPHAAAAABPPPPLKAAAAFPPPPPDAAP/xAAUEQEAAAAAAAAAAAAAAAAAAABg/9oACAEDAQE/EHP/xAAUEQEAAAAAAAAAAAAAAAAAAABg/9oACAECAQE/EHP/xAAmEAEAAQMDAwUBAQEAAAAAAAABEQAhMTBBUXGBoRBhkbHBIEDR/9oACAEBAAE/EP8AS/5JqdaIH0xkkkt0TVTAmooKYe6DtRx9zEPo81FyvZjzQSldiPzRyC2XhPxNO6WGFe439EfagLquAKvqIZJv+R1AwcnCsAc0FZrp8ky9sdaI+MAA4AsfyxaJHwBuPZkoRkzGCbJsNymokCzlgMbNBiGnxPVwvEGmJXsF14KOZehy4eh8FudCzU5Is8PufUlTIYLZTCeyQnWrdhNhoF2BvVsS5RBVhmLC8OljI12XIXWB0mgAAINGJ/mhlBU7A7HpK/iUrjdh5nRaKu69wArynxpFAlR4TfqaMPTj1mdAFjdJgS2vli8VNpEmIYSSiBCK31Gk4o5O557KejLOmGxx9xZm2/8AJQoattY6D7bFKEAVEgRchTHagAgsUZLHVqU+FLlpwGmzOVh49QjyJ8jBtm/aE96ZwdbJ8fIpQq+4PhUxja+7w7r0pmeq5V9WX3sGweuBeU7fgu02bCwiWF/KnI2eEx0cUC62kuWX3HxD6mgzAb5KDA2Fr6oAAADAetzc0t4rdjK8dSlZoNlGV0gSksAStBsuRIhcWOYpJ8QaCOLlKgmA8AHwHmjIWTdvj9C3v/QWZSMHgH7g3rn6O6d78u7205IoKheRp5npMCotzIU0Cxk3ANhi1OVDlAyVcIY/0yUaWbaC4IZ3yNBElvA/lBLp4goEZXZIeJp+JUScdmf+KdrE1RGxwdNVb5QyYMNYFVvZJkpvqjBAAgA4re+KewOpk4Ox6s4KuBLUaju6h8sVIxSxkmyA82+Kba5MpagA2F939qNTNx35goEelB8H7UcjN5PzQsD8H9PQEbTd1+1MyJgZ7/g+46xm+N6uzEnLwfR/ZiwFwX/Gw6PNJDbG2q4Ezg2ufLHehDCgBAHH9iWBCiROKVCEnd2sd09mplirF8uee462aK4Q6IvYHsx2NJCmmigpN0g+6BsjKbgu92XvojXdHCEJ8NTTykdXvI079xOcSs+V01jucBslXtDsadhkhmLxO2m4AqxTDC5WTr/P/9k=")
        else:
            user.set_imagen(decoded_token["picture"])
        user.set_url("")
        user.set_esArtista(False) #TODO, como deberíamos determinar si es artista o no?

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
    # Verificar si el usuario tiene una sesión activa
    session_id = request.cookies.get("session_id")
    if not isUserSessionValid(session_id):
        return Response("No autorizado", status_code=401)

    # Obtener los datos de la sesión del usuario
    session_data = getSessionData(session_id)
    if session_data:
        user_id = session_data["user_id"]
        user_name = session_data["name"]
        print(PCTRL, "User", user_name, "requested account deletion")

        # Verificar si el usuario existe en la base de datos
        if model.get_usuario(user_id):
            try:
                # Eliminar al usuario de Firebase Auth
                auth.delete_user(user_id)
                print(PCTRL, "User", user_name, "deleted from Firebase Auth")

                # Eliminar al usuario de la base de datos
                if model.delete_usuario(user_id):
                    print(PCTRL, "User", user_name, "deleted from database")
                else:
                    print(PCTRL_WARN, "User", user_name, "not deleted from database!")
                    return {"success": False, "error": "User not deleted from database"}

                # Eliminar la sesión del usuario
                del sessions[session_id]
                response.delete_cookie("session_id")
                print(PCTRL, "User session", session_id, "destroyed")

                return {"success": True, "message": "User account deleted successfully"}
            except Exception as e:
                print(PCTRL, "Error deleting user:", str(e))
                return {"success": False, "error": str(e)}
        else:
            print(PCTRL_WARN, "User", user_name, "with id", user_id, "not found in database!")
            return {"success": False, "error": "User not found in database"}
    
    return Response("No autorizado", status_code=401)


# ----------------------------- PERFIL ------------------------------ #

# Ruta para cargar la vista de perfil
@app.get("/profile")
async def perfil(request: Request):
    res = handleAndGetUserDictDBData(request)
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

# -------------------------------- INCLUDES -------------------------------- #
@app.get("/header")
def header(request: Request):
    res = handleAndGetUserDictDBData(request)
    if isinstance(res, Response):
        return view.get_header_view(request, None) # Si es un Response, devolvemos la vista de guest
    
    return view.get_header_view(request, res)  # Si es un dict, pasamos los datos del usuario



# --------------------------- MÉTODOS AUXILIARES --------------------------- #

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

# --------------------------- FAQS --------------------------- #

@app.get("/faqs", description="Muestra preguntas frecuentes desde MongoDB")
def get_faqs(request: Request):
    faqs_json = model.get_faqs()
    return view.get_faqs_view(request, faqs_json)
