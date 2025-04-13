from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from model.dto.songDTO import SongDTO, SongsDTO
from view.view import View
from model.model import Model
from pathlib import Path
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

@app.get("/")
def index(request: Request): 
    return view.get_index_view(request)


# Continuamos añadiendo funciones para manejar las peticiones a las rutas que se necesiten...