import json
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from view.view import View
from model.model import Model
from pathlib import Path
import firebase_admin
from firebase_admin import auth, credentials

# Variable para el color + modulo de la consola
PCTRL = "\033[96mCTRL\033[0m:\t "
WARN = "\033[93mWARN\033[0m |"

# Inicializamos la app
app = FastAPI()

# Inicializar Firebase
if not Path("credentials.json").is_file():
    print("\033[91mERROR: credentials.json file not found!\033[0m")
    exit(1)
    
# Cargamos las credenciales de Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# TODO: CARGA DE DATOS DE PRUEBA, REEMPLAZAR CON DB REAL
with open("login-example.json", "r", encoding="utf-8") as f:
    user_data = json.load(f)

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
sessions = {}

# Cargamos los datos de usuarios desde el modelo
user_data = model.get_usuarios()


# ------------------ DEFINICIÓN DE RUTAS ------------------ #

# Con el decorador @app.get() le decimos a FastAPI que esta función se va a usar para manejar las peticiones GET a la ruta X.
# En este caso, la ruta es la raíz de la app ("/").
# La función index se va a usar para renderizar la template index.html.
@app.get("/")
# El objeto request es un objeto que contiene toda la información de la petición HTTP que se ha hecho al servidor.
def index(request: Request): 
    # Delegamos el trabajo de renderizar la template a la clase View.
    return view.get_index_view(request)


# En este caso servimos la template songs.html al cliente cuando se hace una petición GET a la ruta "/getsongs".
@app.get("/getsongs", description="Hola esto es una descripcion")
def getsongs(request: Request):
    # Vamos a llamar al Model para que nos devuelva la lista de canciones en formato JSON.
    songs = model.get_songs() # JSON
    # Luego se lo pasamos al View para que lo renderice y lo devuelva al cliente.
    return view.get_songs_view(request,songs)

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

        # Comprobar que el usuario existe en la base de datos (simulada)
        if not any(u["id"] == user_id for u in user_data):
            print(PCTRL, WARN, "User is logged into Firebase, but not registered in database! Logon failed")
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
        #TODO
        if True:
            print(PCTRL, "User already registered")
            return {"success": False, "error": "User already registered"}
        else:
            print(PCTRL, "User already registered")
            return {"success": False, "error": "User already registered"}
        
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

        # Verificar si el usuario existe en la base de datos (simulada)
        if any(user["id"] == user_id for user in user_data):
            try:
                # Eliminar al usuario de Firebase Auth
                auth.delete_user(user_id)
                print(PCTRL, "User", user_name, "deleted from Firebase Auth")

                # Eliminar al usuario de la base de datos (simulada) TODO
                #del user_data["usuarios"][user_id]
                #with open("login-example.json", "w", encoding="utf-8") as f:
                #    json.dump(user_data, f, indent=4)
                #print(PCTRL, "User", user_name, "deleted from local database")

                # Eliminar la sesión del usuario
                del sessions[session_id]
                response.delete_cookie("session_id")
                print(PCTRL, "User session", session_id, "destroyed")

                return {"success": True, "message": "User account deleted successfully"}
            except Exception as e:
                print(PCTRL, "Error deleting user:", str(e))
                return {"success": False, "error": str(e)}
        else:
            print(PCTRL, WARN, "User", user_name, "with id", user_id, "not found in database!")
            return {"success": False, "error": "User not found in database"}
    
    return Response("No autorizado", status_code=401)

# Ruta para cargar la vista de perfil (prueba)
@app.get("/profile")
async def perfil(request: Request):
    # Comprobamos si el usuario tiene una sesión activa
    session_id = request.cookies.get("session_id")
    if not isUserSessionValid(session_id):
        return Response("No autorizado", status_code=401)
    
    # Accedemos a los datos de la sesión del usuario
    session_data = getSessionData(session_id)
    if session_data:
        user_id = session_data["user_id"]
        user_name = session_data["name"]
        print(PCTRL, "User", user_name, "requested access to profile")

        # Accedemos a los datos del usuario en la base de datos (simulada)
        user_info = next((u for u in user_data if u["id"] == user_id), None)

        if user_info:
            return view.get_perfil_view(request, user_info)
        else:
            print(PCTRL, WARN, "User", user_name, "with id", user_id, "not found in database!")
        
    return Response("No autorizado", status_code=401)



# --------------------------- MÉTODOS AUXILIARES --------------------------- #
def isUserSessionValid(session_id : str):
    return session_id and session_id in sessions and any(user["id"] == sessions[session_id]["user_id"] for user in user_data
    )

# Un session contiene un name, 
def getSessionData(session_id: str):
    if session_id in sessions:
        return sessions[session_id]
    return None