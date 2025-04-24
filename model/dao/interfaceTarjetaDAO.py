from abc import ABC, abstractmethod
from ..dto.tarjetaDTO import TarjetaDTO

class InterfaceTarjetaDAO(ABC):

    @abstractmethod
    def get_tarjeta(self, usuario: str):
        pass

    @abstractmethod
    def add_tarjeta(self, tarjeta: TarjetaDTO):
        pass