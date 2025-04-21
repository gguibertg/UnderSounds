from bson import ObjectId
import pymongo
import pymongo.results
from ...intefaceListaDAO import InterfaceListaDAO
from ....dto.listaDTO import ListaDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Listas en MongoDB.
class mongodbListaDAO(InterfaceListaDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection

    def get_lista(self, id):
        lista = None

        try:
            query = self.collection.find_one({"_id": ObjectId(id)})

            if query:
                lista = ListaDTO()
                lista.set_id(str(query.get("_id")))  # Convertimos _id a str
                lista.set_titulo(query.get("titulo"))
                lista.set_descripcion(query.get("descripcion"))
                lista.set_lista_canciones(query.get("lista_canciones", []))
                lista.set_esPublico(query.get("esPublico", False))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar la lista: {e}")

        return lista.lista_to_dict() if lista else None
    

    def add_lista(self, lista: ListaDTO) -> str:
        try:
            lista_dict: dict = lista.lista_to_dict()
            lista_dict.pop("id", None)  # id debería estar vacío, así que lo descartamos
            result: pymongo.results.InsertOneResult = self.collection.insert_one(lista_dict)
            return str(result.inserted_id)  # Devolvemos el nuevo _id de la lista

        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar la lista: {e}")
            return None


    def update_lista(self, lista: ListaDTO) -> bool:
        try:
            lista_dict: dict = lista.lista_to_dict()
            lista_dict["_id"] = ObjectId(lista_dict.pop("id", None))  # Convertimos id a ObjectId
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": lista_dict["_id"]}, {"$set": lista_dict}
            )
            return result.modified_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar la lista: {e}")
            return False
    

    def delete_lista(self, id: str) -> bool:
        try:
            result: pymongo.results.DeleteResult = self.collection.delete_one({"_id": ObjectId(id)})  # Convertimos id a ObjectId
            return result.deleted_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar la lista: {e}")
            return False