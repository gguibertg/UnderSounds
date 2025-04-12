from abc import abstractmethod, ABC

class InterfaceDAOFactory(ABC):

    @abstractmethod
    def getFaqsDAO(self):
        pass

