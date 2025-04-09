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


# Inicializamos la app
app = FastAPI()

# Inicializar Firebase
if not Path("credentials.json").is_file():
    print("\033[91mERROR: credentials.json file not found!\033[0m")
    exit(1)
    
# Cargamos las credenciales de Firebase
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# Almacenamiento en memoria para sesiones
sessions = {}

## TODO: CARGA DE DATOS DE PRUEBA, REEMPLAZAR CON DB REAL
user_data = {}

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
async def login(data: dict, response: Response, provider: str):
    token = data.get("token")
    try:
        decoded_token = auth.verify_id_token(token)
        # Identificador único del usuario otorgado por Firebase
        # que podemos usar como identificador del usuario en nuestra base de datos
        user_id = decoded_token["uid"]
        user_email = decoded_token["email"]
        print(PCTRL, "User login:")
        print(PCTRL, "\tUser email: ", user_email)
        print(PCTRL, "\tUser user_id: ", user_id)
        print(PCTRL, "\tUser provider: ", provider)
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
async def login_google(data: dict, response: Response):
    return await login(data, response, "credentials")

# Ruta para procesar la petición de login con credenciales de Google
@app.post("/login-google")
async def login_google(data: dict, response: Response):
    return await login(data, response, "google")

# Ruta para procesar la petición de logout
@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    print(PCTRL, "User session", session_id, "requested logout")
    if session_id in sessions:
        del sessions[session_id]
    response.delete_cookie("session_id")
    print(PCTRL, "User session terminated")
    return {"success": True}

# Ruta para cargar la vista de perfil (prueba)
@app.get("/perfil")
async def perfil(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id or session_id not in sessions:
        return Response("No autorizado", status_code=401)
    
    if session_id in sessions:
        user_id = sessions[session_id]["user_id"]
        user_name = sessions[session_id]["name"]
        print(PCTRL, "User", user_name, "requested access to profile")
        user_info = user_data["usuarios"].get(user_id)
        if user_info:
            return view.get_perfil_view(request, user_info)
        else:
            print(PCTRL, "User", user_name, "with id", user_id, "not found in user_data")
        
    return Response("No autorizado", status_code=401)






def pctrl(msg : str):
    print("\033[96mCTRL\033[0m:\t ", msg)