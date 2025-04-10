from abc import abstractmethod, ABC

class InterfaceDAOFactory(ABC):

    @abstractmethod
    def getSongsDAO(self):
        pass

    @abstractmethod
    def getFaqsDAO(self):
        pass

