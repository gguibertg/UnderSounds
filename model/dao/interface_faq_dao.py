from abc import ABC, abstractmethod

class InterfaceFaqDAO(ABC):
    """
    Interfaz abstracta para acceder y manipular FAQs en la base de datos.

    Esta interfaz define las operaciones CRUD que deben implementar todas
    las clases DAO concretas que trabajen con FAQs.
    """

    @abstractmethod
    def get_faqs(self):
        """
        Recupera todas las FAQs almacenadas.
        """
        pass

    @abstractmethod
    def get_faq_by_id(self, faq_id):
        """
        Recupera una FAQ a partir de su ID.

        Args:
            faq_id: Identificador de la FAQ a buscar.
        """
        pass

    @abstractmethod
    def insert_faq(self, faq):
        """
        Inserta una nueva FAQ en la base de datos.

        Args:
            faq: Objeto FaqDTO o diccionario con los datos de la FAQ.
        """
        pass

    @abstractmethod
    def update_faq(self, faq_id, updated_faq):
        """
        Actualiza los datos de una FAQ existente.

        Args:
            faq_id: Identificador de la FAQ a actualizar.
            updated_faq: Objeto o datos nuevos de la FAQ.
        """
        pass

    @abstractmethod
    def delete_faq(self, faq_id):
        """
        Elimina una FAQ de la base de datos.

        Args:
            faq_id: Identificador de la FAQ a eliminar.
        """
        pass
