from abc import ABC, abstractmethod

class InterfaceGeneroDAO(ABC):

    @abstractmethod	
    def get_genero(self, id):
        pass