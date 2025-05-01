from datetime import datetime

class SesionDTO():
    def __init__(self):   
        self.id: str = None
        self.name: str = None
        self.user_id: str = None
        self.type: str = None
        self.caducidad: datetime = None

    def get_id(self) -> str:
        return self.id

    def set_id(self, id: str):
        self.id = id

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_user_id(self) -> str:
        return self.user_id

    def set_user_id(self, user_id: str):
        self.user_id = user_id

    def get_type(self) -> str:
        return self.type

    def set_type(self, type: str):
        self.type = type

    def get_caducidad(self) -> datetime:
        return self.caducidad

    def set_caducidad(self, caducidad: datetime):
        self.caducidad = caducidad

    def load_from_dict(self, data: dict):
        self.id = data.get("id")
        self.name = data.get("name")
        self.user_id = data.get("user_id")
        self.type = data.get("type")
        self.caducidad = data.get("caducidad")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "type": self.type,
            "caducidad": self.caducidad
        }
