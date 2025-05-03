import pymongo
from pymongo.results import *
from bson import ObjectId
from datetime import datetime, timedelta
from ...interfaceSongDAO import InterfaceSongDAO
from ....dto.songDTO import SongDTO, SongsDTO

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección de songs en MongoDB.
class MongodbSongDAO(InterfaceSongDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_songs(self):
        songs = SongsDTO()
        try:
            query = self.collection.find({"visible": True})

            for doc in query:
                song_dto = SongDTO()
                song_dto.set_id(str(doc.get("_id")))
                song_dto.set_titulo(doc.get("titulo"))
                song_dto.set_artista(doc.get("artista"))
                song_dto.set_colaboradores(doc.get("colaboradores"))
                song_dto.set_fecha(doc.get("fecha"))
                song_dto.set_fechaUltimaModificacion(doc.get("fechaUltimaModificacion"))
                song_dto.set_descripcion(doc.get("descripcion"))
                song_dto.set_duracion(doc.get("duracion"))
                song_dto.set_generos(doc.get("generos"))
                song_dto.set_likes(doc.get("likes"))
                song_dto.set_visitas(doc.get("visitas"))
                song_dto.set_portada(doc.get("portada"))
                song_dto.set_precio(doc.get("precio"))
                song_dto.set_lista_resenas(doc.get("lista_resenas"))
                song_dto.set_visible(doc.get("visiblAe"))
                song_dto.set_album(doc.get("album"))
                song_dto.set_historial(doc.get("historial"))

                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

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
                song.set_fechaUltimaModificacion(query.get("fechaUltimaModificacion"))
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
                song.set_historial(query.get("historial"))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar la cancion: {e}")

        return song.songdto_to_dict() if song else None
    
    def add_song(self, song: SongDTO) -> str:
        try:
            song_dict : dict = song.songdto_to_dict()
            song_dict.pop("id", None)
            result : InsertOneResult = self.collection.insert_one(song_dict)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar la cancion: {e}")
            return None
        
    def update_song(self, song: SongDTO) -> bool:
        try:
            song_dict = song.songdto_to_dict()
            song_id = song_dict.pop("id")
            song_dict["_id"] = ObjectId(song_id)  # importante

            result : UpdateResult = self.collection.update_one({"_id": ObjectId(song_id)}, {"$set": song_dict})
            return result.matched_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al actualizar la cancion: {e}")
            return False
    
    def delete_song(self, id: str) -> bool:
        try:
            result : DeleteResult = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar la cancion: {e}")
            return False

    def get_all_by_genre(self, genre: str):
        songs = SongsDTO()
        try:
            query = self.collection.find({"generos": genre, "visible": True})

            for doc in query:

                song_dto = SongDTO()
                song_dto.set_id(str(doc.get("_id")))
                song_dto.set_titulo(doc.get("titulo"))
                song_dto.set_artista(doc.get("artista"))
                song_dto.set_colaboradores(doc.get("colaboradores"))
                song_dto.set_fecha(doc.get("fecha"))
                song_dto.set_fechaUltimaModificacion(doc.get("fechaUltimaModificacion"))
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
                song_dto.set_historial(doc.get("historial"))

                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [song.songdto_to_dict() for song in songs.songlist]

    def get_all_by_fecha(self, fecha_str):
        songs = SongsDTO()
        try:
            fecha_min = None
            fecha_max = None

            if len(fecha_str) == 4:  # Año: "2025"
                fecha_min = datetime.strptime(fecha_str, "%Y")
                fecha_max = datetime(fecha_min.year + 1, 1, 1)

            elif len(fecha_str) == 7:  # Año y mes: "2025-04"
                fecha_min = datetime.strptime(fecha_str, "%Y-%m")
                if fecha_min.month == 12:
                    fecha_max = datetime(fecha_min.year + 1, 1, 1)
                else:
                    fecha_max = datetime(fecha_min.year, fecha_min.month + 1, 1)

            elif len(fecha_str) == 10:  # Fecha completa: "2025-04-27"
                fecha_min = datetime.strptime(fecha_str, "%Y-%m-%d")
                fecha_max = fecha_min + timedelta(days=1)

            else:
                raise ValueError("Formato de fecha inválido")

            query = self.collection.find({
                "fecha": {
                    "$gte": fecha_min,
                    "$lt": fecha_max
                },
                "visible": True
            })

            for doc in query:

                song_dto = SongDTO()
                song_dto.set_id(str(doc.get("_id")))
                song_dto.set_titulo(doc.get("titulo"))
                song_dto.set_artista(doc.get("artista"))
                song_dto.set_colaboradores(doc.get("colaboradores"))
                song_dto.set_fecha(doc.get("fecha"))
                song_dto.set_fechaUltimaModificacion(doc.get("fechaUltimaModificacion"))
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
                song_dto.set_historial(doc.get("historial"))

                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [song.songdto_to_dict() for song in songs.songlist]

    def get_all_by_nombre(self, titulo):
        songs = SongsDTO()
        try:
            query = self.collection.find({"titulo": {"$regex": titulo, "$options": "i"}, "visible": True})

            for doc in query:

                song_dto = SongDTO()
                song_dto.set_id(str(doc.get("_id")))
                song_dto.set_titulo(doc.get("titulo"))
                song_dto.set_artista(doc.get("artista"))
                song_dto.set_colaboradores(doc.get("colaboradores"))
                song_dto.set_fecha(doc.get("fecha"))
                song_dto.set_fechaUltimaModificacion(doc.get("fechaUltimaModificacion"))
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
                song_dto.set_historial(doc.get("historial"))

                songs.insertSong(song_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar las canciones: {e}")

        return [song.songdto_to_dict() for song in songs.songlist]