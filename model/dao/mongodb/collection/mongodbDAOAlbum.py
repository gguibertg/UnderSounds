import pymongo
import pymongo.results
from ...intefaceAlbumDAO import InterfaceAlbumDAO
from ....dto.albumDTO import AlbumDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbAlbumDAO(InterfaceAlbumDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection

    def get_album(self, id):
        album = None

        try:
            query = self.collection.find_one({"_id": id})

            if query:
                album = AlbumDTO()
                album.set_id(query.get("_id"))
                album.set_titulo(query.get("titulo"))
                album.set_autor(query.get("autor"))
                album.set_descripcion(query.get("descripcion"))
                album.set_fecha(query.get("fecha"))
                album.set_generos(query.get("generos", []))
                album.set_canciones(query.get("canciones", []))
                album.set_nVisualizaciones(query.get("nVisualizaciones"))
                album.set_portada(query.get("portada"))
                album.set_precio(query.get("precio"))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar el álbum: {e}")

        return album.album_to_dict() if album else None
    

    def add_album(self, album: AlbumDTO) -> bool:
        try:
            album_dict: dict = album.album_to_dict()
            album_dict["_id"] = album_dict.pop("id", None)
            result: pymongo.results.InsertOneResult = self.collection.insert_one(album_dict)
            return result.inserted_id == album_dict["_id"]

        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el álbum: {e}")
            return False


    def update_album(self, album: AlbumDTO) -> bool:
        try:
            album_dict: dict = album.album_to_dict()
            album_dict["_id"] = album_dict.pop("id", None)
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": album_dict["_id"]}, {"$set": album_dict}
            )
            return result.modified_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el álbum: {e}")
            return False
    

    def delete_album(self, id: str) -> bool:
        try:
            result: pymongo.results.DeleteResult = self.collection.delete_one({"_id": id})
            return result.deleted_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar el álbum: {e}")
            return False