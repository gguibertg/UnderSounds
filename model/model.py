from .dao.mongodb.mongodbDAOFactory import MongodbDAOFactory

class Model:

    def __init__(self):
        self.factory = MongodbDAOFactory()
        self.faqsDAO = self.factory.getFaqsDAO()

    def get_faqs(self):
        return self.faqsDAO.get_all_faqs()