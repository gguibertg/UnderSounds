from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbFaqDAO import MongodbFaqDAO
from .collection.mongodbDAOUsuario import mongodbUsuarioDAO
from .collection.mongodbDAOAlbum import mongodbAlbumDAO
from .collection.mongodbDAOGenero import mongodbGeneroDAO
from .collection.mongodbSongDAO import MongodbSongDAO
from .collection.mongodbDAOCarrito import mongodbCarritoDAO

# Esta es la clase que implementa el patrón DAO Factory, que genera los DAOs de MongoDB.

class mongodbDAOFactory(InterfaceDAOFactory):

from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbSongDAO import MongodbSongDAO

class MongodbDAOFactory(InterfaceDAOFactory):
    def __init__(self):
        self.connector = MongoConnector()

    def getUsuariosDAO(self):
        return mongodbUsuarioDAO(self.connector.get_usuario_collection())

    def getFaqsDAO(self):
        return MongodbFaqDAO(self.connector.post_faq_collection())
    
    def getCarritoDAO(self):
       return mongodbCarritoDAO(self.connector.get_articulos_carrito())
    
    def getAlbumDAO(self):
        return mongodbAlbumDAO(self.connector.get_album_collection())

    def getGeneroDAO(self):
        return mongodbGeneroDAO(self.connector.get_genero_collection())
    
    def getSongsDAO(self):
        return MongodbSongDAO(self.connector.post_song_collection())

        self.connector = MongoConnector()

    def getSongsDAO(self):
        return MongodbSongDAO(self.connector.post_song_collection())
    