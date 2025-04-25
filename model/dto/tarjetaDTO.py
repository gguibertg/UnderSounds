class TarjetaDTO:
    
    def __init__(self):
        self.id: str = None
        self.usuario: str = None
        self.numero: str = None
        self.fecha: str = None

    def is_empty(self):
        return (self.id is None and self.usuario is None and 
                self.numero is None and self.fecha is None)

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_usuario(self) -> str:
        return self.usuario

    def set_usuario(self, usuario: str):
        self.usuario = usuario

    def get_numero(self) -> str:
        return self.numero

    def set_numero(self, numero: str):
        self.numero = numero

    def get_fecha(self) -> str:
        return self.fecha

    def set_fecha(self, fecha: str):
        self.fecha = fecha

    def get_fecha(self) -> str:
        return self.fecha

    def set_fecha(self, fecha: str):
        self.fecha = fecha


    def to_dict(self):
        return {
            "id": self.id,
            "usuario": self.usuario,
            "numero": self.numero,
            "fecha": self.fecha
        }