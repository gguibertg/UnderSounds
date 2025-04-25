from abc import ABC, abstractmethod

class InterfaceGeneroDAO(ABC):

    @abstractmethod	
    def get_genero(self, id):
        pass

    @abstractmethod
    def get_generos(self):
        pass