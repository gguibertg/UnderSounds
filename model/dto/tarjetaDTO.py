class TarjetaDTO:
    
    def __init__(self):
        self.id: str = None
        self.usuario: str = None
        self.numero: str = None
        self.fecha: str = None
        self.codigo: int = None

    def is_empty(self):
        return (self.id is None and self.usuario is None and 
                self.numero is None and self.fecha is None and self.codigo is None)

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

    def get_codigo(self) -> int:
        return self.codigo

    def set_codigo(self, codigo: int):
        self.codigo = codigo


    def to_dict(self):
        return {
            "id": self.id,
            "usuario": self.usuario,
            "numero": self.numero,
            "fecha": self.fecha,
            "codigo": self.codigo
        }