import pymongo
import pymongo.results
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
                song_dto.set_album(doc.get("album"))
                song_dto.set_artist(doc.get("artist"))
                song_dto.set_collaborators(doc.get("collaborators"))
                song_dto.set_date(doc.get("date"))
                song_dto.set_description(query.get("description"))
                song_dto.set_duration(doc.get("duration"))
                song_dto.set_genres(doc.get("genres"))
                song_dto.set_likes(str(doc.get("likes")))
                song_dto.set_portada(query.get("portada"))
                song_dto.set_price(doc.get("price"))
                song_dto.set_review_list(doc.get("review_list"))

                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los usuarios: {e}")

        return [song.songdto_to_dict() for song in songs.songlist]


    def get_song(self, id):
        song = None

        try:
            query = self.collection.find_one({"_id": id})

            if query:
                song = SongDTO()
                song.set_id(str(query.get("_id")))
                song.set_album(query.get("album"))
                song.set_artist(query.get("artist"))
                song.set_collaborators(query.get("collaborators"))
                song.set_date(query.get("date"))
                song.set_description(query.get("description"))
                song.set_duration(query.get("duration"))
                song.set_genres(query.get("genres"))
                song.set_likes(str(query.get("likes")))
                song.set_price(query.get("price"))
                song.set_portada(query.get("portada"))
                song.set_review_list(query.get("review_list"))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar el usuario: {e}")

        return song.songdto_to_dict() if song else None
    

    def add_song(self, song: SongDTO) -> str:
        try:
            song_dict : dict = song.songdto_to_dict()
            song_dict.pop("id", None)
            result : pymongo.results.InsertOneResult = self.collection.insert_one(song_dict)
            return result.inserted_id == song_dict["_id"]
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar el usuario: {e}")
            return None
        

    def update_song(self, song: SongDTO) -> bool:
        try:
            song_dict : dict = song.songdto_to_dict()
            song_dict["_id"] = song_dict.pop("id", None)
            result : pymongo.results.UpdateResult = self.collection.update_one({"_id": song_dict["_id"]}, {"$set": song_dict})
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