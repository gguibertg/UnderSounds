from abc import ABC, abstractmethod

class InterfaceUsuarioDAO(ABC):
    
    @abstractmethod
    def get_all_usuarios(self):
        pass