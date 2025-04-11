from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from view.view import View
# from model.model import Model
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
#model = Model()


@app.get("/")
def index(request: Request): 
    return view.get_index_view(request)

@app.get("/about")
def about(request: Request):
    return view.get_about_view(request)
