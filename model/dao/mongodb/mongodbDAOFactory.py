from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbFaqDAO import MongodbFaqDAO
from .collection.mongodbDAOUsuario import mongodbUsuarioDAO
from .collection.mongodbDAOAlbum import mongodbAlbumDAO
from .collection.mongodbDAOGenero import mongodbGeneroDAO

# Esta es la clase que implementa el patrón DAO Factory, que genera los DAOs de MongoDB.

class mongodbDAOFactory(InterfaceDAOFactory):

    def __init__(self):
        self.connector = MongoConnector()

    def getUsuariosDAO(self):
        return mongodbUsuarioDAO(self.connector.get_usuario_collection())

    def getFaqsDAO(self):
        return MongodbFaqDAO(self.connector.post_faq_collection())
    
    def getAlbumDAO(self):
        return mongodbAlbumDAO(self.connector.get_album_collection())

    def getGeneroDAO(self):
        return mongodbGeneroDAO(self.connector.get_genero_collection())

