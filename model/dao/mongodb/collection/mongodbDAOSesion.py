
from bson import ObjectId
import pymongo
import pymongo.results
from ...intefaceSesionDAO import InterfaceSesionDAO
from ....dto.sesionDTO import SesionDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbSesionDAO(InterfaceSesionDAO):

    def __init__(self, collection):
        self.collection = collection

    def get_all_sesiones(self) -> list[dict]:
        sesiones = []
        try:
            query = self.collection.find()
            for item in query:
                sesion = SesionDTO()
                sesion.set_id(str(item.get("_id")))
                sesion.set_name(item.get("name"))
                sesion.set_user_id(item.get("user_id"))
                sesion.set_type(item.get("type"))
                sesion.set_caducidad(item.get("caducidad"))
                sesiones.append(sesion.to_dict())
        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las sesiones: {e}")
        return sesiones

    def get_sesion(self, id: str) -> dict:
        sesion = None
        try:
            query = self.collection.find_one({"_id": ObjectId(id)})
            if query:
                sesion = SesionDTO()
                sesion.set_id(str(query.get("_id")))
                sesion.set_name(query.get("name"))
                sesion.set_user_id(query.get("user_id"))
                sesion.set_type(query.get("type"))
                sesion.set_caducidad(query.get("caducidad"))
        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar la sesión: {e}")
        return sesion.to_dict() if sesion else None

    def add_sesion(self, sesion: SesionDTO) -> str | None:
        try:
            s_dict = sesion.to_dict()
            s_dict.pop("id", None) # Eliminar el campo "id" si existe, no lo necesitamos, se genera en MongoDB uno nuevo.
            result: pymongo.results.InsertOneResult = self.collection.insert_one(s_dict)
            return str(result.inserted_id)  # Devolvemos el nuevo _id de la sesión

        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar la sesión: {e}")
            return None

    def update_sesion(self, sesion: SesionDTO) -> bool:
        try:
            s_dict = sesion.to_dict()
            s_dict["_id"] = ObjectId(s_dict.pop("id", None))
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": s_dict["_id"]}, {"$set": s_dict})
            return result.matched_count == 1
        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar la sesión: {e}")
            return False

    def delete_sesion(self, id: str) -> bool:
        try:
            result: pymongo.results.DeleteResult = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count == 1
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar la sesión: {e}")
            return False