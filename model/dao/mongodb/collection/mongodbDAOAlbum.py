from bson import ObjectId
import pymongo
import pymongo.results
from ...intefaceAlbumDAO import InterfaceAlbumDAO
from ....dto.albumDTO import AlbumDTO, AlbumsDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class mongodbAlbumDAO(InterfaceAlbumDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection

    def get_all_albums(self):
        albums = AlbumsDTO()
        try:
            query = self.collection.find()

            for doc in query:
                album_dto = AlbumDTO()
                album_dto.set_id(str(doc.get("_id")))  # Convertimos _id a str
                album_dto.set_titulo(doc.get("titulo"))
                album_dto.set_autor(doc.get("autor"))
                album_dto.set_colaboradores(doc.get("colaboradores"))
                album_dto.set_descripcion(doc.get("descripcion"))
                album_dto.set_fecha(doc.get("fecha"))
                album_dto.set_generos(doc.get("generos", []))
                album_dto.set_canciones(doc.get("canciones", []))
                album_dto.set_visitas(doc.get("visitas"))
                album_dto.set_portada(doc.get("portada"))
                album_dto.set_precio(doc.get("precio"))
                album_dto.set_likes(doc.get("likes"))
                album_dto.set_visible(doc.get("visible"))

                albums.insertSong(album_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [album.album_to_dict() for album in albums.albumlist]
    

    def get_all_by_genre(self, genre):
        albums = AlbumsDTO()
        try:
            query = self.collection.find({"generos": genre})

            for doc in query:
                album_dto = AlbumDTO()
                album_dto.set_id(str(doc.get("_id")))  # Convertimos _id a str
                album_dto.set_titulo(doc.get("titulo"))
                album_dto.set_autor(doc.get("autor"))
                album_dto.set_colaboradores(doc.get("colaboradores"))
                album_dto.set_descripcion(doc.get("descripcion"))
                album_dto.set_fecha(doc.get("fecha"))
                album_dto.set_generos(doc.get("generos", []))
                album_dto.set_canciones(doc.get("canciones", []))
                album_dto.set_visitas(doc.get("visitas"))
                album_dto.set_portada(doc.get("portada"))
                album_dto.set_precio(doc.get("precio"))
                album_dto.set_likes(doc.get("likes"))
                album_dto.set_visible(doc.get("visible"))

                albums.insertSong(album_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [album.album_to_dict() for album in albums.albumlist]
    
    def get_all_by_fecha(self, fecha):
        albums = AlbumsDTO()
        try:
            query = self.collection.find({"fecha": {"$gte":fecha}})

            for doc in query:
                album_dto = AlbumDTO()
                album_dto.set_id(str(doc.get("_id")))  # Convertimos _id a str
                album_dto.set_titulo(doc.get("titulo"))
                album_dto.set_autor(doc.get("autor"))
                album_dto.set_colaboradores(doc.get("colaboradores"))
                album_dto.set_descripcion(doc.get("descripcion"))
                album_dto.set_fecha(doc.get("fecha"))
                album_dto.set_generos(doc.get("generos", []))
                album_dto.set_canciones(doc.get("canciones", []))
                album_dto.set_visitas(doc.get("visitas"))
                album_dto.set_portada(doc.get("portada"))
                album_dto.set_precio(doc.get("precio"))
                album_dto.set_likes(doc.get("likes"))
                album_dto.set_visible(doc.get("visible"))

                albums.insertSong(album_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [album.album_to_dict() for album in albums.albumlist]
    
    def get_all_by_nombre(self, titulo):
        albums = AlbumsDTO()
        try:
            query = self.collection.find({"titulo": {"$regex": titulo, "$options": "i"}})

            for doc in query:
                album_dto = AlbumDTO()
                album_dto.set_id(str(doc.get("_id")))  # Convertimos _id a str
                album_dto.set_titulo(doc.get("titulo"))
                album_dto.set_autor(doc.get("autor"))
                album_dto.set_colaboradores(doc.get("colaboradores"))
                album_dto.set_descripcion(doc.get("descripcion"))
                album_dto.set_fecha(doc.get("fecha"))
                album_dto.set_generos(doc.get("generos", []))
                album_dto.set_canciones(doc.get("canciones", []))
                album_dto.set_visitas(doc.get("visitas"))
                album_dto.set_portada(doc.get("portada"))
                album_dto.set_precio(doc.get("precio"))
                album_dto.set_likes(doc.get("likes"))
                album_dto.set_visible(doc.get("visible"))

                albums.insertSong(album_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [album.album_to_dict() for album in albums.albumlist]
    

    def add_album(self, album: AlbumDTO) -> str:
        try:
            album_dict: dict = album.album_to_dict()
            album_dict.pop("id", None)  # id debería estar vacío, así que lo descartamos
            result: pymongo.results.InsertOneResult = self.collection.insert_one(album_dict)
            return str(result.inserted_id)  # Devolvemos el nuevo _id del álbum

        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el álbum: {e}")
            return None


    def update_album(self, album: AlbumDTO) -> bool:
        try:
            album_dict: dict = album.album_to_dict()
            album_dict["_id"] = ObjectId(album_dict.pop("id", None))  # Convertimos id a ObjectId
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": album_dict["_id"]}, {"$set": album_dict}
            )
            return result.matched_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el álbum: {e}")
            return False
    

    def delete_album(self, id: str) -> bool:
        try:
            result: pymongo.results.DeleteResult = self.collection.delete_one({"_id": ObjectId(id)})  # Convertimos id a ObjectId
            return result.deleted_count == 1

        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar el álbum: {e}")
            return False