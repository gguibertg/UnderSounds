from abc import ABC, abstractmethod
from typing import List, Optional

# La clase InterfaceSongDAO es una interfaz abstracta que define el contrato para los DAOs de canciones.
class InterfaceUsuarioDAO(ABC):

    # Aquí debemos ir añadiendo los métodos abstractos que se van a usar en la clase DAO.
    @abstractmethod
    def getUsuario(self, email):
        pass
    
    @abstractmethod
    def getAllUsuarios(self):
        pass