from bson import ObjectId
import pymongo
import pymongo.results
from ...interfaceSongDAO import InterfaceSongDAO
from ....dto.songDTO import SongDTO, SongsDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

class MongodbSongDAO(InterfaceSongDAO):
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_songs(self):
        songs = SongsDTO()
        try:
            for doc in self.collection.find():
                song_dto = SongDTO()
                song_dto.set_id(str(doc.get("_id")))
                song_dto.set_titulo(doc.get("title") or doc.get("titulo"))
                song_dto.set_artista(doc.get("artist"))
                song_dto.set_colaboradores(doc.get("collaborators") or [])
                song_dto.set_fecha(doc.get("date") or doc.get("fecha"))
                song_dto.set_descripcion(doc.get("description") or doc.get("descripcion"))
                song_dto.set_duracion(doc.get("duration") or doc.get("duracion"))
                song_dto.set_generos(doc.get("genres") or [])
                song_dto.set_likes(int(doc.get("likes", 0)))
                song_dto.set_visitas(int(doc.get("visitas", 0)))
                song_dto.set_portada(doc.get("portada"))
                song_dto.set_precio(float(doc.get("price") or doc.get("precio") or 0.0))
                song_dto.set_lista_resenas(doc.get("review_list") or doc.get("lista_reseñas") or [])
                song_dto.set_visible(bool(doc.get("visible", True)))
                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [song.songdto_to_dict() for song in songs.get_songlist()]

    def get_song(self, id: str):
        song = None
        try:
            doc = self.collection.find_one({"_id": ObjectId(id)})
            if doc:
                song = SongDTO()
                song.set_id(str(doc.get("_id")))
                song.set_titulo(doc.get("title") or doc.get("titulo"))
                song.set_artista(doc.get("artist"))
                song.set_colaboradores(doc.get("collaborators") or [])
                song.set_fecha(doc.get("date") or doc.get("fecha"))
                song.set_descripcion(doc.get("description") or doc.get("descripcion"))
                song.set_duracion(doc.get("duration") or doc.get("duracion"))
                song.set_generos(doc.get("genres") or [])
                song.set_likes(int(doc.get("likes", 0)))
                song.set_visitas(int(doc.get("visitas", 0)))
                song.set_portada(doc.get("portada"))
                song.set_precio(float(doc.get("price") or doc.get("precio") or 0.0))
                song.set_lista_resenas(doc.get("review_list") or doc.get("lista_reseñas") or [])
                song.set_visible(bool(doc.get("visible", True)))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar la canción: {e}")

        return song.songdto_to_dict() if song else None

    def add_song(self, song: SongDTO) -> str:
        try:
            song_dict = song.songdto_to_dict()
            song_dict.pop("id", None)
            result: pymongo.results.InsertOneResult = self.collection.insert_one(song_dict)
            return str(result.inserted_id)
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar la canción: {e}")
            return None

    def update_song(self, song: SongDTO) -> bool:
        try:
            song_dict = song.songdto_to_dict()
            oid = ObjectId(song_dict.pop("id", None))
            song_dict["_id"] = oid
            result: pymongo.results.UpdateResult = self.collection.update_one(
                {"_id": oid},
                {"$set": song_dict}
            )
            return result.modified_count == 1
        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar la canción: {e}")
            return False

    def delete_song(self, id: str) -> bool:
        try:
            result: pymongo.results.DeleteResult = self.collection.delete_one(
                {"_id": ObjectId(id)}
            )
            return result.deleted_count == 1
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar la canción: {e}")
            return False