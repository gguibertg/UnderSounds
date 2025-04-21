from abc import ABC, abstractmethod

class InterfaceListaDAO(ABC):

    @abstractmethod	
    def get_lista(self, id):
        pass

    @abstractmethod
    def add_lista(self, lista):
        pass

    @abstractmethod
    def update_lista(self, lista):
        pass

    @abstractmethod
    def delete_lista(self, id):
        pass