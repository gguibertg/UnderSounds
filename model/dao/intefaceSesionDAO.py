from abc import ABC, abstractmethod
from model.dto.sesionDTO import SesionDTO

class InterfaceSesionDAO(ABC):
    
    @abstractmethod
    def get_all_sesiones(self):
        pass

    @abstractmethod	
    def get_sesion(self, id : str):
        pass

    @abstractmethod
    def add_sesion(self, sesion : SesionDTO):
        pass

    @abstractmethod
    def update_sesion(self, usuario : SesionDTO):
        pass

    @abstractmethod
    def delete_sesion(self, id : str):
        pass