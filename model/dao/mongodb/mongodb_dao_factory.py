from ...factory.interface_dao_factory import InterfaceDAOFactory
from .collection.mongodb_faq_dao import MongodbFaqDAO


class MongodbDAOFactory(InterfaceDAOFactory):
    """
    Fábrica de DAOs que utiliza MongoDB como sistema de persistencia.

    Esta clase implementa la interfaz InterfaceDAOFactory y proporciona instancias
    de DAOs que se conectan a MongoDB, permitiendo el acceso estructurado a los datos.
    """

    def __init__(self):
        """
        Constructor de la fábrica. No requiere inicialización explícita
        ya que los DAOs gestionan internamente sus propias conexiones.
        """
        pass

    def createFaqDAO(self):
        """
        Devuelve una instancia funcional del DAO de FAQs.

        Returns:
            MongodbFaqDAO: DAO configurado para trabajar con la colección 'faqs'.
        """
        return MongodbFaqDAO()

    def getSongDao(self):
        """
        Método de marcador requerido por la interfaz.

        Returns:
            None
        """
        return None
