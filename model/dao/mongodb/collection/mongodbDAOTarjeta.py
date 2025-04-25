from ...interfaceTarjetaDAO import InterfaceTarjetaDAO
from ....dto.tarjetaDTO import TarjetaDTO
from pymongo.results import *

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

class MongodbTarjetaDAO(InterfaceTarjetaDAO):

    def __init__(self, collection):
        self.collection = collection

    def get_tarjeta(self, usuario: str):
        tarjeta = None

        try:
            query = self.collection.find_one({"usuario": usuario})

            if query:
                tarjeta = TarjetaDTO()
                tarjeta.set_id(str(query.get("_id")))
                tarjeta.set_usuario(query.get("usuario"))
                tarjeta.set_numero(query.get("numero"))
                tarjeta.set_fecha(query.get("fecha"))

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar la tarjeta: {e}")

        return tarjeta.to_dict() if tarjeta else None


    def add_tarjeta(self, tarjeta: TarjetaDTO):
        try:
            tarjeta_dict : dict = tarjeta.to_dict()
            tarjeta_dict.pop("id", None)
            result : InsertOneResult = self.collection.insert_one(tarjeta_dict)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al agregar la tarjeta: {e}")
            return None
