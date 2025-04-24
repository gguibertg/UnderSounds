from ...interfaceTarjetaDAO import InterfaceTarjetaDAO
from ....dto.tarjetaDTO import TarjetaDTO

class MongodbTarjetaDAO(InterfaceTarjetaDAO):

    def __init__(self, collection):
        self.collection = collection

    def get_tarjeta(self, usuario: str):
        pass

    def add_tarjeta(self, tarjeta: TarjetaDTO):
        pass
