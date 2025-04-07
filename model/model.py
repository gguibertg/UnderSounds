from .dao.mongodb.mongodbDAOFactory import mongodbDAOFactory #TODO: Cambiar a MongoDB
from .dto.song_dto import SongDTO, SongsDTO

# La clase Model es la encargada de gestionar los datos y la lógica de negocio de la aplicación.
# Esta clase nos permite interactuar con la base de datos y obtener los datos que necesitamos para la aplicación,
# sin la necesidad de que otras clases tengan que preocuparse por la implementación de la base de datos.
class Model ():

    # Al crear la clase definimos factores y DAOs que vamos a usar para interactuar con la base de datos.
    def __init__(self):
        self.factory = mongodbDAOFactory()
        self.daoSong = self.factory.getSongDao()
        pass

    # Cuando alguien utilice la función get_songs, se va a llamar a la función get_songs de la clase DAO.
    # Esta función va a devolver una lista de canciones en formato JSON.
    def get_songs(self):
        # Primero definimos un objeto de la clase SongsDTO, que es la que se va a usar para almacenar las canciones.
        mySongsDTO = SongsDTO()
        # Luego llamamos a la función get_songs de la clase DAO, que nos va a devolver una lista de canciones.
        songs = self.daoSong.get_songs()
        # Por último, por cada canción que nos ha devuelto la DAO, creamos un objeto de la clase SongDTO y lo añadimos a la lista de canciones.
        for s in songs:
            song_data = s # (Local)
           # Crear un objeto SongDTO con los datos de la canción
            song_dto = SongDTO()
           # song_dto.id = doc.id  # (Firestore)
            song_dto.title = song_data.get("id", "") # (Local)
            song_dto.title = song_data.get("title", "")
            song_dto.author = song_data.get("author", "")
            song_dto.album = song_data.get("album", "")
            song_dto.musicgenre = song_data.get("musicgenre", "")
            song_dto.duration = song_data.get("duration", 0)
            song_dto.price = song_data.get("price", 0.0)
            song_dto.rating = song_data.get("rating", 0)
            song_dto.release = song_data.get("release", "")
            mySongsDTO.insertSong(song_dto.songdto_to_dict())  # Agregar la canción a la lista
        return mySongsDTO.songlist_to_json()


    # TODO: Esta función se va a usar para guardar el mensaje de contacto en la base de datos.
    def save_contact_msg(self, name: str, email: str, telf: str, msg: str):
        return True