import pymongo
import pymongo.results
from ...interfaceCarritoDAO import InterfaceCarritoDAO
from ....dto.articuloCestaDTO import ArticulosCestaDTO, ArticuloCestaDTO
from ....dto.articuloDTO import ArticuloDTO
from ....dto.artistaDTO import ArtistaDTO
from bson import ObjectId

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección del Carrito en MongoDB.
class mongodbCarritoDAO(InterfaceCarritoDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_articulos(self):
        articulos = ArticulosCestaDTO()
        try:
            # Filtramos los artículos que pertenecen a un usuario específico
            query = self.collection.find()

            for doc in query:
                articulo_cesta_dto = ArticuloCestaDTO()
                articulo_cesta_dto.set_id(str(doc.get("_id")))

                articulo_dto = ArticuloDTO(**doc.get("articulo"))
                artista_dto = ArtistaDTO(**doc.get("artista"))

                articulo_cesta_dto.set_articulo(articulo_dto)
                articulo_cesta_dto.set_artista(artista_dto)
                articulo_cesta_dto.set_cantidad(doc.get("cantidad"))
                articulo_cesta_dto.set_usuario(doc.get("usuario"))

                articulos.insertArticuloCesta(articulo_cesta_dto)
                
        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los articulos: {e}")

        return [articulo.articulocestadto_to_dict() for articulo in articulos.articulosCestaList]

    def insertArticulo(self, articulo) -> bool:
        try:
            articulo_dict : dict = articulo.articulocestadto_to_dict()
            articulo_dict["_id"] = articulo_dict.pop("id", None)
            result : pymongo.results.InsertOneResult = self.collection.insert_one(articulo_dict)
            return result.inserted_id == articulo_dict["_id"]
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el usuario: {e}")
            return False
        
    def deleteArticulo(self, id) -> bool:
        try:
            result : pymongo.results.DeleteResult = self.collection.delete_one({"id": id})
            return result.deleted_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar el articulo: {e}")
            return False        

    def incrementArticulo(self, id) -> bool:
        try:
            # Realiza una actualización incremental del campo 'cantidad' en +1
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$inc": {"cantidad": 1}}
            )
            return result.modified_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el artículo: {e}")
            return False

    def decrementArticulo(self, id) -> bool:
        try:
            # Solo decrementa si la cantidad actual es mayor a 0
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": ObjectId(id), "cantidad": {"$gt": 0}},
                {"$inc": {"cantidad": -1}}
            )
            return result.modified_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el artículo: {e}")
            return False

        
        

    