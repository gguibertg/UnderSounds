from bson import ObjectId
import pymongo
import pymongo.results
from model.dao.intefaceContactoDAO import InterfaceContactoDAO
from model.dto.contactoDTO import ContactoDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbContactoDAO(InterfaceContactoDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection

    def add_contacto(self, contacto: ContactoDTO) -> str:
        try:
            contacto_dict: dict = contacto.contacto_to_dict()
            contacto_dict.pop("id", None)  # id debería estar vacío, así que lo descartamos
            result: pymongo.results.InsertOneResult = self.collection.insert_one(contacto_dict)
            return str(result.inserted_id)  # Devolvemos el nuevo _id del álbum

        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el álbum: {e}")
            return None