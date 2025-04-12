from abc import ABC, abstractmethod

class InterfaceUsuarioDAO(ABC):
    
    @abstractmethod
    def get_all_usuarios(self):
        pass

    @abstractmethod	
    def get_usuario(self, id):
        pass

    @abstractmethod
    def add_usuario(self, usuario):
        pass

    @abstractmethod
    def update_usuario(self, usuario):
        pass

    @abstractmethod
    def delete_usuario(self, id):
        pass