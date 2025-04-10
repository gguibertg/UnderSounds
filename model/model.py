from .dao.mongodb.mongodb_dao_factory import MongodbDAOFactory

class Model:
    """
    Clase principal del modelo. Gestiona el acceso a datos a través de la DAO Factory.
    Esta clase actúa como fachada del modelo, centralizando llamadas a los DAOs concretos.
    """

    def __init__(self):
        """
        Constructor que inicializa la fábrica de DAOs y recupera instancias de los DAOs necesarios.
        """
        self.factory = MongodbDAOFactory()
        self.faqDAO = self.factory.get_faq_dao()
        self.userDAO = None
        self.songDAO = None
        self.cartDAO = None
        self.reviewDAO = None

    def get_faqs(self):
        """
        Devuelve todas las FAQs almacenadas.

        Returns:
            str: FAQs en formato JSON.
        """
        return self.faqDAO.get_faqs()

    def get_faq_by_id(self, faq_id):
        """
        Recupera una FAQ específica por su ID.

        Args:
            faq_id: Identificador de la FAQ.

        Returns:
            dict or None: Diccionario con la FAQ o None si no existe.
        """
        return self.faqDAO.get_faq_by_id(faq_id)

    def insert_faq(self, faq_dto):
        """
        Inserta una nueva FAQ en la base de datos.

        Args:
            faq_dto: Objeto FaqDTO con los datos de la FAQ.
        """
        self.faqDAO.insert_faq(faq_dto)

    def update_faq(self, faq_id, updated_faq_dto):
        """
        Actualiza una FAQ existente por su ID.

        Args:
            faq_id: ID de la FAQ a actualizar.
            updated_faq_dto: Objeto FaqDTO con los nuevos datos.

        Returns:
            bool: True si se actualizó, False en caso contrario.
        """
        return self.faqDAO.update_faq(faq_id, updated_faq_dto)

    def delete_faq(self, faq_id):
        """
        Elimina una FAQ de la base de datos por su ID.

        Args:
            faq_id: ID de la FAQ a eliminar.

        Returns:
            bool: True si se eliminó, False en caso contrario.
        """
        return self.faqDAO.delete_faq(faq_id)
