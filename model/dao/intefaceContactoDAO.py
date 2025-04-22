from abc import ABC, abstractmethod

class InterfaceContactoDAO(ABC):

    @abstractmethod
    def add_contacto(self, album):
        pass