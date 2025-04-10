"""
Controlador de rutas web para FastAPI.
Conecta los datos con las vistas, siguiendo el patrón MVC.
"""

import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from view.view import View
from model.model import Model
from model.dto.faq_dto import FaqDTO, FaqsDTO

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
    """
    Renderiza la página principal (index).
    """
    return view.get_index_view(request)

@app.get("/getsongs", description="Listado de canciones")
def getsongs(request: Request):
    """
    Muestra la vista con la lista de canciones (si está implementado en el modelo).
    """
    songs = model.get_songs()
    return view.get_songs_view(request, songs)

@app.get("/faqs", description="Muestra preguntas frecuentes desde MongoDB")
def get_faqs(request: Request):
    """
    Muestra la vista con la lista de preguntas frecuentes almacenadas en MongoDB.

    :param request: Objeto Request
    :return: Plantilla HTML renderizada con los datos de MongoDB
    """
    faqs_json = model.get_faqs()
    return view.get_faqs_view(request, faqs_json)
