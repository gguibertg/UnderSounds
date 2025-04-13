from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbSongDAO import MongodbSongDAO

class MongodbDAOFactory(InterfaceDAOFactory):
    def __init__(self):
        self.connector = MongoConnector()

    def getSongsDAO(self):
        return MongodbSongDAO(self.connector.post_song_collection())
    