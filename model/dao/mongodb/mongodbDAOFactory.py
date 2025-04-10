from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbDAOSong import MongodbSongDAO
from .collection.mongodbFaqDAO import MongodbFaqDAO

class MongodbDAOFactory(InterfaceDAOFactory):
    def __init__(self):
        self.connector = MongoConnector()

    def getSongsDAO(self):
        return MongodbSongDAO(self.connector.get_song_collection())

    def getFaqsDAO(self):
        return MongodbFaqDAO(self.connector.get_faq_collection())
    

