"""
Fábrica DAO para MongoDB.
Permite obtener instancias DAO específicas para diferentes entidades.
"""

from pymongo import MongoClient
from ...factory.interface_dao_factory import InterfaceDAOFactory
from .collection.mongodbDAOSong import mongodbSongDAO
from .collection.mongodb_faq_dao import MongodbFaqDAO

class MongodbDAOFactory(InterfaceDAOFactory):
    """
    Fábrica de DAOs para MongoDB.
    """

    def __init__(self):
        client = MongoClient("mongodb://localhost:27017")
        self.db = client["undersounds"]

    def get_song_dao(self):
        """
        Devuelve el DAO para canciones.
        """
        return mongodbSongDAO(self.db["songs"])

    def getSongDao(self):
        return MongodbSongDAO()

    def get_dao_faq(self):
        """
        Devuelve el DAO para preguntas frecuentes.
        """
        return MongodbFaqDAO(self.db)
