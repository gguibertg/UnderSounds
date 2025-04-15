from .dao.mongodb.mongodbDAOFactory import mongodbDAOFactory
from .dto.usuarioDTO import UsuarioDTO, UsuariosDTO

# La clase Model tiene los métodos que hacen puente entre controller y la base de datos.
class Model ():

    def __init__(self):
        self.factory = mongodbDAOFactory()
        self.daoUsuario = self.factory.getUsuariosDAO()
        self.faqsDAO = self.factory.getFaqsDAO()
        pass
    
    def get_usuario(self, id):
        return self.daoUsuario.get_usuario(id)
    
    def add_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.add_usuario(usuario)

    def update_usuario(self, usuario : UsuarioDTO):
        return self.daoUsuario.update_usuario(usuario)

    def delete_usuario(self, id):
        return self.daoUsuario.delete_usuario(id)

    def get_usuarios(self):
        return self.daoUsuario.get_all_usuarios()

    def get_faqs(self):
        return self.faqsDAO.get_all_faqs()
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
    # La función recibe el nombre, el email, el teléfono y el mensaje del contacto.
    # La función devuelve True si se ha guardado correctamente y False si ha habido un error.
    def save_contact_msg(self, name: str, email: str, telf: str, msg: str):
        return True