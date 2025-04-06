from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from view.view import View
from model.model import Model
from pathlib import Path
from fastapi.responses import JSONResponse
# Inicializamos la app

app = FastAPI()

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


# Carga la página contact.html
@app.get("/contact")
def index(request: Request): 
    # Delegamos el trabajo de renderizar la template a la clase View.
    return view.get_contact_view(1)


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
        return view.get_contact_view(1)
    else:
        return view.get_contact_view(-1)