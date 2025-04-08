from abc import ABC, abstractmethod
from typing import List, Optional

# La clase InterfaceSongDAO es una interfaz abstracta que define el contrato para los DAOs de canciones.
class InterfaceSongDAO(ABC):

    # Aquí debemos ir añadiendo los métodos abstractos que se van a usar en la clase DAO.
    @abstractmethod
    def get_songs(self):
        pass