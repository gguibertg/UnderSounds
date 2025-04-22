from abc import abstractmethod, ABC

class InterfaceDAOFactory(ABC):

# Un método por cada colección existente en la base de datos.

    @abstractmethod
    def getUsuariosDAO(self):
        pass

    @abstractmethod
    def getFaqsDAO(self):
        pass
    
    @abstractmethod
    def getCarritoDAO (self):
        pass

    @abstractmethod
    def getAlbumDAO(self):
        pass

    @abstractmethod
    def getGeneroDAO(self):
        pass

    @abstractmethod
    def getSongsDAO(self):
        pass


