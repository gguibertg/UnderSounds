class ContactoDTO:
    def __init__(self):
        self.id: str = None
        self.nombre: str = None
        self.email: str = None
        self.telefono: str = None
        self.mensaje: str = None

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_nombre(self) -> str:
        return self.nombre

    def set_nombre(self, nombre: str):
        self.nombre = nombre

    def get_email(self) -> str:
        return self.email

    def set_email(self, email: str):
        self.email = email

    def get_telefono(self) -> str:
        return self.telefono

    def set_telefono(self, telefono: str):
        self.telefono = telefono

    def get_mensaje(self) -> str:
        return self.mensaje

    def set_mensaje(self, mensaje: str):
        self.mensaje = mensaje

    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.nombre = data.get("nombre")
        self.email = data.get("email")
        self.telefono = data.get("telefono")
        self.mensaje = data.get("mensaje")

    def contacto_to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "mensaje": self.mensaje
        }
