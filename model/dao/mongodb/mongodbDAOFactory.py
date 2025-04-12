from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbDAOUsuario import mongodbUsuarioDAO

# Esta es la clase que implementa el patrón DAO Factory, que genera los DAOs de MongoDB.

class mongodbDAOFactory(InterfaceDAOFactory):

    def __init__(self):
        self.connector = MongoConnector()

    def getUsuariosDAO(self):
        return mongodbUsuarioDAO(self.connector.get_usuario_collection())