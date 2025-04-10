from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="view/templates") 

class View():

    def __init__(self): 
        pass

    def get_index_view(self, request: Request): 
        return templates.TemplateResponse("main/index.html", {"request" : request})

    def get_faqs_view(self, request: Request, faqs):
        return templates.TemplateResponse("main/faqs.html", {
            "request": request,
            "faqs": faqs
        })
