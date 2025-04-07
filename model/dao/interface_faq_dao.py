"""
Interfaz DAO para acceder a las preguntas frecuentes (FAQs).
Define los métodos CRUD que cualquier implementación debe cumplir.
"""

from abc import ABC, abstractmethod
from typing import List
from model.dto.faq_dto import FaqDTO


class InterfaceFaqDAO(ABC):
    """
    Interfaz abstracta para operaciones CRUD sobre FAQs.
    """

    @abstractmethod
    def get_all_faqs(self) -> List[FaqDTO]:
        """
        Recupera todas las FAQs.

        :return: Lista de objetos FaqDTO
        """
        pass

    @abstractmethod
    def get_faq_by_id(self, faq_id: str) -> FaqDTO:
        """
        Recupera una FAQ específica por su ID.

        :param faq_id: ID de la FAQ
        :return: Objeto FaqDTO o None si no se encuentra
        """
        pass

    @abstractmethod
    def insert_faq(self, faq: FaqDTO) -> str:
        """
        Inserta una nueva FAQ.

        :param faq: Objeto FaqDTO
        :return: ID generado de la nueva FAQ
        """
        pass

    @abstractmethod
    def update_faq(self, faq_id: str, faq: FaqDTO) -> bool:
        """
        Actualiza una FAQ existente.

        :param faq_id: ID de la FAQ
        :param faq: Objeto FaqDTO con los nuevos datos
        :return: True si se actualizó, False si no se encontró
        """
        pass

    @abstractmethod
    def delete_faq(self, faq_id: str) -> bool:
        """
        Elimina una FAQ por su ID.

        :param faq_id: ID de la FAQ
        :return: True si se eliminó, False si no se encontró
        """
        pass
