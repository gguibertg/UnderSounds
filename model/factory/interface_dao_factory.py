# # Crea los diferentes DAO para el acceso a la información
# """
# InterfaceDAOFactory es una clase abstracta que define la interfaz para las fábricas de DAO (Data Access Object).
# Utiliza el módulo `abc` (Abstract Base Classes) para garantizar que las subclases implementen los métodos definidos.
# Métodos:
# ---------
# - getSongDao():
#     Método abstracto que debe ser implementado por las clases DAOFactory para proporcionar una instancia del DAO de canciones.
# """

from abc import abstractmethod, ABC

class InterfaceDAOFactory(ABC):

    @abstractmethod
    def getSongDao(self):
        pass

    # Seguir añadiendo métodos abstractos para los diferentes DAOs que se necesiten...