
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from view.view import View
from model.model import Model
from model.dto.faqDTO import FaqDTO, FaqsDTO

# Instancia principal de la app
app = FastAPI()

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

@app.get("/")
def index(request: Request):
    return view.get_index_view(request)

@app.get("/getsongs", description="Listado de canciones")
def getsongs(request: Request):
    songs = model.get_songs()
    return view.get_songs_view(request, songs)

@app.get("/faqs", description="Muestra preguntas frecuentes desde MongoDB")
def get_faqs(request: Request):
    faqs_json = model.get_faqs()
    return view.get_faqs_view(request, faqs_json)
