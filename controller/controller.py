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
from model.dao.mongodb.mongodb_dao_factory import MongodbDAOFactory
from model.dto.faq_dto import FaqDTO, FaqsDTO

# Instancia principal de la app
app = FastAPI()

# Archivos estáticos

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

# Inicialización de vista, modelo y DAO
view = View()
model = Model()
dao_factory = MongodbDAOFactory()
faq_dao = dao_factory.get_dao_faq()

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


# Continuamos añadiendo funciones para manejar las peticiones a las rutas que se necesiten...

# ! Descomentar el siguiente bloque para usar MongoDB
# @app.get("/faqs")
# def get_faqs(request: Request):
#     """
#     Muestra la vista con la lista de preguntas frecuentes.

#     :param request: Objeto Request
#     :return: Vista faqs.html renderizada con datos de MongoDB
#     """
#     faqs = faq_dao.get_all_faqs()
#     container = FaqsDTO()
#     for faq in faqs:
#         container.insert_faq(faq)
#     return view.get_faqs_view(request, faqs_raw)

# ! Descomentar el siguiente bloque para usar JSON local hasta que se implemente MongoDB
# Una vez que se implemente MongoDB, este bloque se puede eliminar junto con la carpeta data y el import de json.

@app.get("/faqs", description="Muestra FAQs desde JSON para pruebas.")
def get_faqs(request: Request):
    """
    Endpoint que carga las preguntas frecuentes desde un archivo JSON local
    y las pasa a la plantilla HTML para su visualización.

    :param request: Objeto de solicitud HTTP
    :return: Plantilla HTML renderizada con los datos cargados desde JSON
    """
    # Ruta del archivo JSON (ajusta si es necesario)
    json_path = Path("data/faqs.json")

    # Leer y cargar los datos JSON
    with open(json_path, encoding="utf-8") as f:
        faqs_raw = json.load(f)

    # Convertir a objetos FaqDTO
    faqs_container = FaqsDTO()
    for entry in faqs_raw:
        faq = FaqDTO()
        faq.set_question(entry.get("question"))
        faq.set_answer(entry.get("answer"))
        faqs_container.insert_faq(faq)

    # Renderizar vista
    return view.get_faqs_view(request, faqs_raw)
