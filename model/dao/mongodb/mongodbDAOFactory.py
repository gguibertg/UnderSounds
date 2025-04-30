from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbFaqDAO import MongodbFaqDAO
from .collection.mongodbDAOUsuario import mongodbUsuarioDAO
from .collection.mongodbDAOAlbum import mongodbAlbumDAO
from .collection.mongodbDAOGenero import mongodbGeneroDAO
from .collection.mongodbSongDAO import MongodbSongDAO
from .collection.mongodbDAOCarrito import mongodbCarritoDAO
from .collection.mongodbDAOContacto import mongodbContactoDAO
from .collection.mongodbDAOReseña import mongodbReseñaDAO
from .collection.mongodbDAOSesion import mongodbSesionDAO


# Esta es la clase que implementa el patrón DAO Factory, que genera los DAOs de MongoDB.
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
    
    def getContactoDAO(self):
        return mongodbContactoDAO(self.connector.get_contacto_collection())
    
    def getReseñaDAO(self):
        return mongodbReseñaDAO(self.connector.get_reseña_collection())
    
    def getSesionDAO(self):
        return mongodbSesionDAO(self.connector.get_sesion_collection())
