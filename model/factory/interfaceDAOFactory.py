from abc import abstractmethod, ABC

class InterfaceDAOFactory(ABC):

    @abstractmethod
    def getUsuariosDAO(self):
        pass

