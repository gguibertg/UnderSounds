from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbDAOUsuario import mongodbUsuarioDAO

# -----------------------------------------------------------
# No se muy bien para que sirve esta clase.
# Quien lo sepa mejor, que lo explique aquí:
# -----------------------------------------------------------

class mongodbDAOFactory(InterfaceDAOFactory):

    def __init__(self):
        self.connector = MongoConnector()

    def getUsuariosDAO(self):
        return mongodbUsuarioDAO(self.connector.get_usuario_collection())