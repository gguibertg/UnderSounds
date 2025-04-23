import pymongo
import pymongo.results
from bson import ObjectId
from ...interfaceSongDAO import InterfaceSongDAO
from ....dto.songDTO import SongDTO, SongsDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de Usuarios en MongoDB.
class MongodbSongDAO(InterfaceSongDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_songs(self):
        songs = SongsDTO()
        try:
            query = self.collection.find()

            for doc in query:
                song_dto = SongDTO()
                song_dto.set_id(str(doc.get("_id")))
                song_dto.set_titulo(doc.get("titulo"))
                song_dto.set_artista(doc.get("artista"))
                song_dto.set_colaboradores(doc.get("colaboradores"))
                song_dto.set_fecha(doc.get("fecha"))
                song_dto.set_descripcion(doc.get("descripcion"))
                song_dto.set_duracion(doc.get("duracion"))
                song_dto.set_generos(doc.get("generos"))
                song_dto.set_likes(doc.get("likes"))
                song_dto.set_visitas(doc.get("visitas"))
                song_dto.set_portada(doc.get("portada"))
                song_dto.set_precio(doc.get("precio"))
                song_dto.set_lista_resenas(doc.get("lista_resenas"))
                song_dto.set_visible(doc.get("visible"))
                song_dto.set_album(doc.get("album"))

                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los usuarios: {e}")

        return [song.songdto_to_dict() for song in songs.songlist]


    def get_song(self, id: str):
        song = None

        try:
            query = self.collection.find_one({"_id": ObjectId(id)})

            if query:
                song = SongDTO()
                song.set_id(str(query.get("_id")))
                song.set_titulo(query.get("titulo"))
                song.set_artista(query.get("artista"))
                song.set_colaboradores(query.get("colaboradores"))
                song.set_fecha(query.get("fecha"))
                song.set_descripcion(query.get("descripcion"))
                song.set_duracion(query.get("duracion"))
                song.set_generos(query.get("generos"))
                song.set_likes(query.get("likes"))
                song.set_visitas(query.get("visitas"))
                song.set_portada(query.get("portada"))
                song.set_precio(query.get("precio"))
                song.set_lista_resenas(query.get("lista_resenas"))
                song.set_visible(query.get("visible"))
                song.set_album(query.get("album"))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar el usuario: {e}")

        return song.songdto_to_dict() if song else None
    

    def add_song(self, song: SongDTO) -> str:
        try:
            song_dict : dict = song.songdto_to_dict()
            song_dict.pop("id", None)
            result : pymongo.results.InsertOneResult = self.collection.insert_one(song_dict)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el usuario: {e}")
            return None
        

    def update_song(self, song: SongDTO) -> bool:
        try:
            song_dict = song.songdto_to_dict()
            song_id = song_dict.pop("id")
            song_dict["_id"] = ObjectId(song_id)  # importante

            result : pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": ObjectId(song_id)},  # usa ObjectId aquí también
                {"$set": song_dict}
            )
            return result.modified_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar el usuario: {e}")
            return False
    

    def delete_song(self, id: str) -> bool:
        try:
            result : pymongo.results.DeleteResult = self.collection.delete_one({"_id": id})
            return result.deleted_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar el usuario: {e}")
            return False