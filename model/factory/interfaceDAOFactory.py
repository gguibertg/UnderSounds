from abc import abstractmethod, ABC

class InterfaceDAOFactory(ABC):

# Colecciones de la base de datos (por DAO)

    @abstractmethod
    def getUsuariosDAO(self):
        pass

