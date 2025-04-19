from abc import ABC, abstractmethod

class InterfaceCarritoDAO(ABC):

    @abstractmethod
    def get_all_articulos(self, usuario):
        pass
    
    @abstractmethod
    def upsert_articulo_en_carrito(self, usuario, articulo) -> bool:
        pass

    @abstractmethod
    def articulo_existe_en_carrito(self, carrito, articulo_id) -> bool:
        pass
    
    @abstractmethod
    def agregar_articulo_a_carrito(self, usuario, articulo_dict) -> bool:
        pass
    
    @abstractmethod
    def crear_carrito(self, usuario, articulo_dict) -> bool:
        pass
    
    @abstractmethod
    def deleteArticuloDelCarrito(self, usuario, id_articulo) -> bool:
        pass

    
