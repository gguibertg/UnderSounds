"""
Implementación de InterfaceFaqDAO usando MongoDB con pymongo.
"""

from bson import ObjectId
from model.dao.interface_faq_dao import InterfaceFaqDAO
from model.dto.faq_dto import FaqDTO


class MongodbFaqDAO(InterfaceFaqDAO):
    """
    DAO para la colección 'faqs' de MongoDB.
    Implementa operaciones CRUD básicas.
    """

    def __init__(self, db):
        """
        Inicializa el DAO con la colección de FAQs.

        :param db: Objeto pymongo.database.Database
        """
        self.collection = db["faqs"]

    def get_all_faqs(self):
        """
        Recupera todas las FAQs de la colección.

        :return: Lista de objetos FaqDTO
        """
        faqs = []
        for doc in self.collection.find():
            faq = FaqDTO()
            faq.set_id(str(doc["_id"]))
            faq.set_question(doc.get("question"))
            faq.set_answer(doc.get("answer"))
            faqs.append(faq)
        return faqs

    def get_faq_by_id(self, faq_id: str) -> FaqDTO:
        """
        Recupera una FAQ por ID.

        :param faq_id: ID de la FAQ
        :return: Objeto FaqDTO o None si no se encuentra
        """
        doc = self.collection.find_one({"_id": ObjectId(faq_id)})
        if doc:
            faq = FaqDTO()
            faq.set_id(str(doc["_id"]))
            faq.set_question(doc.get("question"))
            faq.set_answer(doc.get("answer"))
            return faq
        return None

    def insert_faq(self, faq: FaqDTO) -> str:
        """
        Inserta una nueva FAQ.

        :param faq: Objeto FaqDTO
        :return: ID generado
        """
        result = self.collection.insert_one(faq.faq_to_dict())
        return str(result.inserted_id)

    def update_faq(self, faq_id: str, faq: FaqDTO) -> bool:
        """
        Actualiza una FAQ por su ID.

        :param faq_id: ID del documento
        :param faq: Datos nuevos
        :return: True si se modificó, False si no
        """
        result = self.collection.update_one(
            {"_id": ObjectId(faq_id)},
            {"$set": faq.faq_to_dict()}
        )
        return result.modified_count > 0

    def delete_faq(self, faq_id: str) -> bool:
        """
        Elimina una FAQ por ID.

        :param faq_id: ID del documento
        :return: True si se eliminó, False si no
        """
        result = self.collection.delete_one({"_id": ObjectId(faq_id)})
        return result.deleted_count > 0
