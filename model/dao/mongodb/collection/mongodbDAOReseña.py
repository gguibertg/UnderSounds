import pymongo
import pymongo.results
from bson import ObjectId
from ...interfaceReseñaDAO import InterfaceReseñaDAO
from ....dto.reseñasDTO import ReseñaDTO, ReseñasDTO
from ....dto.songDTO import SongDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbReseñaDAO(InterfaceReseñaDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection

    def get_all_reseñas_song(self, song: SongDTO):
        reseñas = ReseñasDTO()
        try:
            query = song.get_lista_resenas()

            for doc in query:
                reseña_dto = ReseñaDTO()
                reseña_dto.set_id(str(doc.get_id("id")))
                reseña_dto.set_reseña(doc.get_reseña("reseña"))
                reseña_dto.set_usuario(doc.get_usuario("usuario"))
               
                reseñas.insertReseña(reseña_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las reseñas: {e}")

        return [reseña.reseñadto_to_dict() for reseña in reseñas.reseñalist]

    def get_reseña(self, id):
        reseña = None

        try:
            query = self.collection.find_one({"_id": ObjectId(id)})

            if query:
                reseña = ReseñaDTO()
                reseña.set_id(str(query.get("_id")))
                reseña.set_reseña(query.get("reseña"))
                reseña.set_usuario(query.get("usuario"))
                
        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar el género: {e}")

        return reseña.reseñadto_to_dict if reseña else None
    
    def get_reseña_song(self, id, song: SongDTO):
        reseña_dict = self.get_reseña(id) 

        reseña = ReseñaDTO()
        reseña.load_from_dict(reseña_dict)
        
        if reseña in song.lista_resenas:
            return reseña.reseñadto_to_dict
    
    def add_reseña(self, reseña: ReseñaDTO) -> str:
        # Insertar reseña en colección Mongo
        try:
            reseña_dict : dict = reseña.reseñadto_to_dict()
            reseña_dict.pop("id", None)
            result : pymongo.results.InsertOneResult = self.collection.insert_one(reseña_dict)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el usuario: {e}")
            return None
            

    def update_reseña(self, reseña: ReseñaDTO) -> bool:
        try:
            reseña_dict = reseña.reseñadto_to_dict()
            reseña_id = reseña_dict.pop("id")
            reseña_dict["_id"] = ObjectId(reseña_id)  # importante

            result : pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": ObjectId(reseña_id)},  # usa ObjectId aquí también
                {"$set": reseña_dict}
            )
            return result.modified_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el usuario: {e}")
            return False
    

    def delete_reseña(self, id: str) -> bool:
        try:
            result : pymongo.results.DeleteResult = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar el usuario: {e}")
            return False