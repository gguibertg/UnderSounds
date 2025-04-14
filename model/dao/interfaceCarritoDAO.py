from abc import ABC, abstractmethod

class InterfaceCarritoDAO(ABC):

    @abstractmethod
    def get_all_articulos(self):
        pass
    
    @abstractmethod
    def insertArticulo(self, articulo, cantidad):
        pass
    
    @abstractmethod
    def deleteArticulo(self, id):
        pass
    
    @abstractmethod
    def incrementArticulo(self, id):
        pass
    
    @abstractmethod
    def decrementArticulo (self, id):
        pass
    
