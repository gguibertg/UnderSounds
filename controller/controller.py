import uuid
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from view.view import View
from model.model import Model
from pathlib import Path
import firebase_admin
from firebase_admin import auth, credentials
# Inicializamos la app

app = FastAPI()

# Inicializar Firebase
if not Path("credentials.json").is_file():
    print("\033[91mERROR: credentials.json file not found!\033[0m")
    exit(1)

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

# Almacenamiento en memoria para sesiones
sessions = {}

#Simulación de datos de usuarios
user_data = {}


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


view = View()
model = Model()

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


@app.post("/login")
async def login(data: dict, response: Response, provider: str):
    token = data.get("token")
    try:
        decoded_token = auth.verify_id_token(token)
        # Identificador único del usuario otorgado por Firebase
        # que podemos usar como identificador del usuario en nuestra base de datos
        print("User trying to log as: " + decoded_token)
        user_id = decoded_token["uid"]
        print("User user_id: " + user_id)
        print("User provider: " + provider)
        session_id = str(uuid.uuid4())
        #Faltaría asignar vigencia a la sesión
        sessions[session_id] = {"user_id": user_id, "type": provider}
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/login-credentials")
async def login_google(data: dict, response: Response):
    return await login(data, response, "credentials")


@app.post("/login-google")
async def login_google(data: dict, response: Response):
    return await login(data, response, "google")


@app.post("/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    print("User ending session with session_id: ", session_id)
    if session_id in sessions:
        del sessions[session_id]
    response.delete_cookie("session_id")
    return {"success": True}