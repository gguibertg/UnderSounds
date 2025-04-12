from ...factory.interfaceDAOFactory import InterfaceDAOFactory
from .mongodbConnector import MongoConnector
from .collection.mongodbFaqDAO import MongodbFaqDAO

class MongodbDAOFactory(InterfaceDAOFactory):
    def __init__(self):
        self.connector = MongoConnector()

    def getFaqsDAO(self):
        return MongodbFaqDAO(self.connector.post_faq_collection())
    

