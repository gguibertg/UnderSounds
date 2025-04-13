from .dao.mongodb.mongodbDAOFactory import MongodbDAOFactory #TODO: Cambiar a MongoDB
from .dto.songDTO import SongDTO, SongsDTO

# La clase Model es la encargada de gestionar los datos y la lógica de negocio de la aplicación.
# Esta clase nos permite interactuar con la base de datos y obtener los datos que necesitamos para la aplicación,
# sin la necesidad de que otras clases tengan que preocuparse por la implementación de la base de datos.
class Model ():

    # Al crear la clase definimos factores y DAOs que vamos a usar para interactuar con la base de datos.
    def __init__(self):
        self.factory = MongodbDAOFactory()
        self.songsDAO = self.factory.getSongsDAO()
        pass

    def get_song(self, id):
        return self.songsDAO.get_song(id)
    
    def add_song(self, usuario : SongDTO):
        return self.songsDAO.add_song(usuario)

    def update_song(self, usuario : SongDTO):
        return self.songsDAO.update_song(usuario)

    def delete_song(self, id):
        return self.songsDAO.delete_song(id)

    def get_songs(self):
        return self.songsDAO.get_all_songs()